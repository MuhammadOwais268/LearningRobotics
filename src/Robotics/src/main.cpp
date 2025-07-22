#include <Arduino.h>
#include <Wire.h>
#include <VL53L0X.h>
#include <Adafruit_GFX.h>
#include <Adafruit_SSD1306.h>

// --- Pin Definitions ---
#define ENA 25
#define IN1 14
#define IN2 18
#define ENB 26
#define IN3 12
#define IN4 5

// =================================================================
// CONCEPT: CLASSES AND OBJECTS
// =================================================================

// The CLASS (the blueprint for our robot)
class Robot {
public:
    // Attributes: The hardware components the robot possesses.
    // These are objects of other classes provided by the libraries.
    VL53L0X sensor;
    Adafruit_SSD1306 display;

    // Constructor: Runs when a Robot object is created.
    Robot() : display(128, 64, &Wire, -1) { // Initialize the display object
        Serial.println("Robot object created in memory.");
    }

    // Method: A behavior. This initializes all the hardware.
    void initializeHardware() {
        Wire.begin();
        pinMode(ENA, OUTPUT); pinMode(IN1, OUTPUT); pinMode(IN2, OUTPUT);
        pinMode(ENB, OUTPUT); pinMode(IN3, OUTPUT); pinMode(IN4, OUTPUT);

        if (!display.begin(SSD1306_SWITCHCAPVCC, 0x3C)) {
            Serial.println("OLED allocation failed");
            for(;;);
        }
        sensor.setTimeout(500);
        if (!sensor.init()) {
            Serial.println("Sensor Failed!");
            while(1);
        }
        sensor.startContinuous();
        Serial.println("All robot hardware initialized.");
    }

    // Method: Reports the sensor reading to the OLED display.
    void reportStatus() {
        int distance = sensor.readRangeContinuousMillimeters();
        
        display.clearDisplay();
        display.setTextSize(2);
        display.setTextColor(WHITE);
        display.setCursor(0, 0);
        display.print("Dist: ");
        display.print(distance);
        display.print("mm");
        display.display();
    }
};

// --- Create a global OBJECT from the Robot CLASS ---
Robot myBot;

void setup() {
    Serial.begin(9600);
    delay(1000);
    
    // Command our object to initialize its hardware.
    myBot.initializeHardware();
}

void loop() {
    // Repeatedly command our object to report its status.
    myBot.reportStatus();
    delay(100);
}