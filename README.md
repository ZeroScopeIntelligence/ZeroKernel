# Zero Kernel

Zero Kernel is an experimental, standalone operating-system kernel project developed in C and x86 Assembly under **ZeroScope Intelligence**. The project is being built from the ground up, beginning with a bootable x86_64 kernel and progressing toward memory management, hardware drivers, a filesystem, shell, and native package manager.

**Target architecture:** x86_64  
**Bootloader:** GRUB / Multiboot2  
**Languages:** C and x86 Assembly (NASM)  
**Build environment:** Debian Trixie container and x86_64-elf cross-compiler  
**Emulator:** QEMU  
**Current milestone:** First successful x86_64 QEMU boot

> **Project status:** The x86_64 bootstrap described below has been built, validated as Multiboot2, and successfully booted in QEMU. Roadmap items and design documents are proposals unless explicitly marked implemented.

---

## Current milestone: x86_64 bootstrap

The new bootstrap provides the first working foundation for the x86_64 kernel:

- GRUB Multiboot2 header and boot configuration.
- Assembly entry point and initial page-table setup.
- Transition from the 32-bit bootloader environment into x86_64 long mode.
- Initial GDT and 16 KiB bootstrap stack.
- Freestanding C kernel entry point.
- VGA text-mode output at `0xB8000`.
- QEMU bootable ISO generation.

The first successful boot displayed the Zero Kernel title, architecture and language information, and kernel initialization messages.

### Boot screen

The initial kernel screen confirms that execution reached `kernel_main()` and wrote text to VGA memory. It is an early boot milestone, not a complete operating system.

## Repository layout

```text
.
├── boot/
│   └── grub/
│       └── grub.cfg
├── docker/
│   └── Dockerfile
├── docs/
│   ├── BOOTSTRAP.md
│   ├── FILESYSTEM.md
│   └── ZEROPKG.md
├── examples/
│   └── hello-package/
├── tests/
│   └── test_zeropkg.py
├── tools/
│   └── zeropkg.py
├── kernel/
│   ├── arch/
│   │   └── x86_64/
│   │       └── boot.asm
│   ├── core/
│   │   └── kernel.c
│   ├── boot.asm
│   ├── kernel.c
│   ├── linker.ld
│   └── Makefile
├── linker.ld
└── Makefile
```

The root-level Makefile builds the new x86_64 bootstrap from `kernel/arch/x86_64/boot.asm` and `kernel/core/kernel.c`. Earlier prototype files are retained under `kernel/` and are not part of this new build target.

## Build and run

The recommended build environment is the included Debian Trixie Docker image. See [Bootstrap Build Guide](docs/BOOTSTRAP.md) for the full cross-compiler setup and build instructions.

Build the container from the repository root:

```bash
docker build -t zerokernel-builder -f docker/Dockerfile .
```

Start the container with the repository mounted:

```bash
docker run --rm -it -v "$PWD:/workspace" zerokernel-builder
```

After building and installing the `x86_64-elf` cross-compiler into `.toolchain`, run these commands from the repository root:

```bash
make
make check
make iso
```

Boot the ISO in QEMU:

```bash
make run
```

For terminal-only environments with QEMU's curses display backend:

```bash
qemu-system-x86_64 \
    -cdrom build/zerokernel.iso \
    -m 256M \
    -display curses \
    -monitor none
```

The build output is stored in `build/`; the local cross-compiler is stored in `.toolchain/`. Both are excluded from Git.

## Current limitations

- Initial page tables map only the first 2 MiB of physical memory.
- VGA text output is implemented; serial logging is not yet implemented.
- IDT, exception handling, and hardware interrupt handling are not yet implemented.
- Physical and virtual memory managers are not yet implemented.
- Keyboard and storage drivers are future work for the new x86_64 bootstrap.
- The Multiboot2 information structure is passed to the C entry point but is not yet parsed.
- The older prototype source is retained for reference and is separate from the new root-level build.

## Earlier prototype

The repository retains an earlier kernel prototype under `kernel/kernel.c`, `kernel/boot.asm`, `kernel/linker.ld`, and `kernel/Makefile`. That prototype explored VGA output, PS/2 keyboard input, a command loop, and temporary in-memory text storage. It is kept separate from the new x86_64 bootstrap while the architecture is being rebuilt and validated.

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

The host-side ZeroPKG prototype is now implemented in Python. It can create, inspect, and verify version-1 `.zpkg` archives. It checks payload paths, file sizes, SHA-256 digests, archive structure, and basic extraction-safety constraints. It does not install packages into the host or the running kernel.

Try the current host-side commands:

```bash
python3 tools/zeropkg.py --help
python3 -m unittest discover -s tests -v
```

The native commands above remain a future design target. Native installation depends on persistent storage, a VFS, an ELF64 loader, user-mode execution, process management, and system calls. Signed repository metadata and TLS-backed remote repositories are also future work.

See [ZeroPKG Design](docs/ZEROPKG.md) for the package format, current tool usage, trust model, and implementation milestones.

## Development roadmap

1. Expand boot-time memory mapping and formalize CPU initialization.
2. Add serial logging, GDT/IDT setup, and CPU exception handlers.
3. Implement physical memory management.
4. Build terminal and keyboard input services.
5. Design and implement the VFS and native ZeroFS.
6. Add a block-device abstraction and QEMU storage driver.
7. Connect filesystem operations to the shell.
8. Implement an ELF64 loader, user mode, processes, and system calls.
9. Expand ZeroPKG package-format tests and implement offline installation into a disposable test root.
10. Add transactional removal, package database, and dependency resolution.
11. Add signed repository metadata and network support after TLS is available.
11. Evaluate ext2 compatibility and additional device drivers.

## Development principles

- Build and test in QEMU before experimenting with physical hardware.
- Keep kernel code freestanding and independent of a host operating system at runtime.
- Separate bootstrapping, kernel services, drivers, filesystem code, and user applications.
- Test filesystem code against disposable virtual disk images.
- Verify package metadata, hashes, and signatures before installing software.
- Document which features are implemented, experimental, or planned.

## Educational use

Zero Kernel is an experimental learning project for exploring operating-system architecture, x86_64 assembly and C, bootloaders, CPU initialization, memory management, hardware drivers, filesystem design, executable formats, process management, and package management.

It is not intended for production use.

## License

MIT License

---

Built by **ZeroScope Intelligence** with C, Assembly, and curiosity.
