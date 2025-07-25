#include <Wire.h>
#include <VL53L0X.h>
#include "L298N.h"
#include <Adafruit_GFX.h>
#include <Adafruit_SSD1306.h>

// OLED setup
#define SCREEN_WIDTH 128
#define SCREEN_HEIGHT 64
Adafruit_SSD1306 display(SCREEN_WIDTH, SCREEN_HEIGHT, &Wire, -1);

// Motor + Sensor
L298N motor(14, 27, 26);
VL53L0X sensor;

// PID setup
float setpoint = 200;
float Kp = 1.5, Ki = 0.2, Kd = 0.3;
float error = 0, prev_error = 0, integral = 0;
float dt = 0.1;

// FSM states
enum State { IDLE, FORWARD, AVOID };
State state = IDLE;
unsigned long stateStart = 0;

// Moving Average Filter
#define N 5
int readings[N] = {0};
int readIndex = 0;

int getFilteredDistance(int newVal) {
  readings[readIndex] = newVal;
  readIndex = (readIndex + 1) % N;
  int sum = 0;
  for (int i = 0; i < N; i++) sum += readings[i];
  return sum / N;
}

void setup() {
  Serial.begin(115200);
  Wire.begin();

  if (!display.begin(SSD1306_SWITCHCAPVCC, 0x3C)) {
    Serial.println("OLED failed");
    while (1);
  }

  sensor.setTimeout(500);
  if (!sensor.init()) {
    Serial.println("VL53L0X failed");
    while (1);
  }
  sensor.startContinuous();
  motor.setSpeed(0);
  stateStart = millis();
}

void loop() {
  int rawDistance = sensor.readRangeContinuousMillimeters();
  if (sensor.timeoutOccurred()) {
    Serial.println("Sensor timeout");
    motor.stop();
    return;
  }

  int distance = getFilteredDistance(rawDistance);

  // FSM Logic
  switch (state) {
    case IDLE:
      motor.stop();
      if (millis() - stateStart > 3000) {
        state = FORWARD;
        stateStart = millis();
      }
      break;

    case FORWARD:
      if (distance < 150) {
        motor.backward();
        state = AVOID;
        stateStart = millis();
      } else {
        error = setpoint - distance;
        integral += error * dt;
        float derivative = (error - prev_error) / dt;
        prev_error = error;

        float output = Kp * error + Ki * integral + Kd * derivative;

        int speed = constrain(abs(output), 0, 255);
        motor.setSpeed(speed);
        if (output > 0) motor.forward();
        else if (output < 0) motor.backward();
        else motor.stop();
      }
      break;

    case AVOID:
      if (millis() - stateStart > 1000) {
        state = FORWARD;
        stateStart = millis();
      }
      break;
  }

  // OLED feedback
  display.clearDisplay();
  display.setCursor(0, 0);
  display.setTextSize(1);
  display.setTextColor(WHITE);
  display.println("Sensor Filtering");
  display.print("Raw: "); display.println(rawDistance);
  display.print("Filtered: "); display.println(distance);
  display.print("Error: "); display.println(error);
  display.print("State: ");
  display.println(state == IDLE ? "IDLE" : (state == FORWARD ? "FORWARD" : "AVOID"));
  display.display();

  delay(dt * 1000);
}
