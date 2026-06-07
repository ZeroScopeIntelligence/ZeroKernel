// Reads a single byte from a specific hardware I/O port
unsigned char inb(unsigned short port) {
    unsigned char result;
    __asm__ volatile("inb %1, %0" : "=a"(result) : "Nd"(port));
    return result;
}

// A layout map for standard lowercase US keys
// Find this array around line 9:
const char scancode_to_ascii[] = {
    0,  27, '1', '2', '3', '4', '5', '6', '7', '8', '9', '0', '-', '=', '\b',
    0, 'q', 'w', 'e', 'r', 't', 'y', 'u', 'i', 'o', 'p', '[', ']', '\n',  
    0,  'a', 's', 'd', 'f', 'g', 'h', 'j', 'k', 'l', ';', '\'', '`',   0,
 '\\', 'z', 'x', 'c', 'v', 'b', 'n', 'm', ',', '.', '/',   0,   '*',   0, ' '
};


// Global Tracking Variables
int cursor_row = 0;
int cursor_col = 0;
char cmd_buffer[80]; // Declared safely as an array
int cmd_len = 0;

// Virtual RAM File Storage 
char saved_file_content[256] = ""; // Declared safely as an array
int file_has_data = 0;             

// Helper function to compare strings up to a maximum number of characters (n)
int strncmp(const char *s1, const char *s2, int n) {
    while (n > 0 && *s1 && (*s1 == *s2)) {
        s1++;
        s2++;
        n--;
    }
    if (n == 0) {
        return 0;
    }
    return *(const unsigned char*)s1 - *(const unsigned char*)s2;
}

// Helper function to compare strings completely
int strcmp(const char *s1, const char *s2) {
    while (*s1 && (*s1 == *s2)) {
        s1++;
        s2++;
    }
    return *(const unsigned char*)s1 - *(const unsigned char*)s2;
}

// Clears the text screen entirely
void clear_screen() {
    char *video = (char*) 0xB8000;
    for(int i = 0; i < 80 * 25 * 2; i++) {
        video[i] = 0;
    }
    cursor_row = 0;
    cursor_col = 0;
}

// Prints a string and advances the screen cursor automatically
void print_string(const char *str, char color) {
    char *video = (char*) 0xB8000;
    int i = 0;
    
    while (str[i] != '\0') {
        if (str[i] == '\n') {
            cursor_row++;
            cursor_col = 0;
        } else {
            int offset = (cursor_row * 80 + cursor_col) * 2;
            video[offset] = str[i];
            video[offset + 1] = color;
            cursor_col++;
            
            if (cursor_col >= 80) {
                cursor_col = 0;
                cursor_row++;
            }
        }
        i++;
    }
}

// Prints the command prompt arrow
void print_prompt() {
    print_string("\nzero_kernel> ", 0x0B); 
}

// The Command Interpreter Core
void execute_command() {
    cmd_buffer[cmd_len] = '\0'; // Null-terminate the string buffer
    
    if (cmd_len == 0) {
        print_prompt();
        return;
    }
    
    print_string("\n", 0x0F);
    
    // 1. HELP COMMAND
    if (strcmp(cmd_buffer, "help") == 0) {
        print_string("Available commands:\n", 0x0F);
        print_string("  help         - Show this menu\n", 0x0A);
        print_string("  about        - Show operating system details\n", 0x0A);
        print_string("  clear        - Clear the text screen\n", 0x0A);
        print_string("  echo         - Repeat message back\n", 0x0A);
        print_string("  write        - Save text to virtual file\n", 0x0A);
        print_string("  read         - Read your saved text file\n", 0x0A);
        print_string("  shutdown     - Turn off the computer\n", 0x0A);
        print_string("  show version - Display the current OS version\n", 0x0A);
        print_string("  install      - Install the operating system\n", 0x0A);
    } 

    // Start of new commands added

    // 2. ABOUT COMMAND
    else if (strcmp(cmd_buffer, "about") == 0) {
        print_string("Zero OS v1.2.0\n", 0x0A); // Light Green
        print_string("Built by RUNNINDEAD", 0x0F);
    } 
    // 3. CLEAR COMMAND
    else if (strcmp(cmd_buffer, "clear") == 0) {
        clear_screen();
        cmd_len = 0;
        print_string("zero_kernel> ", 0x0B);
        return;
    } 
    // 4. ECHO COMMAND
    else if (strncmp(cmd_buffer, "echo ", 5) == 0) {
        print_string(&cmd_buffer[5], 0x0F); // Skips "echo " and prints content
    }
    // 5. WRITE COMMAND
    else if (strncmp(cmd_buffer, "write ", 6) == 0) {
        int i = 0;
        while (cmd_buffer[i + 6] != '\0' && i < 254) {
            saved_file_content[i] = cmd_buffer[i + 6];
            i++;
        }
        saved_file_content[i] = '\0';
        file_has_data = 1;
        print_string("File successfully written to RAM memory space!", 0x0A);
    }
    // 6. READ COMMAND
    else if (strcmp(cmd_buffer, "read") == 0) {
        if (file_has_data == 1) {
            print_string("Saved File Contents:\n", 0x0E); 
            print_string(saved_file_content, 0x0F);       
        } else {
            print_string("Error: No file data found. Use 'write [text]' first.", 0x0C); 
        }
    }
    
    else if (strcmp(cmd_buffer, "install") == 0) {
        print_string("Installing Zero OS to disk...", 0x0A);
        // Simulate installation process
        for (int i = 0; i < 5; i++) {
            print_string(".", 0x0A);
            for (volatile int j = 0; j < 100000000; j++); // Simple delay loop
        }
        print_string("\nInstallation complete! You can now boot from your disk.", 0x0A);



    }
    // 7. SHUTDOWN COMMAND
    else if (strcmp(cmd_buffer, "shutdown") == 0) {
        print_string("Shutting down Zero OS safely...", 0x0C);
        __asm__ volatile("outw %0, %1" : : "a"((unsigned short)0x2000), "d"((unsigned short)0x604));
        __asm__ volatile("outw %0, %1" : : "a"((unsigned short)0x2000), "d"((unsigned short)0xB004));
    }

    // 8. SHOW VERSION COMMAND
    else if (strcmp(cmd_buffer, "version") == 0 || strcmp(cmd_buffer, "show version") == 0) {        print_string("Zero OS Version: v1.0\n", 0x0A);
        print_string("Build Date: 2024-06-07\n", 0x0A);
        print_string("Author: RUNNINDEAD\n", 0x0A);
    }


    // 8. UNKNOWN COMMAND
    else {
        print_string("Unknown command: ", 0x0C); 
        print_string(cmd_buffer, 0x0C);
    }
    
    cmd_len = 0;
    print_prompt();
}

// Listens to hardware updates and parses keys
void run_cli_loop() {
    char *video_memory = (char*) 0xB8000;
    
    while(1) {
        if ((inb(0x64) & 1) == 1) {
            unsigned char scancode = inb(0x60);
            
            if (scancode < 0x80) { 
                char c = scancode_to_ascii[scancode];
                
                if (c == '\n') {
                    execute_command();
                } 
                else if (c == '\b') {
                    if (cmd_len > 0) {
                        cmd_len--;
                        cursor_col--;
                        int offset = (cursor_row * 80 + cursor_col) * 2;
                        video_memory[offset] = ' ';     
                        video_memory[offset + 1] = 0;   
                    }
                } 
                else if (c != 0 && cmd_len < 79) {
                    cmd_buffer[cmd_len] = c;
                    cmd_len++;
                    
                    int offset = (cursor_row * 80 + cursor_col) * 2;
                    video_memory[offset] = c;
                    video_memory[offset + 1] = 0x0F; 
                    cursor_col++;
                }
            }
        }
    }
}


// Initial Shell Kernel Main Entry Point
void kernel_main(void) {
    clear_screen();
    
    print_string("==================================================\n", 0x0A);
    print_string("          Welcome to Zero OS v1.0\n", 0x0A);
    print_string("==================================================\n", 0x0A);
    print_string("Type 'help' to see available system tools.", 0x07);
    
    print_prompt();
    run_cli_loop(); 
}
