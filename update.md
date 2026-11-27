# Zero Kernel — Project Update

## Completed: First x86_64 boot

The new x86_64 bootstrap has successfully built and booted in QEMU.

- Added a GRUB Multiboot2 header and boot menu.
- Added the NASM entry point and initial page tables.
- Transitioned from the GRUB 32-bit environment into x86_64 long mode.
- Added the initial GDT and bootstrap stack.
- Added the freestanding C kernel entry point.
- Added VGA text output for the first boot screen.
- Added a root-level Makefile for the ELF kernel, Multiboot2 validation, ISO creation, and QEMU launch.
- Added a Debian Trixie Docker build environment.
- Documented the bootstrap and updated the repository README.

## Current state

The first boot screen confirms that the kernel reaches `kernel_main()` and can write to VGA text memory. This is an early boot foundation, not a complete operating system.

The initial page tables currently map only the first 2 MiB of physical memory. Serial logging, IDT/exception handling, memory management, keyboard input, and storage support remain future work.

## Next development milestones

1. Add serial logging for terminal-based debugging.
2. Implement the IDT and CPU exception handlers.
3. Expand memory mapping and add physical memory management.
4. Build reusable terminal and keyboard drivers.
5. Continue toward the VFS and native ZeroFS filesystem.
6. Develop process management, system calls, and user-mode execution.

See [README.md](README.md) and [docs/BOOTSTRAP.md](docs/BOOTSTRAP.md) for build instructions and technical details.
