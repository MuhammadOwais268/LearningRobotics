#include <Wire.h>
#include <VL53L0X.h>
#include "L298N.h"  // Make sure you have your custom L298N.h library

// Motor control pins: ENA, IN1, IN2
L298N motor(14, 27, 26);
VL53L0X sensor;

void setup() {
  Serial.begin(115200);
  Wire.begin();  // Initialize I2C for VL53L0X

  sensor.setTimeout(500);

  if (!sensor.init()) {
    Serial.println("VL53L0X not detected.");
    while (1);  // Stay here if sensor not found
  }

  sensor.startContinuous();  // Start taking continuous distance readings
  motor.setSpeed(200);       // Set initial motor speed (0–255)
}

void loop() {
  int distance = sensor.readRangeContinuousMillimeters();

  if (sensor.timeoutOccurred()) {
    Serial.println("Sensor timeout");
    motor.stop();
    return;
  }

  Serial.print("Distance: ");
  Serial.print(distance);
  Serial.println(" mm");

  // Control logic: closed-loop based on distance
  if (distance < 150) {
    Serial.println("Too close: Reversing");
    motor.backward();
  } else if (distance > 250) {
    Serial.println("Too far: Moving forward");
    motor.forward();
  } else {
    Serial.println("In range: Stopping");
    motor.stop();
  }

  delay(100);
}
