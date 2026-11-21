# ZeroPKG Package Manager Design

**Status:** Proposed architecture — not yet implemented.

ZeroPKG is the planned native package manager for Zero Kernel. It will manage software packages after the operating system has the filesystem, executable loader, process model, and required system services.

## Goals

- Install, remove, inspect, and list packages.
- Track package versions and file ownership.
- Resolve declared dependencies.
- Verify package integrity and repository metadata.
- Keep installation and removal predictable and auditable.

## Planned commands

| Command | Purpose |
|---|---|
| `zeropkg update` | Refresh repository metadata |
| `zeropkg upgrade` | Upgrade installed packages |
| `zeropkg install <name>` | Install a package |
| `zeropkg remove <name>` | Remove a package |
| `zeropkg search <term>` | Search repository metadata |
| `zeropkg list` | List installed packages |
| `zeropkg info <name>` | Display package metadata |
| `zeropkg verify` | Verify installed package files |

These commands describe the intended interface; they are not available in the current kernel.

## Proposed .zpkg package format

The first format may be a versioned archive containing:

```text
example-1.0.0.zpkg
├── metadata.json
├── manifest.txt
└── payload/
    └── usr/
        └── bin/
            └── example
```

Example metadata:

```json
{
  "format_version": 1,
  "name": "example",
  "version": "1.0.0",
  "architecture": "x86_64",
  "description": "Example Zero Kernel utility",
  "dependencies": [],
  "license": "MIT"
}
```

The package format must define archive limits, path normalization, file permissions, checksums, and signature handling before installation is implemented.

## Repository and trust model

Repository metadata and packages must be authenticated. The design should include:

- Signed repository metadata.
- Package hashes checked before installation.
- A documented trusted-key mechanism.
- Version and architecture checks.
- Clear failure behavior when signatures or hashes do not match.
- No automatic execution of arbitrary package install scripts.

Packages should install files only beneath approved system directories. Path traversal, absolute-path injection, symlink escape, and archive extraction attacks must be prevented.

## Installed package database

The planned database location is:

```text
/var/lib/zeropkg/
├── installed/
│   └── example.json
└── status.db
```

The package database should record package name, version, architecture, installed file manifest, checksums, and dependencies.

## Required kernel capabilities

ZeroPKG should not be treated as a working installer until these capabilities exist:

1. Persistent filesystem and VFS.
2. Storage driver and reliable file writes.
3. ELF64 executable loader.
4. User-mode execution and process management.
5. System-call interface for file and process operations.
6. Networking and TLS support for remote repositories, or a safe offline package import path.
7. Package verification and installation transaction logic.

## Development milestones

1. Finalize and document the package metadata schema.
2. Build a host-side `.zpkg` creation and inspection tool.
3. Implement package manifest and checksum verification.
4. Implement local/offline package installation to a test root filesystem.
5. Add installed-package database and removal logic.
6. Add dependency resolution.
7. Add signed repository metadata.
8. Add network repository support after networking and TLS are available.

## Scope

ZeroPKG is intended to be independent of Linux package managers. Familiar command names are user-interface inspiration only; ZeroPKG will use its own package format, metadata, repository format, and installation implementation.
