import json
import sys
import tempfile
import unittest
import zipfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))
from zeropkg import PackageError, create_package, verify_package


class ZeroPkgTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.source = self.root / "source"
        (self.source / "usr" / "bin").mkdir(parents=True)
        (self.source / "usr" / "bin" / "hello").write_text("#!/bin/sh\necho hello\n")
        self.package = self.root / "hello-1.0.0.zpkg"

    def tearDown(self):
        self.temp.cleanup()

    def build(self):
        create_package(
            self.source, self.package, "hello", "1.0.0", "x86_64",
            "Test utility", "MIT", [],
        )

    def test_create_and_verify_package(self):
        self.build()
        metadata, manifest = verify_package(self.package)
        self.assertEqual(metadata["name"], "hello")
        self.assertEqual(metadata["version"], "1.0.0")
        self.assertEqual(manifest[0]["path"], "usr/bin/hello")

    def test_payload_tampering_is_detected(self):
        self.build()
        tampered = self.root / "tampered.zpkg"
        with zipfile.ZipFile(self.package) as original:
            entries = {name: original.read(name) for name in original.namelist()}
        entries["payload/usr/bin/hello"] += b"# changed\n"
        with zipfile.ZipFile(tampered, "w", compression=zipfile.ZIP_DEFLATED) as archive:
            for name, data in entries.items():
                archive.writestr(name, data)
        with self.assertRaises(PackageError):
            verify_package(tampered)

    def test_symlink_source_is_rejected(self):
        link = self.source / "linked-file"
        link.symlink_to(self.source / "usr" / "bin" / "hello")
        with self.assertRaises(PackageError):
            self.build()

    def test_path_traversal_in_manifest_is_rejected(self):
        self.build()
        malicious = self.root / "malicious.zpkg"
        with zipfile.ZipFile(self.package) as original:
            entries = {name: original.read(name) for name in original.namelist()}
        manifest = json.loads(entries["manifest.json"])
        manifest[0]["path"] = "../outside"
        entries["manifest.json"] = json.dumps(manifest).encode()
        with zipfile.ZipFile(malicious, "w") as archive:
            for name, data in entries.items():
                archive.writestr(name, data)
        with self.assertRaises(PackageError):
            verify_package(malicious)


if __name__ == "__main__":
    unittest.main()
