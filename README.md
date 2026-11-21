# Zero Kernel

Zero Kernel is an experimental, standalone x86 operating-system project developed in C and Assembly. The goal is to build the kernel and its supporting operating-system components from the ground up, beginning with a bootable kernel and growing toward a filesystem, shell, and native software package manager.

**Target architecture:** x86_64  
**Bootloader:** GRUB / Multiboot2 (planned development path)  
**Languages:** C and x86 Assembly  
**Development/testing:** QEMU  
**Status:** Educational project under active development

> **Project status:** This README distinguishes existing project features from proposed work. Items in the roadmap and design documents are not claims that those features are already implemented.

---

## Current project features

The repository's initial implementation documents the following capabilities:

- VGA text-mode terminal output
- PS/2 keyboard input
- Interactive command shell
- In-memory, RAM-based text storage
- Built-in `help`, `about`, `clear`, `echo`, `write`, `read`, and `version` commands
- QEMU/ACPI shutdown support
- Basic installation simulation
- Direct hardware I/O using inline assembly

The current RAM-based storage is temporary: its contents do not persist after the virtual machine shuts down. It is not yet a disk-backed filesystem.

## Project direction

Zero Kernel is intended to become an independent operating system, not a Linux distribution or a modified Linux kernel. Linux-like command names and directory conventions may be familiar to users, but kernel services, filesystem code, executable support, and package management will be developed as Zero Kernel components.

## Planned architecture

```text
                  Zero Shell / Applications
                            |
                            v
                    Virtual Filesystem
                       /         \
                      v           v
                   ZeroFS       ext2*
                      \           /
                       v         v
                    Block-device layer
                            |
                       Storage driver

                  ZeroPKG (future)
                         |
                 Package repositories
```

`* ext2 compatibility is a future goal, after native ZeroFS functionality is established.`

## Filesystem: ZeroFS

ZeroFS is the proposed native filesystem for Zero Kernel. The planned design includes:

- A versioned superblock
- Block allocation bitmap
- Inode table and directory entries
- File data blocks
- A Virtual Filesystem (VFS) interface
- A host-side utility for creating and inspecting disk images

The intended root filesystem layout follows familiar Unix conventions:

```text
/
├── bin/
├── boot/
├── dev/
├── etc/
├── home/
├── lib/
├── opt/
├── root/
├── tmp/
├── usr/
└── var/
```

The first storage target is a disposable QEMU virtual disk. ext2 compatibility may be added later. ext4 is outside the initial implementation scope.

See [Filesystem Design](docs/FILESYSTEM.md) for the proposed on-disk structures, VFS responsibilities, and implementation milestones.

## Software installation: ZeroPKG

ZeroPKG is the proposed native package manager. Its intended command interface is:

| Command | Purpose |
|---|---|
| `zeropkg update` | Refresh repository metadata |
| `zeropkg upgrade` | Upgrade installed packages |
| `zeropkg install <name>` | Install a package |
| `zeropkg remove <name>` | Remove a package |
| `zeropkg search <term>` | Search packages |
| `zeropkg list` | List installed packages |
| `zeropkg info <name>` | Show package information |

These commands are a design target, not currently working shell commands. The proposed `.zpkg` format will include package metadata, a file manifest, and payload files. Package integrity and repository authenticity checks are required before installation is enabled.

A full package manager depends on persistent storage, a VFS, an ELF64 loader, user-mode execution, process management, and system calls. Remote repositories will additionally require networking and TLS.

See [ZeroPKG Design](docs/ZEROPKG.md) for the proposed package format, trust model, and implementation milestones.

## Planned shell commands

The shell is expected to grow toward familiar filesystem utilities:

- `help`, `clear`, `echo`, `about`, `version`
- `ls`, `cd`, `pwd`
- `mkdir`, `touch`, `cat`
- `cp`, `mv`, `rm`
- `zeropkg` package-management commands

Filesystem and package commands will become available only after their underlying kernel services are implemented.

## Development roadmap

1. Stabilize the boot process and kernel entry.
2. Establish x86_64 long mode and CPU tables.
3. Implement interrupts, exceptions, and memory management.
4. Build terminal and keyboard input services.
5. Design and implement the VFS and native ZeroFS.
6. Add a block-device abstraction and QEMU storage driver.
7. Connect filesystem operations to the shell.
8. Implement an ELF64 loader, user mode, processes, and system calls.
9. Build ZeroPKG and local package installation.
10. Add package repositories, signature verification, and network support.
11. Evaluate ext2 compatibility and additional device drivers.

## Development principles

- Build and test in QEMU before experimenting with physical hardware.
- Keep kernel code freestanding and independent of a host operating system at runtime.
- Separate bootstrapping, kernel services, drivers, filesystem code, and user applications.
- Test filesystem code against disposable virtual disk images.
- Verify package metadata, hashes, and signatures before installing software.
- Document which features are implemented, experimental, or planned.

## Requirements

The intended development toolchain includes:

- GCC or an x86_64 cross-compiler
- NASM
- GNU binutils and linker
- GNU Make
- GRUB utilities and `grub-mkrescue`
- xorriso
- QEMU system emulator
- GDB (for debugging)

Exact build dependencies and commands will be maintained as the build system is finalized.

## Educational use

Zero Kernel is an experimental learning project for exploring:

- Operating-system architecture
- x86_64 assembly and C
- Bootloaders and CPU initialization
- Memory management
- Hardware drivers
- Filesystem design
- Executable formats and process management
- Package management

It is not intended for production use.

## License

MIT License

---

Built by **ZeroScope Intelligence** with C, Assembly, and curiosity.
