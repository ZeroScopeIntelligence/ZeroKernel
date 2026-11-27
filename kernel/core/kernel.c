#include <stdint.h>

#define VGA_MEMORY ((volatile uint16_t*)0xB8000)
#define VGA_WIDTH 80
#define VGA_HEIGHT 25

static void terminal_clear(void)
{
    for (int i = 0; i < VGA_WIDTH * VGA_HEIGHT; i++)
    {
        VGA_MEMORY[i] = (uint16_t)0x0F20;
    }
}

static void terminal_write(const char* message, int row)
{
    int column = 0;

    while (*message && column < VGA_WIDTH)
    {
        VGA_MEMORY[row * VGA_WIDTH + column] =
            (uint16_t)(0x0A00 | (uint8_t)*message);

        message++;
        column++;
    }
}

void kernel_main(uint32_t magic, uintptr_t multiboot_info)
{
    (void)magic;
    (void)multiboot_info;

    terminal_clear();

    terminal_write("================================", 2);
    terminal_write("          ZERO KERNEL", 3);
    terminal_write("================================", 4);

    terminal_write("Architecture: x86_64", 7);
    terminal_write("Kernel: Zero Kernel", 8);
    terminal_write("Language: C / Assembly", 9);

    terminal_write("[OK] Bootloader initialized", 12);
    terminal_write("[OK] Kernel loaded", 13);
    terminal_write("[OK] Kernel entry reached", 14);

    terminal_write("Zero Kernel is running.", 17);

    while (1)
    {
        __asm__ volatile ("hlt");
    }
}
