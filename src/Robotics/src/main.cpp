#include <Arduino.h>
#include <Wire.h>
#include <VL53L0X.h> // Include the Pololu sensor library
#include <Adafruit_GFX.h>
#include <Adafruit_SSD1306.h>

#define SCREEN_WIDTH 128
#define SCREEN_HEIGHT 64

VL53L0X sensor;
Adafruit_SSD1306 display(SCREEN_WIDTH, SCREEN_HEIGHT, &Wire, -1);

// A variable of datatype 'int' to store a whole number
int distance_mm = 0; 
// A variable of datatype 'bool' to store a true/false value
bool sensor_ok = false;

void setup() {
  Wire.begin();
  display.begin(SSD1306_SWITCHCAPVCC, 0x3C);

  // Initialize the sensor and store the result in our boolean variable
  sensor.setTimeout(500);
  if (sensor.init()) {
    sensor_ok = true;
    sensor.startContinuous();
  }
  
  // Display status based on the boolean variable's value
  display.clearDisplay();
  display.setTextSize(1);
  display.setTextColor(WHITE);
  display.setCursor(0, 0);
  if (sensor_ok) {
    display.println("Sensor... OK");
  } else {
    display.println("Sensor... FAILED");
  }
  display.display();
  delay(2000);
}

void loop() {
  // Store the latest sensor reading in our integer variable
  distance_mm = sensor.readRangeContinuousMillimeters();

  // Display the content of the variable on the screen
  display.clearDisplay();
  display.setTextSize(2);
  display.setCursor(0, 0);
  display.print("Dist:");
  display.setCursor(0, 20);
  display.print(distance_mm); // This prints the number stored in the variable
  display.print(" mm");
  display.display();
  
  delay(100);
}