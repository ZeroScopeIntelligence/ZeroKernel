// Reads a single byte from a specific hardware I/O port
unsigned char inb(unsigned short port) {
    unsigned char result;
    // Inline assembly to read from 'port' into 'result'
    __asm__ volatile("inb %1, %0" : "=a"(result) : "Nd"(port));
    return result;
}

// A simplified layout map for standard lowercase US keys (Scancodes 0x00 to 0x39)
const char scancode_to_ascii[] = {
    0,  27, '1', '2', '3', '4', '5', '6', '7', '8', '9', '0', '-', '=', '\b',
  '\t', 'q', 'w', 'e', 'r', 't', 'y', 'u', 'i', 'o', 'p', '[', ']', '\n',
    0,  'a', 's', 'd', 'f', 'g', 'h', 'j', 'k', 'l', ';', '\'', '`',   0,
 '\\', 'z', 'x', 'c', 'v', 'b', 'n', 'm', ',', '.', '/',   0,   '*',   0, ' '
};

// Continuous loop checking the keyboard controller hardware status
void read_keyboard() {
    char *video_memory = (char*) 0xB8000;
    int cursor_offset = 160; // Start printing on the second line of the screen
    
    while(1) {
        // Step A: Check if a key data byte is ready (Read status port 0x64)
        if ((inb(0x64) & 1) == 1) {
            
            // Step B: Read the raw scancode from data port 0x60
            unsigned char scancode = inb(0x60);
            
            // If the highest bit is set (scancode >= 0x80), the key was RELEASED.
            // We only process values less than 0x80 (key pressed down).
            if (scancode < 0x80) {
                
                // Get the readable character from our layout map
                char c = scancode_to_ascii[scancode];
                
                if (c != 0) {
                    // Write the character straight to screen memory
                    video_memory[cursor_offset] = c;
                    video_memory[cursor_offset + 1] = 0x0A; // Light Green text
                    
                    // Move our text cursor position forward by 2 bytes
                    cursor_offset += 2;
                }
            }
        }
    }
}

// Main Entry Point (Called from assembly boot loader)
void kernel_main(void) {
    char *video = (char*) 0xB8000;
    
    // Clear screen text space
    for(int i = 0; i < 80 * 25 * 2; i++) {
        video[i] = 0;
    }
    
    // Print initialization title string on the first line
    char *title = "Zero OS Keyboard Driver Active. Start typing below:";
    int i = 0;
    while(title[i] != '\0') {
        video[i * 2] = title[i];
        video[i * 2 + 1] = 0x0F; // White text
        i++;
    }
    
    // Hand execution loop control entirely over to the keyboard reader
    read_keyboard(); 
}
