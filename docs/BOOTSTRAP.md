# Zero Kernel x86_64 Bootstrap

**Status:** First QEMU boot successful. This is an early boot foundation, not a feature-complete operating system.

## What is implemented

- GRUB Multiboot2 boot header.
- 32-bit protected-mode entry supplied by GRUB.
- Initial page tables and transition into x86_64 long mode.
- A small GDT used for the long-mode transition.
- A 16 KiB bootstrap stack.
- A freestanding C kernel entry point.
- VGA text-mode output.
- A halt loop after kernel initialization.
- ISO creation with GRUB and QEMU boot testing.

The first successful screen displayed the Zero Kernel title, architecture and language information, and three initialization messages.

## Source layout

```text
boot/
└── grub/
    └── grub.cfg
docker/
└── Dockerfile
kernel/
├── arch/
│   └── x86_64/
│       └── boot.asm
└── core/
    └── kernel.c
linker.ld
Makefile
```

The repository also retains the earlier prototype source files under `kernel/` (including `kernel/kernel.c`, `kernel/boot.asm`, `kernel/linker.ld`, and `kernel/Makefile`). The new root-level Makefile builds the x86_64 bootstrap files listed above; it does not build or replace that earlier prototype.

## Build environment

The project uses a Debian Trixie container with:

- GCC and GNU Binutils
- NASM
- GNU Make
- GRUB utilities
- xorriso and mtools
- QEMU system emulator
- Build dependencies for the x86_64-elf cross-compiler

Build the container from the repository root:

```bash
docker build -t zerokernel-builder -f docker/Dockerfile .
```

Start it with the repository mounted at `/workspace`:

```bash
docker run --rm -it -v "$PWD:/workspace" zerokernel-builder
```

## Cross-compiler

The bootstrap is compiled with an `x86_64-elf` cross-compiler. Build and install GNU Binutils and GCC into the project-local `.toolchain` directory. The toolchain directory is ignored by Git because it contains generated build tools.

Example environment setup inside the container:

```bash
export PREFIX=/workspace/.toolchain
export TARGET=x86_64-elf
export PATH="$PREFIX/bin:$PATH"
```

Build Binutils with the target `x86_64-elf`, then build GCC with C as the enabled language and `--without-headers`. Build and install target libgcc as well. The root Makefile automatically prepends `.toolchain/bin` to PATH when invoked.

Verify the compiler:

```bash
x86_64-elf-gcc --version
x86_64-elf-as --version
x86_64-elf-ld --version
```

## Build and validate

From the repository root, after the cross-compiler is installed:

```bash
make
make check
make iso
ls -lh build/zerokernel.iso
```

The check target uses `grub-file --is-x86-multiboot2` to validate the kernel image's Multiboot2 header.

## Run in QEMU

With a graphical display:

```bash
make run
```

For a terminal-only environment that supports the curses display backend:

```bash
qemu-system-x86_64 \
    -cdrom build/zerokernel.iso \
    -m 256M \
    -display curses \
    -monitor none
```

The kernel currently writes directly to VGA text memory at physical address `0xB8000`; it does not yet provide serial logging.

## Current limitations

- The bootstrap maps only the first 2 MiB of physical memory with a 2 MiB page. Keep the linked kernel, stack, and page tables within this mapped range until page-table coverage is expanded.
- VGA text output is used; serial output is not implemented.
- No IDT, exception handlers, or hardware interrupt handlers are installed yet.
- No physical or virtual memory manager exists yet.
- No keyboard, storage, filesystem, process, or user-mode support is part of this bootstrap.
- The Multiboot2 information pointer is currently passed to the C entry point but not parsed.
- The boot screen is a milestone test, not evidence of a complete operating system.

## Next milestones

1. Add serial logging for reliable terminal-based debugging.
2. Implement the IDT and CPU exception handlers.
3. Expand and formalize GDT/CPU initialization.
4. Add physical memory-map parsing and a physical memory manager.
5. Build reusable terminal and keyboard drivers.
6. Add storage, VFS, and ZeroFS support.
7. Add process management, system calls, and user-mode execution.
