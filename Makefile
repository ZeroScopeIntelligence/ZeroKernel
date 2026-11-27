TARGET = x86_64-elf

CC = $(TARGET)-gcc
AS = nasm
BUILD = build

# Use the project-local cross-compiler when it has been built.
export PATH := $(CURDIR)/.toolchain/bin:$(PATH)

CFLAGS = -std=gnu11 \
         -ffreestanding \
         -fno-stack-protector \
         -fno-pic \
         -fno-pie \
         -mno-red-zone \
         -mcmodel=small \
         -O2 \
         -Wall \
         -Wextra

LDFLAGS = -nostdlib \
          -static \
          -no-pie \
          -Wl,--build-id=none \
          -T linker.ld

C_SOURCES = kernel/core/kernel.c
ASM_SOURCES = kernel/arch/x86_64/boot.asm
OBJECTS = $(BUILD)/boot.o $(BUILD)/kernel.o

.PHONY: all iso run check clean

all: $(BUILD)/kernel.elf

$(BUILD):
	mkdir -p $(BUILD)

$(BUILD)/boot.o: $(ASM_SOURCES) | $(BUILD)
	$(AS) -f elf64 $< -o $@

$(BUILD)/kernel.o: $(C_SOURCES) | $(BUILD)
	$(CC) $(CFLAGS) -c $< -o $@

$(BUILD)/kernel.elf: $(OBJECTS) linker.ld
	$(CC) $(LDFLAGS) -o $@ $(OBJECTS) -lgcc

check: $(BUILD)/kernel.elf
	grub-file --is-x86-multiboot2 $<
	@echo "Multiboot2 validation successful."

iso: check
	mkdir -p iso/boot/grub
	cp $(BUILD)/kernel.elf iso/boot/kernel.elf
	cp boot/grub/grub.cfg iso/boot/grub/grub.cfg
	grub-mkrescue -o $(BUILD)/zerokernel.iso iso

run: iso
	qemu-system-x86_64 -cdrom $(BUILD)/zerokernel.iso -m 256M

clean:
	rm -rf $(BUILD) iso/boot
