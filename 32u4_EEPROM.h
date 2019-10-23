/**
 * File: 32u4_EEPROM.h
 * Created: 19/10/2019
 * Updated: 19/10/2019
 */

#ifndef H_32U4_EEPROM
#define H_32U4_EEPROM

#include <Arduino.h>

// Shift Registers

#define DATA        A5
#define LATCH       A4
#define CLOCK       A3

// EEPROM

#define D0          1
#define D1          2
#define D2          3
#define D3          5
#define D4          7
#define D5          9
#define D6          10
#define D7          12

#define CE          A2
#define OE          A1
#define WE          A0

// Function Definitions

void setupEEPROM();

void set_address_bus(uint16_t address);

uint8_t read_byte(uint16_t address);
void write_byte(uint16_t address, uint8_t data);

void read_block(uint16_t from, uint16_t to, uint16_t linelength);
void read_binblock(uint16_t from, uint16_t to);
void write_block(uint16_t address, uint8_t* buffer, uint16_t len);

void printAddress(uint16_t address);
void printByte(uint8_t data);

#endif // H_32U4_EEPROM
