KERNEL = mykernel.bin

all: $(KERNEL)

$(KERNEL): boot.o kernel.o
	ld -m elf_i386 -T linker.ld boot.o kernel.o -o $(KERNEL)

boot.o: boot.asm
	nasm -f elf32 boot.asm -o boot.o

kernel.o: kernel.c
	gcc -m32 -c kernel.c -o kernel.o -ffreestanding -O2 -Wall -Wextra

run: $(KERNEL)
	qemu-system-i386 -kernel $(KERNEL)

clean:
	rm -f *.o $(KERNEL)
