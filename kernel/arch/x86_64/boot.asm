BITS 32

section .multiboot
align 8

multiboot_header:
    dd 0xE85250D6
    dd 0
    dd multiboot_header_end - multiboot_header
    dd -(0xE85250D6 + 0 + (multiboot_header_end - multiboot_header))

    dw 0
    dw 0
    dd 8

multiboot_header_end:

section .bss
align 16

stack_bottom:
    resb 16384
stack_top:

section .text
global _start
extern kernel_main

_start:
    cli

    mov esp, stack_top

    ; Preserve Multiboot2 information pointer
    mov esi, ebx

    ; Set up page tables
    call setup_page_tables

    ; Enable PAE and PSE
    mov eax, cr4
    or eax, (1 << 5) | (1 << 4)
    mov cr4, eax

    ; Load PML4
    mov eax, pml4_table
    mov cr3, eax

    ; Enable long mode
    mov ecx, 0xC0000080
    rdmsr
    or eax, 1 << 8
    wrmsr

    ; Enable paging
    mov eax, cr0
    or eax, 1 << 31
    mov cr0, eax

    ; Load GDT and enter 64-bit mode
    lgdt [gdt64.pointer]
    jmp 0x08:long_mode_start

setup_page_tables:
    mov eax, pdpt_table
    or eax, 0x03
    mov [pml4_table], eax

    mov eax, pd_table
    or eax, 0x03
    mov [pdpt_table], eax

    ; Map the first 2 MiB using a 2 MiB page
    mov dword [pd_table], 0x00000083
    mov dword [pd_table + 4], 0

    ret

BITS 64

long_mode_start:
    ; Initialize data segments
    mov ax, 0x10
    mov ds, ax
    mov es, ax
    mov ss, ax

    ; Initialize stack
    mov rsp, stack_top

    ; Pass Multiboot2 magic and information pointer
    mov edi, 0x36D76289
    mov esi, esi

    call kernel_main

.hang:
    cli
    hlt
    jmp .hang

section .rodata
align 8

gdt64:
    dq 0
    dq 0x00AF9A000000FFFF
    dq 0x00CF92000000FFFF

.pointer:
    dw $ - gdt64 - 1
    dq gdt64

section .bss
align 4096

pml4_table:
    resb 4096

pdpt_table:
    resb 4096

pd_table:
    resb 4096
