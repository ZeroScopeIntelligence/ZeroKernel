ENTRY(start)                    /* Tell the linker our entry point is 'start' */

SECTIONS {
    . = 0x100000;               /* Start arranging code at 1MB in memory */

    .text : {
        *(.multiboot)           /* The multiboot header must go first! */
        *(.text)                /* Followed by the actual code */
    }

    .rodata : { *(.rodata) }    /* Read-only data (like text strings) */
    .data   : { *(.data) }      /* Initialized variables */
    .bss    : { *(.bss) }       /* Uninitialized variables & our stack */
}
