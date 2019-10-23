/**
 * File: 32u4_ICP.cpp
 * Created: 19/10/2019
 * Updated: 19/10/2019
 */

#include "SPI.h"
#include "32u4_ICP.h"

void setupICP() {
  
}

static bool rst_active_high;
void reset_target(bool reset) {
  digitalWrite(RESET, ((reset && rst_active_high) || (!reset && !rst_active_high)) ? HIGH : LOW);
}
