/**
 * Title: 32u4 Programmer
 * Author: D Cooper Dalrymple
 * Created: 20/08/2019
 * Updated: 01/11/2019
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

#include "32u4_ISP.h"
#include "32u4_EEPROM.h"

#define DEBUG

// Status LED

#define STATUS      13

// Piezo Buzzer

#define PIEZO       11
#define PIEZO_NOTE  262 // C4
#define PIEZO_DUR   250 // ms

// USB Serial Comm

#define BAUDRATE    19200 //115200
#define INFO_TITLE  "32u4 Programmer"
#define INFO_HWMAJ  "0"
#define INFO_HWMIN  "1"
#define INFO_SWMAJ  "0"
#define INFO_SWMIN  "1"
#define INFO_DATE   "03/11/2019 12:16:00"
#define INFO_STR    "Title: " INFO_TITLE "$Hardware Version: " INFO_HWMAJ "." INFO_HWMIN "$Software Version: " INFO_SWMAJ "." INFO_SWMIN "$Date: " INFO_DATE

#define BUFFERSIZE  1024
#define COMMANDSIZE 32

// Command Structure and Buffers

#define CMD_NONE            0
#define CMD_VERSION         1
#define CMD_VERSION_CH      'V'
#define CMD_SET_ADDRESS     2
#define CMD_SET_ADDRESS_CH  'A'
#define CMD_SET_DATA        3
#define CMD_SET_DATA_CH     'D'
#define CMD_TONE            9
#define CMD_TONE_CH         'T'

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
  setupISP();
}

void loop() {
  uint8_t i = 0;
  uint16_t index = 0;

  // Wait for command to come in
  readCommand();
  setStatus(HIGH);
  
  Command command = parseCommand();

  // Filter command values
  uint16_t endAddress = command.startAddress + command.dataLength - 1;
  if (command.dataLength > BUFFERSIZE) command.dataLength = BUFFERSIZE;
  if (command.lineLength == 0) command.lineLength = 32;

  switch (command.code) {
    case CMD_VERSION:
      Serial.println(INFO_STR);
      break;
    case CMD_TONE:
      doTone();
      break;
    case CMD_SET_ADDRESS:
      #ifdef DEBUG
      Serial.print("Setting address bus to 0x");
      printAddress(command.startAddress);
      Serial.println();
      #endif
      set_address_bus(command.startAddress);
      break;
    case CMD_SET_DATA:
      #ifdef DEBUG
      Serial.print("Setting data bus to 0x");
      printByte(command.startAddress & 0x00FF);
      Serial.println();
      #endif
      write_data_bus(command.startAddress & 0x00FF);
      break;
    case CMD_READ_HEX:
      read_block(command.startAddress, endAddress, command.lineLength);
      Serial.println('%');
      break;
    case CMD_READ_BIN:
      read_binblock(command.startAddress, endAddress);
      break;
    case CMD_WRITE_HEX:
      #ifdef DEBUG
      Serial.println("Waiting for ");
      Serial.print(command.dataLength);
      Serial.println(" bytes");
      #endif
      while (index / 2 < command.dataLength) {
        if (Serial.available()) {
          cmd_buffer[index++] = Serial.read();
        }
      }
      
      #ifdef DEBUG
      index = 0;
      Serial.print("Received ");
      while (index / 2 < command.dataLength) {
        Serial.print(cmd_buffer[index++]);
      }
      Serial.println();
      #endif
      
      index = 0;
      while (index < command.dataLength) {
        block_buffer[index] = hexByte(cmd_buffer + (index * 2));
        index++;
      }

      #ifdef DEBUG
      index = 0;
      Serial.print("Interpretted ");
      while (index < command.dataLength) {
        printByte(block_buffer[index++]);
      }
      Serial.println();
      #endif
      
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

  setStatus(LOW);
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
    case CMD_SET_DATA_CH:
      command.code = CMD_SET_DATA;
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
    case CMD_TONE_CH:
      command.code = CMD_TONE;
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

void setStatus(uint8_t state) {
  digitalWrite(STATUS, state);
}

void doTone() {
  tone(PIEZO, PIEZO_NOTE);
  delay(PIEZO_DUR);
  noTone(PIEZO);
  digitalWrite(PIEZO, LOW);
}
