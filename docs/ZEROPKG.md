# ZeroPKG Package Manager

**Status:** Host-side package creation and verification prototype implemented. Native installation is not implemented.

ZeroPKG is the planned native package manager for Zero Kernel. The first implementation is a host-side Python utility used to create, inspect, and verify .zpkg archives while the operating system's filesystem and process services are still under development.

## Current host-side commands

Run the utility from the repository root:

```bash
python3 tools/zeropkg.py --help
```

Create a package from a directory tree:

```bash
python3 tools/zeropkg.py create \
  --name hello \
  --version 1.0.0 \
  --source examples/hello-package \
  --output build/hello-1.0.0.zpkg \
  --architecture x86_64 \
  --description "Example Zero Kernel utility" \
  --license MIT
```

Inspect package metadata and verify its contents:

```bash
python3 tools/zeropkg.py inspect build/hello-1.0.0.zpkg
python3 tools/zeropkg.py verify build/hello-1.0.0.zpkg
```

Dependencies can be declared by repeating --depends:

```bash
python3 tools/zeropkg.py create \
  --name demo-app --version 1.0.0 \
  --source examples/demo-app \
  --output build/demo-app-1.0.0.zpkg \
  --depends runtime-lib --depends base-utils
```

## Package format v1

A .zpkg file is a ZIP archive with the following entries:

```text
example-1.0.0.zpkg
├── metadata.json
├── manifest.json
└── payload/
    └── usr/
        └── bin/
            └── example
```

metadata.json records the format version, package name, version, architecture (x86_64 or any), description, dependencies, and license.

manifest.json records each payload file's normalized relative path, byte size, SHA-256 digest, and intended permission bits.

## Verification and safety behavior

The prototype currently:

- Rejects symbolic links and non-regular source files when creating packages.
- Rejects absolute paths, parent-directory traversal, backslashes, and non-normalized paths.
- Rejects duplicate archive and manifest entries.
- Rejects symlink entries, encrypted entries, and unsupported compression methods.
- Enforces file-count, per-file, and total uncompressed size limits.
- Checks that archive payload paths match the manifest.
- Verifies every payload file's size and SHA-256 digest.
- Does not extract archives or execute package scripts.

The SHA-256 manifest detects payload changes only when the manifest itself is trusted. It does **not** authenticate the publisher. Signed package metadata and trusted repository keys are future requirements before packages can be accepted from remote sources.

## Tests

Run the unit tests:

```bash
python3 -m unittest discover -s tests -v
```

The tests cover package creation, checksum tampering, symbolic-link rejection, and path-traversal rejection.

## Not implemented yet

The current utility does not install or remove software, resolve dependencies, maintain an installed-package database, download packages, verify digital signatures, or interact with the running Zero Kernel. It is a host-side format prototype only.

Native installation must wait until Zero Kernel has persistent storage, a VFS, safe file operations, an ELF64 loader, user-mode execution, process management, and a system-call interface.

## Planned milestones

1. Finalize the metadata and archive specification.
2. Expand tests for malformed archives, limits, permissions, and duplicate paths.
3. Add package database and dependency-resolution design.
4. Implement offline installation into a disposable test root filesystem.
5. Add transactional install/remove and file ownership tracking.
6. Add signed repository metadata and a trusted-key model.
7. Add remote repository support after networking and TLS exist.

ZeroPKG is independent of Linux package managers; familiar command names are interface inspiration only.
