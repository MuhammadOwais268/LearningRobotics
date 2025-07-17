// File: src/main.cpp

#include <Arduino.h>  // ✅ This line is required

void setup() {
  pinMode(2, OUTPUT); // GPIO 2 is usually the onboard LED
}

void loop() {
  digitalWrite(2, HIGH); // Turn LED ON
  delay(500);            // Wait 500 milliseconds
  digitalWrite(2, LOW);  // Turn LED OFF
  delay(500);            // Wait 500 milliseconds
}
