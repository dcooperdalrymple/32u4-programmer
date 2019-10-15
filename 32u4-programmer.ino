/**
 * Title: 32u4 Programmer
 * Author: D Cooper Dalrymple
 * Created: 20/08/2019
 * Updated: 15/10/2019
 * https://dcooperdalrymple.com/
 */

/**
 * Resources:
 * - https://github.com/rsbohn/ArduinoISP/blob/master/ArduinoISP/ArduinoISP.ino
 * - https://github.com/mkeller0815/MEEPROMMER/blob/master/Arduino/MEEPROMMERfirmware/MEEPROMMERfirmware.ino
 */

#include "SPI.h"
#include "pins_arduino.h"

enum programmerMode {
    NONE,
    EEPROM,
    ISP
};

#define HEARTBEAT_PIN 13
#define HEARTBEAT_STEP 256


programmerMode mode = NONE;
uint8_t error = 0;
uint8_t buffer[256];

void setup() {
    Serial.begin(9600);

    pinMode(HEARTBEAT_PIN, OUTPUT);
}

void loop() {
    if (error) {

    }

    heartbeat();

    if (Serial.available()) {
        readSerial();
    }
}

void heartbeat() {
    if (millis() % HEARTBEAT_STEP < HEARTBEAT_STEP / 2) {
        digitalWrite(HEARTBEAT_PIN, HIGH);
    } else {
        digitalWrite(HEARTBEAT_PIN, LOW);
    }
}

void readSerial() {
    switch (mode) {
        case EEPROM:
            readEEPROM();
            break;
        case ISP:
            readISP();
            break;
        case NONE:
        default:
            readControl();
            break;
    }
}

void readControl() {

}

void setupEEPROM() {
    mode = EEPROM;
}

void readEEPROM() {

}

void setupISP() {
    mode = ISP;

    SPI.setDataMode(0);
    SPI.setBitOrder(MSBFIRST);
    SPI.setClockDivider(SPI_CLOCK_DIV128);
}

void readISP() {

}
