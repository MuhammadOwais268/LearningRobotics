// <<< FIX: Include the main Arduino header FIRST >>>
// This ensures all core definitions (like Wire) are loaded before any other library.
#include <Arduino.h>

// Now include the other libraries
#include <Wire.h>
#include <Adafruit_GFX.h>
#include <Adafruit_SSD1306.h>

#define SCREEN_WIDTH 128
#define SCREEN_HEIGHT 64

// Create the display object globally. This is safe now because Arduino.h is included first.
Adafruit_SSD1306 display(SCREEN_WIDTH, SCREEN_HEIGHT, &Wire, -1);

void setup() {
  // Start I2C communication (required for the OLED)
  Wire.begin();

  // Initialize the display
  if (!display.begin(SSD1306_SWITCHCAPVCC, 0x3C)) {
    for (;;); // If it fails, halt the program
  }

  // --- Main Actions ---
  display.clearDisplay();
  display.setTextSize(2);
  display.setTextColor(WHITE);
  display.setCursor(10, 10);
  display.println("Hello");
  display.println(" Robot!");
  display.display(); // Push the text to the screen
}

void loop() {
  // The screen is static, so nothing needs to be repeated here.
}