#!/usr/bin/env python3
"""Host-side builder and verifier for the ZeroPKG v1 package format.

This tool creates and validates package archives. It deliberately does not
install packages into the host or into the running Zero Kernel.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import stat
import sys
import zipfile
from pathlib import Path, PurePosixPath
from typing import Any

FORMAT_VERSION = 1
MAX_FILES = 10_000
MAX_FILE_SIZE = 128 * 1024 * 1024
MAX_PACKAGE_SIZE = 512 * 1024 * 1024
RESERVED = {"metadata.json", "manifest.json"}
NAME_RE = re.compile(r"^[a-z0-9][a-z0-9+._-]{0,63}$")
VERSION_RE = re.compile(r"^[0-9A-Za-z][0-9A-Za-z.+_-]{0,63}$")


class PackageError(Exception):
    """Raised when a package is malformed or unsafe."""


def safe_relative_path(value: str) -> str:
    if not value or "\\" in value or "\x00" in value:
        raise PackageError(f"Invalid package path: {value!r}")
    path = PurePosixPath(value)
    if path.is_absolute() or any(part in ("", ".", "..") for part in path.parts):
        raise PackageError(f"Unsafe package path: {value!r}")
    if ":" in path.parts[0]:
        raise PackageError(f"Drive-qualified package path is not allowed: {value!r}")
    normalized = path.as_posix()
    if normalized != value:
        raise PackageError(f"Non-normalized package path: {value!r}")
    return normalized


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def create_package(source: Path, output: Path, name: str, version: str,
                   architecture: str, description: str, license_name: str,
                   dependencies: list[str]) -> None:
    if not NAME_RE.fullmatch(name):
        raise PackageError("Package name must use lowercase letters, digits, '+', '.', '_' or '-'.")
    if not VERSION_RE.fullmatch(version):
        raise PackageError("Version contains unsupported characters.")
    if not source.is_dir():
        raise PackageError(f"Source directory does not exist: {source}")
    if architecture not in {"x86_64", "any"}:
        raise PackageError("Supported architectures are: x86_64, any.")
    for dependency in dependencies:
        if not NAME_RE.fullmatch(dependency):
            raise PackageError(f"Invalid dependency name: {dependency}")

    files: list[tuple[str, Path]] = []
    total_size = 0
    for item in sorted(source.rglob("*")):
        if item.is_symlink():
            raise PackageError(f"Symbolic links are not supported: {item}")
        if item.is_dir():
            continue
        if not item.is_file():
            raise PackageError(f"Only regular files can be packaged: {item}")
        relative = safe_relative_path(item.relative_to(source).as_posix())
        if relative in RESERVED:
            raise PackageError(f"Source uses reserved package path: {relative}")
        size = item.stat().st_size
        if size > MAX_FILE_SIZE:
            raise PackageError(f"File exceeds size limit ({MAX_FILE_SIZE} bytes): {item}")
        total_size += size
        files.append((relative, item))

    if not files:
        raise PackageError("Cannot create an empty package.")
    if len(files) > MAX_FILES or total_size > MAX_PACKAGE_SIZE:
        raise PackageError("Package exceeds the configured file-count or total-size limit.")

    manifest: list[dict[str, Any]] = []
    for relative, item in files:
        mode = stat.S_IMODE(item.stat().st_mode) & 0o755
        if mode == 0:
            mode = 0o644
        manifest.append({
            "path": relative,
            "size": item.stat().st_size,
            "sha256": sha256_file(item),
            "mode": mode,
        })

    metadata = {
        "format_version": FORMAT_VERSION,
        "name": name,
        "version": version,
        "architecture": architecture,
        "description": description,
        "dependencies": sorted(set(dependencies)),
        "license": license_name,
    }

    output.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(output, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        archive.writestr("metadata.json", json.dumps(metadata, indent=2, sort_keys=True) + "\n")
        archive.writestr("manifest.json", json.dumps(manifest, indent=2, sort_keys=True) + "\n")
        for relative, item in files:
            archive.write(item, f"payload/{relative}")


def read_json_member(archive: zipfile.ZipFile, name: str) -> Any:
    try:
        return json.loads(archive.read(name).decode("utf-8"))
    except (KeyError, UnicodeDecodeError, json.JSONDecodeError, zipfile.BadZipFile) as exc:
        raise PackageError(f"Missing or invalid {name}: {exc}") from exc


def verify_package(package: Path) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    if not package.is_file():
        raise PackageError(f"Package does not exist: {package}")
    if package.stat().st_size > MAX_PACKAGE_SIZE:
        raise PackageError("Compressed package exceeds size limit.")

    try:
        with zipfile.ZipFile(package, "r") as archive:
            infos = archive.infolist()
            names = [entry.filename for entry in infos]
            if len(names) != len(set(names)):
                raise PackageError("Archive contains duplicate paths.")
            if len(infos) > MAX_FILES + len(RESERVED):
                raise PackageError("Archive contains too many entries.")
            if any(info.flag_bits & 0x1 for info in infos):
                raise PackageError("Encrypted archive entries are not supported.")

            total_uncompressed = 0
            for info in infos:
                if info.is_dir():
                    continue
                safe_relative_path(info.filename)
                if info.compress_type not in (zipfile.ZIP_STORED, zipfile.ZIP_DEFLATED):
                    raise PackageError(f"Unsupported compression method: {info.filename}")
                unix_mode = (info.external_attr >> 16) & 0xFFFF
                if stat.S_ISLNK(unix_mode):
                    raise PackageError(f"Symbolic link entry is not allowed: {info.filename}")
                if info.file_size > MAX_FILE_SIZE:
                    raise PackageError(f"Entry exceeds size limit: {info.filename}")
                total_uncompressed += info.file_size
            if total_uncompressed > MAX_PACKAGE_SIZE:
                raise PackageError("Uncompressed package exceeds size limit.")

            metadata = read_json_member(archive, "metadata.json")
            manifest = read_json_member(archive, "manifest.json")
            if not isinstance(metadata, dict) or metadata.get("format_version") != FORMAT_VERSION:
                raise PackageError("Unsupported or invalid package metadata format.")
            for field in ("name", "version", "architecture", "description", "license"):
                if not isinstance(metadata.get(field), str):
                    raise PackageError(f"Metadata field {field!r} must be a string.")
            if not NAME_RE.fullmatch(metadata["name"]) or not VERSION_RE.fullmatch(metadata["version"]):
                raise PackageError("Invalid package name or version.")
            if metadata["architecture"] not in {"x86_64", "any"}:
                raise PackageError("Unsupported package architecture.")
            if not isinstance(metadata.get("dependencies"), list) or not all(
                isinstance(dep, str) and NAME_RE.fullmatch(dep) for dep in metadata["dependencies"]
            ):
                raise PackageError("Invalid dependencies list.")
            if not isinstance(manifest, list) or not manifest:
                raise PackageError("Manifest must be a non-empty list.")

            seen: set[str] = set()
            expected_payload: set[str] = set()
            for entry in manifest:
                if not isinstance(entry, dict):
                    raise PackageError("Manifest entries must be objects.")
                relative = safe_relative_path(entry.get("path", ""))
                if relative in seen:
                    raise PackageError(f"Duplicate manifest path: {relative}")
                seen.add(relative)
                expected_payload.add(f"payload/{relative}")
                if not isinstance(entry.get("size"), int) or entry["size"] < 0:
                    raise PackageError(f"Invalid size for {relative}")
                if not isinstance(entry.get("sha256"), str) or not re.fullmatch(
                    r"[0-9a-f]{64}", entry["sha256"]
                ):
                    raise PackageError(f"Invalid SHA-256 value for {relative}")
                if not isinstance(entry.get("mode"), int) or entry["mode"] & ~0o755:
                    raise PackageError(f"Invalid file mode for {relative}")

                member = f"payload/{relative}"
                try:
                    data = archive.read(member)
                except KeyError as exc:
                    raise PackageError(f"Missing payload file: {relative}") from exc
                if len(data) != entry["size"]:
                    raise PackageError(f"Size mismatch: {relative}")
                if hashlib.sha256(data).hexdigest() != entry["sha256"]:
                    raise PackageError(f"SHA-256 mismatch: {relative}")

            actual_payload = {
                name for name in names
                if name.startswith("payload/") and not name.endswith("/")
            }
            if actual_payload != expected_payload:
                raise PackageError("Payload entries do not match the manifest.")
            if not RESERVED.issubset(set(names)):
                raise PackageError("Package is missing required metadata or manifest.")
            allowed = RESERVED | expected_payload
            if set(names) != allowed:
                raise PackageError("Archive contains unexpected entries.")
            return metadata, manifest
    except zipfile.BadZipFile as exc:
        raise PackageError(f"Not a valid .zpkg archive: {exc}") from exc


def command_create(args: argparse.Namespace) -> int:
    create_package(Path(args.source), Path(args.output), args.name, args.version,
                   args.architecture, args.description, args.license, args.depends)
    print(f"Created package: {args.output}")
    return 0


def command_inspect(args: argparse.Namespace) -> int:
    metadata, manifest = verify_package(Path(args.package))
    print(json.dumps({"metadata": metadata, "files": manifest}, indent=2))
    return 0


def command_verify(args: argparse.Namespace) -> int:
    metadata, manifest = verify_package(Path(args.package))
    print(f"OK: {metadata['name']} {metadata['version']} ({metadata['architecture']})")
    print(f"Verified {len(manifest)} file(s).")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="zeropkg", description="ZeroPKG host-side package utility")
    subparsers = parser.add_subparsers(dest="command", required=True)

    create = subparsers.add_parser("create", help="Create a .zpkg archive from a directory")
    create.add_argument("--name", required=True)
    create.add_argument("--version", required=True)
    create.add_argument("--source", required=True, help="Directory containing package payload files")
    create.add_argument("--output", required=True, help="Output .zpkg path")
    create.add_argument("--architecture", default="x86_64", choices=("x86_64", "any"))
    create.add_argument("--description", default="")
    create.add_argument("--license", default="NOASSERTION")
    create.add_argument("--depends", action="append", default=[], help="Dependency package name; repeatable")
    create.set_defaults(func=command_create)

    inspect = subparsers.add_parser("inspect", help="Verify and display package metadata")
    inspect.add_argument("package")
    inspect.set_defaults(func=command_inspect)

    verify = subparsers.add_parser("verify", help="Verify package structure and payload checksums")
    verify.add_argument("package")
    verify.set_defaults(func=command_verify)
    return parser


def main() -> int:
    args = build_parser().parse_args()
    try:
        return args.func(args)
    except (PackageError, OSError) as exc:
        print(f"zeropkg: error: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
