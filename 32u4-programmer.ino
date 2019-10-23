/**
 * Title: 32u4 Programmer
 * Author: D Cooper Dalrymple
 * Created: 20/08/2019
 * Updated: 19/10/2019
 * https://dcooperdalrymple.com/
 */

/**
 * Resources:
 * - https://github.com/rsbohn/ArduinoISP/blob/master/ArduinoISP/ArduinoISP.ino
 * - https://github.com/mkeller0815/MEEPROMMER/blob/master/Arduino/MEEPROMMERfirmware/MEEPROMMERfirmware.ino
 */

#include "Arduino.h"
#include <SoftwareSerial.h>
#include <Mouse.h>
#include <Keyboard.h>

#include "32u4_ICP.h"
#include "32u4_EEPROM.h"

// Status LED

#define STATUS      13

// Piezo Buzzer

#define PIEZO       11
#define PIEZO_NOTE  262 // C4
#define PIEZO_DUR   250 // ms

// USB Serial Comm

#define BAUDRATE    19200 //115200
#define HWVER       1
#define SWMAJ       0
#define SWMIN       1
#define VERSIONSTR  "32u4 Programmer $Revision 0.1 $ $Date: 19/10/2019 20:45:00 $, CMD:R,r,w,W,V"

#define BUFFERSIZE  1024
#define COMMANDSIZE 32

// Command Structure and Buffers

#define CMD_NONE            0
#define CMD_VERSION         1
#define CMD_VERSION_CH      'V'
#define CMD_SET_ADDRESS     2
#define CMD_SET_ADDRESS_CH  'A'

#define CMD_READ_HEX        10
#define CMD_READ_HEX_CH     'R'
#define CMD_READ_BIN        11
#define CMD_READ_BIN_CH     'r'

#define CMD_WRITE_HEX       20
#define CMD_WRITE_HEX_CH    'W'
#define CMD_WRITE_BIN       21
#define CMD_WRITE_BIN_CH    'w'

typedef struct cmd {
  uint8_t code;
  uint16_t startAddress;
  uint16_t dataLength;
  uint8_t lineLength;
} Command;

uint8_t block_buffer[BUFFERSIZE]; // Block storage
char cmd_buffer[COMMANDSIZE]; // Command line parsing buffer

// Main

void setup() {
  // Configure USB Serial
  Mouse.end();
  Serial.end();
  Serial.begin(BAUDRATE);
  while (!Serial) { };

  // Status Indicators
  pinMode(STATUS, OUTPUT);
  digitalWrite(STATUS, LOW);
  pinMode(PIEZO, OUTPUT);
  digitalWrite(PIEZO, LOW);
  
  // Setup Programmers
  setupEEPROM();
  setupICP();
}

void loop() {
  uint8_t i = 0;
  uint16_t index = 0;
  
  readCommand();
  Command command = parseCommand();

  // Filter command values
  uint16_t endAddress = command.startAddress + command.dataLength - 1;
  if (command.dataLength > BUFFERSIZE) command.dataLength = BUFFERSIZE;
  if (command.lineLength == 0) command.lineLength = 32;

  switch (command.code) {
    case CMD_VERSION:
      Serial.println(VERSIONSTR);
      break;
    case CMD_SET_ADDRESS:
      Serial.print("Setting address bus to 0x");
      printAddress(cmd_buffer + 2);
      Serial.println();
      set_address_bus(command.startAddress);
      break;
    case CMD_READ_HEX:
      read_block(command.startAddress, endAddress, command.lineLength);
      Serial.println('%');
      break;
    case CMD_READ_BIN:
      read_binblock(command.startAddress, endAddress);
      break;
    case CMD_WRITE_HEX:
      Serial.println("waiting for ");
      Serial.print(command.dataLength);
      Serial.println(" bytes");
      while (index < command.dataLength) {
        if (Serial.available()) {
          cmd_buffer[i++] = Serial.read();
          if (i >= 2) {
            block_buffer[index++] = hexByte(cmd_buffer);
            Serial.println("Received " + block_buffer[index - 1]);
            i = 0;
          }
        }
      }
      write_block(command.startAddress, block_buffer, command.dataLength);
      Serial.println('%');
      break;
    case CMD_WRITE_BIN:
      while (index < command.dataLength) {
        if (Serial.available()) {
          block_buffer[index++] = Serial.read();
        }
      }
      write_block(command.startAddress, block_buffer, command.dataLength);
      Serial.println('%');
      break;
  }
}

/*********************************
 * Command and Parsing Functions *
 *********************************/

void readCommand() {
  // Clear command buffer
  for (uint8_t i = 0; i < COMMANDSIZE; i++) cmd_buffer[i] = 0;

  char c = ' ';
  uint16_t index = 0;

  // Read serial data until linebreak or buffer is full
  do {
    if (Serial.available()) {
      c = Serial.read();
      cmd_buffer[index++] = c;
    }
  } while (c != '\n' && index < COMMANDSIZE); // Save room for termination char

  // Change last new line to '\0' termination
  cmd_buffer[index - 1] = 0;
}

Command parseCommand() {
  Command command;
  
  // Convert commas to '\0' terminator
  cmd_buffer[1] = 0; // Command character
  cmd_buffer[6] = 0; // Start address (4 bytes)
  cmd_buffer[11] = 0; // End address length (4 bytes)
  cmd_buffer[14] = 0; // Line Length (2 bytes)

  command.startAddress = hexWord(cmd_buffer + 2);
  command.dataLength = hexWord(cmd_buffer + 7);
  command.lineLength = hexByte(cmd_buffer + 12);

  switch (cmd_buffer[0]) {
    case CMD_SET_ADDRESS_CH:
      command.code = CMD_SET_ADDRESS;
      break;
    case CMD_READ_HEX_CH:
      command.code = CMD_READ_HEX;
      break;
    case CMD_READ_BIN_CH:
      command.code = CMD_READ_BIN;
      break;
    case CMD_WRITE_HEX_CH:
      command.code = CMD_WRITE_HEX;
      break;
    case CMD_WRITE_BIN_CH:
      command.code = CMD_WRITE_BIN;
      break;
    case CMD_VERSION_CH:
      command.code = CMD_VERSION;
      break;
    default:
      command.code = CMD_NONE;
      break;
  }

  return command;
}

// String hexadecimal Conversion
uint8_t hexDigit(char c) {
  if (c >= '0' && c <= '9') {
    return c - '0';
  } else if (c >= 'a' && c <= 'f') {
    return c - 'a' + 10;
  } else if (c >= 'A' && c <= 'F') {
    return c - 'A' + 10;
  } else {
    return 0; // Invalid character
  }
}
uint8_t hexByte(char* a) {
  return (hexDigit(a[0]) << 4) + hexDigit(a[1]);
}
uint16_t hexWord(char* data) {
  return (hexDigit(data[0]) << 12) +
         (hexDigit(data[1]) << 8) +
         (hexDigit(data[2]) << 4) +
          hexDigit(data[3]);
}

/*********************
 * Status Indication *
 *********************/

void doTone() {
  tone(PIEZO, PIEZO_NOTE, PIEZO_DUR);
  noTone(PIEZO);
  digitalWrite(PIEZO, LOW);
}
