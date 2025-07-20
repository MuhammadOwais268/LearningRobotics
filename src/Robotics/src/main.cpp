#include <Arduino.h>

// Most ESP32 boards have a built-in LED connected to GPIO pin 2.
// The 'LED_BUILTIN' variable is a shortcut for this pin number.
const int ledPin = LED_BUILTIN;

// The setup() function runs once when you press reset or power the board
void setup() {
  // Initialize the digital pin as an output.
  // This tells the ESP32 that we will be sending signals OUT of this pin.
  pinMode(ledPin, OUTPUT);
}

// The loop() function runs over and over again forever
void loop() {
  // Turn the LED on by making the voltage HIGH
  digitalWrite(ledPin, HIGH);

  // Wait for one second (1000 milliseconds)
  delay(1000);

  // Turn the LED off by making the voltage LOW
  digitalWrite(ledPin, LOW);

  // Wait for another second
  delay(1000);
}