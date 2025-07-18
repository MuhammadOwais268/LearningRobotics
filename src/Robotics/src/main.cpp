#include <Arduino.h>  // Includes the core Arduino functions

void setup() {
  Serial.begin(9600);  // Start Serial communication at 115200 baud
  Serial.println("Setup complete. Starting Hello World...");
}

void loop() {
  Serial.println("Hello, World!");  // Print Hello, World! to the Serial Monitor
  delay(1000);                      // Wait for 1 second
}
