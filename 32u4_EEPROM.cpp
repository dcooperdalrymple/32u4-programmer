/**
 * File: 32u4_EEPROM.cpp
 * Created: 19/10/2019
 * Updated: 01/11/2019
 */

#include "32u4_EEPROM.h"

void setupEEPROM() {
  pinMode(DATA, OUTPUT);
  pinMode(LATCH, OUTPUT);
  pinMode(CLOCK, OUTPUT);

  digitalWrite(OE, HIGH);
  pinMode(OE, OUTPUT);
  digitalWrite(CE, HIGH);
  pinMode(CE, OUTPUT);
  digitalWrite(WE, HIGH);
  pinMode(WE, OUTPUT);
}

void data_bus_input() {
  pinMode(D0, INPUT);
  pinMode(D1, INPUT);
  pinMode(D2, INPUT);
  pinMode(D3, INPUT);
  pinMode(D4, INPUT);
  pinMode(D5, INPUT);
  pinMode(D6, INPUT);
  pinMode(D7, INPUT);
}

void data_bus_output() {
  pinMode(D0, OUTPUT);
  pinMode(D1, OUTPUT);
  pinMode(D2, OUTPUT);
  pinMode(D3, OUTPUT);
  pinMode(D4, OUTPUT);
  pinMode(D5, OUTPUT);
  pinMode(D6, OUTPUT);
  pinMode(D7, OUTPUT);
}

uint8_t read_data_bus() {
  return ((digitalRead(D7) << 7) +
          (digitalRead(D6) << 6) +
          (digitalRead(D5) << 5) +
          (digitalRead(D4) << 4) +
          (digitalRead(D3) << 3) +
          (digitalRead(D2) << 2) +
          (digitalRead(D1) << 1) +
          digitalRead(D0));
}

void write_data_bus(uint8_t data) {
  digitalWrite(D0, (data >> 0) & 0x01);
  digitalWrite(D1, (data >> 1) & 0x01);
  digitalWrite(D2, (data >> 2) & 0x01);
  digitalWrite(D3, (data >> 3) & 0x01);
  digitalWrite(D4, (data >> 4) & 0x01);
  digitalWrite(D5, (data >> 5) & 0x01);
  digitalWrite(D6, (data >> 6) & 0x01);
  digitalWrite(D7, (data >> 7) & 0x01);
}

void set_address_bus(uint16_t address) {
  uint8_t hi = address >> 8;
  uint8_t lo = address & 0xff;

  digitalWrite(LATCH, LOW);

  shiftOut(DATA, CLOCK, LSBFIRST, lo);
  shiftOut(DATA, CLOCK, LSBFIRST, hi);

  digitalWrite(LATCH, HIGH);
}

// Output Enable, LOW active
void set_oe(uint8_t state) {
  digitalWrite(OE, state);
}

// Chip Enable, LOW active
void set_ce(uint8_t state) {
  digitalWrite(CE, state);
}

// Write Enable, LOW active
void set_we(uint8_t state) {
  digitalWrite(WE, state);
}

uint8_t read_byte(uint16_t address) {
  data_bus_input();

  set_oe(HIGH); // Disable Output
  set_ce(LOW); // Enable Chip Select
  set_we(HIGH); // Disable Write

  set_address_bus(address); // Set Address

  set_oe(LOW); // Enable Output
  delay(1);
  uint8_t data = read_data_bus();
  set_oe(HIGH); // Disable Output

  delay(1);
  return data;
}

void write_byte(uint16_t address, uint8_t data) {
  set_oe(HIGH); // Disable Output
  set_we(HIGH); // Disable Write

  set_address_bus(address); // Set Address

  data_bus_output();
  write_data_bus(data);

  set_ce(LOW); // Enable Chip Select

  // Perform Write
  delayMicroseconds(20);
  set_we(LOW); // Enable Write
  delayMicroseconds(20);
  set_we(HIGH); // Disable Write

  // Wait until data is correct
  data_bus_input();
  set_oe(LOW); // Enable Output
  while (data != read_data_bus()) { }

  set_oe(HIGH); // Disable Output
  set_ce(HIGH); // Disable Chip Select

  delay(3);
}

// Input / Output

void read_block(uint16_t from, uint16_t to, uint16_t linelength) {
  uint16_t count = 0;
  for (uint16_t address = from; address <= to; address++) {
    if (count == 0) {
      Serial.println();
      Serial.print("0x");
      printAddress(address);
      Serial.print(" : ");
    }

    uint8_t data = read_byte(address);
    printByte(data);
    Serial.print(" ");
    count = (++count % linelength);
  }
  Serial.println();
}

void read_binblock(uint16_t from, uint16_t to) {
  for (uint16_t address = from; address <= to; address++) {
    Serial.write(read_byte(address));
  }
  Serial.print('\0');
}

void write_block(uint16_t address, uint8_t* buffer, uint16_t len) {
  for (uint16_t i = 0; i < len; i++) {
    write_byte(address+i, buffer[i]);
  }
}

void printAddress(uint16_t address) {
  if (address < 0x0010) Serial.print("0");
  if (address < 0x0100) Serial.print("0");
  if (address < 0x1000) Serial.print("0");
  Serial.print(address, HEX);
}

void printByte(uint8_t data) {
  if (data < 0x10) Serial.print("0");
  Serial.print(data, HEX);
}
