#include <Arduino.h>
#include <Wire.h>
#include <string>
#include <Adafruit_GFX.h>
#include <Adafruit_SSD1306.h>

// =================================================================
// CONCEPT: POINTERS
// A pointer is a variable that holds a memory address. We can use it
// to dynamically choose which object's function to call.
// =================================================================

// --- Define an "Interface" using an Abstract Base Class ---
// This blueprint says that any "Blinker" object MUST have a blink() method.
class Blinker {
public:
    virtual void initialize() = 0; // Pure virtual function
    virtual void blink() = 0;      // Pure virtual function
};

// --- First Implementation: Blinks the on-board LED ---
class LedBlinker : public Blinker {
public:
    void initialize() override {
        pinMode(LED_BUILTIN, OUTPUT);
        Serial.println("On-board LED initialized.");
    }
    
    void blink() override {
        Serial.println("Blinking on-board LED...");
        digitalWrite(LED_BUILTIN, HIGH);
        delay(500);
        digitalWrite(LED_BUILTIN, LOW);
        delay(500);
    }
};

// --- Second Implementation: Blinks a message on the OLED ---
class OledBlinker : public Blinker {
private:
    Adafruit_SSD1306 display;

public:
    OledBlinker() : display(128, 64, &Wire, -1) {}

    void initialize() override {
        if (!display.begin(SSD1306_SWITCHCAPVCC, 0x3C)) {
             Serial.println("OLED Failed!");
             for(;;);
        }
        Serial.println("OLED Display initialized.");
    }

    void blink() override {
        Serial.println("Blinking message on OLED...");
        display.clearDisplay();
        display.setTextSize(2);
        display.setTextColor(WHITE);
        display.setCursor(20, 10);
        display.println("BLINK!");
        display.display();
        delay(500);
        
        display.clearDisplay();
        display.display();
        delay(500);
    }
};

// --- Global Objects ---
LedBlinker myLed;
OledBlinker myOled;

// This is our POINTER. It's a variable that can hold the address
// of ANY object that is a "Blinker" (i.e., LedBlinker or OledBlinker).
Blinker* currentBlinkerPtr = nullptr;


void setup() {
    Serial.begin(115200);
    Wire.begin();
    delay(1000);
    Serial.println("--- Program Start: Pointers ---");
    
    myLed.initialize();
    myOled.initialize();

    // --- Using the Pointer ---
    // First, let's make the pointer hold the ADDRESS of the myLed object.
    Serial.println("\nSetting pointer to the LED Blinker...");
    currentBlinkerPtr = &myLed;
}

void loop() {
    // This is the magic of pointers. We don't need to know if we are
    // controlling the LED or the OLED. We just tell the pointer:
    // "Go to the address you're holding and call the blink() method on whatever object you find there."
    currentBlinkerPtr->blink();
    
    // Every 5 blinks, we will SWITCH what the pointer is pointing to.
    static int blinkCount = 0;
    blinkCount++;
    if (blinkCount % 5 == 0) {
        // Check what the pointer is currently pointing to
        if (currentBlinkerPtr == &myLed) {
            // If it's pointing to the LED, switch it to point to the OLED
            Serial.println("\n>>> SWITCHING pointer to OLED Blinker <<<");
            currentBlinkerPtr = &myOled;
        } else {
            // If it's pointing to the OLED, switch it back to the LED
            Serial.println("\n>>> SWITCHING pointer back to LED Blinker <<<");
            currentBlinkerPtr = &myLed;
        }
    }
}