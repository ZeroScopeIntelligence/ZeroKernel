bits 32                         ; We are working in 32-bit protected mode
section .multiboot              ; Special section for the bootloader signature
    ALIGN 4
    MAGIC    equ 0x1BADB002     ; Magic number letting GRUB find our kernel
    FLAGS    equ 0x00           ; Flags
    CHECKSUM equ -(MAGIC + FLAGS)

    dd MAGIC
    dd FLAGS
    dd CHECKSUM

section .text
global start
extern kernel_main              ; Links to the main function in kernel.c

start:
    cli                         ; Disable hardware interrupts
    mov esp, stack_space        ; Point the CPU stack pointer to our memory area
    call kernel_main            ; Jump into our C kernel code
    
halt:
    hlt                         ; If kernel_main returns, halt the CPU
    jmp halt

section .bss
resb 8192                       ; Reserve 8 Kilobytes of memory for the stack
stack_space:
