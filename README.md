# Zero Kernel

A minimal x86 operating system kernel written in C that runs directly on bare metal.

Zero Kernel provides a lightweight command-line interface, direct VGA text output, keyboard input handling, and simple in-memory file storage without relying on any existing operating system.

---

## Features

* 🖥️ VGA text mode terminal
* ⌨️ PS/2 keyboard input
* 💻 Interactive command shell
* 📄 Virtual RAM-based file storage
* 🧹 Screen clearing
* 🔊 Echo command
* 📚 Built-in help menu
* ⚡ Direct hardware I/O using inline assembly
* 🔌 ACPI/QEMU shutdown support
* 🛠️ Simple installation simulation

---

## Current Commands

| Command        | Description                       |
| -------------- | --------------------------------- |
| `help`         | Display available commands        |
| `about`        | Show operating system information |
| `clear`        | Clear the display                 |
| `echo <text>`  | Print text back to the terminal   |
| `write <text>` | Save text into virtual RAM        |
| `read`         | Display saved RAM contents        |
| `version`      | Display system version            |
| `show version` | Display system version            |
| `install`      | Simulate installation process     |
| `shutdown`     | Power off the virtual machine     |

---

## Example

```text
==================================================
          Welcome to Zero OS v1.0
==================================================

Type 'help' to see available system tools.

zero_kernel> help

Available commands:
help
about
clear
echo
write
read
shutdown
show version
install
```

---

## Project Structure

```text
Zero-Kernel/
│
├── kernel.c
├── linker.ld
├── boot.asm
├── Makefile
├── README.md
```

---

## How It Works

### Keyboard Driver

Keyboard input is read directly from the PS/2 controller.

```c
inb(0x60)
```

Scancodes are translated into ASCII characters using a lookup table.

---

### VGA Output

Characters are written directly into VGA text memory.

```c
0xB8000
```

Every character contains:

* ASCII value
* Text color

---

### Command Interpreter

User input is buffered until Enter is pressed.

The kernel compares the command against supported commands using its own implementations of:

* `strcmp()`
* `strncmp()`

No C standard library is required.

---

### Virtual File Storage

The `write` command stores text inside a RAM buffer.

```text
write Hello World
```

Later it can be retrieved using

```text
read
```

This acts as a simple in-memory virtual file system.

---

## Requirements

* x86 Emulator

  * QEMU (recommended)
  * Bochs
  * VirtualBox (with appropriate boot image)

* GCC Cross Compiler

* NASM

* GNU Make

---

## Future Goals

* Memory manager
* Interrupt Descriptor Table (IDT)
* Paging
* Dynamic heap allocation
* FAT12/FAT32 filesystem
* Disk driver
* Process scheduler
* User mode applications
* ELF executable loader
* Networking
* PCI device support
* Mouse driver
* Real filesystem
* Graphical desktop

---

## Why Zero Kernel?

Zero Kernel is a learning operating system project built from scratch to explore low-level programming concepts including:

* Operating system development
* Computer architecture
* Bare-metal programming
* Hardware communication
* Memory management
* Shell design
* Kernel development

---

## Disclaimer

This project is intended for educational purposes. It is an experimental hobby operating system and is not designed for production use.

---

## License

MIT License

---

Built with C, Assembly, and curiosity.
