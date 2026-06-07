// Define standard VGA color attributes for easier reading
#define COLOR_WHITE_ON_BLACK 0x0F
#define COLOR_GREEN_ON_BLUE  0x1A
#define COLOR_RED_ON_BLACK   0x04
#define COLOR_YELLOW_ON_RED  0x4E

// Function to print a string at a specific screen position with a custom color
void print_string_with_color(const char *str, int row, int col, char color_attribute) {
    // VGA text mode buffer begins at this memory address
    char *video_memory = (char*) 0xB8000;
    
    // Calculate the exact memory offset based on screen dimensions (80 columns x 25 rows)
    // Multiplied by 2 because each character uses 2 bytes (character + color)
    int offset = (row * 80 + col) * 2;
    
    int i = 0;
    while (str[i] != '\0') {
        video_memory[offset] = str[i];             // Write character byte
        video_memory[offset + 1] = color_attribute; // Write color attribute byte
        
        offset += 2; // Advance to the next character position in memory
        i++;
    }
}

void kernel_main(void) {
    // Print custom messages with distinct color combinations
    print_string_with_color("Welcome to ZeroScope Kernel!", 2, 5, COLOR_GREEN_ON_BLUE);

    // Keep the CPU running indefinitely
    while(1);
}
