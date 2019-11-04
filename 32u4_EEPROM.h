/**
 * File: 32u4_EEPROM.h
 * Created: 19/10/2019
 * Updated: 01/11/2019
 */

#ifndef H_32U4_EEPROM
#define H_32U4_EEPROM

#include <Arduino.h>

// Shift Registers

#define DATA        A2
#define LATCH       A1
#define CLOCK       A0

// EEPROM

#define D0          0
#define D1          1
#define D2          2
#define D3          3
#define D4          5
#define D5          7
#define D6          9
#define D7          10

#define CE          A3
#define OE          A4
#define WE          A5

// Function Definitions

void setupEEPROM();

void set_address_bus(uint16_t address);
void write_data_bus(uint8_t data);

uint8_t read_byte(uint16_t address);
void write_byte(uint16_t address, uint8_t data);

void read_block(uint16_t from, uint16_t to, uint16_t linelength);
void read_binblock(uint16_t from, uint16_t to);
void write_block(uint16_t address, uint8_t* buffer, uint16_t len);

void printAddress(uint16_t address);
void printByte(uint8_t data);

#endif // H_32U4_EEPROM
