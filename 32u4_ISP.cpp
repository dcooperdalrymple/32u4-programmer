/**
 * File: 32u4_ISP.cpp
 * Created: 19/10/2019
 * Updated: 01/11/2019
 */

#include "SPI.h"
#include "32u4_ISP.h"

// ISP Variables

int error = 0;
int pmode = 0;
uint16_t address;
Parameter param;

void setupISP() {
  
}
/*
void ISP_loop() {
  if (Serial.available()) {
    avrisp();
  }
}

uint8_t getch() {
  while (!Serial.available());
  return Serial.read();
}
void fill(uint16_t n) {
  for (uint16_t x = 0; x < n; x++) {
    buff[x] = getch();
  }
}

static bool rst_active_high;
void reset_target(bool reset) {
  digitalWrite(RESET, ((reset && rst_active_high) || (!reset && !rst_active_high)) ? HIGH : LOW);
}

uint8_t spi_transaction(uint8_t a, uint8_t b, uint8_t c, uint8_t d) {
  SPI.transfer(a);
  SPI.transfer(b);
  SPI.transfer(c);
  return SPI.transfer(d);
}

void empty_reply() {
  if (CRC_EOP == getch()) {
    Serial.print((char)STK_INSYNC);
    Serial.print((char)STK_OK);
  } else {
    error++;
    Serial.print((char)STK_NOSYNC);
  }
}

void breply(uint8_t b) {
  if (CRC_EOP == getch()) {
    Serial.print((char)STK_INSYNC);
    Serial.print((char)b);
    Serial.print((char)STK_OK);
  } else {
    error++;
    Serial.print((char)STK_NOSYNC);
  }
}

void get_version(uint8_t c) {
  switch (c) {
    case 0x80:
      breply(HWVER);
      break;
    case 0x81:
      breply(SWMAJ);
      break;
    case 0x82:
      breply(SWMIN);
      break;
    case 0x93:
      breply('S'); // Serial programmer
      break;
    default:
      breply(0);
      break;
  }
}

void set_parameters() {
  param.devicecode = block_buffer[0];
  param.revision = block_buffer[1];
  param.progtype = block_buffer[2];
  param.parmode = block_buffer[3];
  param.polling = block_buffer[4];
  param.selftimed = block_buffer[5];
  param.lockbytes = block_buffer[6];
  param.fusebytes = block_buffer[7];
  param.flashpoll = block_buffer[8];
  // Ignore block_buffer[9] (= block_buffer[8])
  
  // following are 16 bits (big endian)
  param.eeprompoll = beget16(&block_buffer[10]);
  param.pagesize = beget16(&block_buffer[12]);
  param.eepromsize = beget16(&block_buffer[14]);

  // 32 bits flashsize (big endian)
  param.flashsize = block_buffer[16] * 0x01000000
                  + block_buffer[17] * 0x00010000
                  + block_buffer[18] * 0x00000100
                  + block_buffer[19];

  // AVR devices have active low reset, AT89Sx are active high
  rst_active_high = (param.devicecode >= 0xe0);
}
*/
