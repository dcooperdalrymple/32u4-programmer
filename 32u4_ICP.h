/**
 * File: 32u4_ICP.h
 * Created: 19/10/2019
 * Updated: 19/10/2019
 */

#ifndef H_32U4_ICP
#define H_32U4_ICP

#include <Arduino.h>

// SPI ICSP

#define PIN_MOSI    MOSI
#define PIN_MISO    MISO
#define PIN_SCK     SCK
#define RESET       0

#define SPI_CLOCK   (1000000/6)

// STK Definitions

#define STK_OK      0x10
#define STK_FAILED  0x11
#define STK_UNKNOWN 0x12
#define STK_INSYNC  0x14
#define STK_NOSYNC  0x15
#define CRC_EOP     0x20

// Parameter structure

/*
#define beget16(addr) (*addr * 256 + *(addr+1))
typedef struct parameter {
  uint8_t devicecode;
  uint8_t revision;
  uint8_t progtype;
  uint8_t parmode;
  uint8_t polling;
  uint8_t selftimed;
  uint8_t lockbytes;
  uint8_t fusebytes;
  uint8_t flashpoll;
  uint16_t eeprompoll;
  uint16_t pagesize;
  uint16_t eepromsize;
  uint32_t flashsize;
} Parameter;
Parameter param;
*/

// Function Definitions

void setupICP();
void reset_target(bool reset);

#endif // H_32U4_ICP
