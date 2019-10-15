# 32u4 Programmer
EEPROM and ATtiny13A ISP programmer with native USB support using the Atmega32u4 microcontroller. Intended for making homebrew NES & VCS cartridges with easily rewritable EEPROM for prototyping.

## Supported ICs

### EEPROM

Intended for use with Atmel AT28Cxxx ICs, but other pin-compatible chips might work as well.

- Atmel AT28C16 _16Kb (2K x 8)_
- Atmel AT28C256 _256Kb (32K x 8)_
- Atmel AT28C040 _4Mb (512K x 8)_

### ISP

Intended for use with Atmel ATtiny13A for writing AVRCIC but other devices should be supported with no modifications or with jumper cables.

- Atmel ATtiny13A
- Atmel ATtiny25/45/85

Atmel ATtiny24/44/84 chips are not supported, _yet_.

## Operating Functionality

### Tethered COMP Mode

_In development._

### Untethered PRGM Mode

_In development._

## Possible Future Updates

- Support for EPROM devices (ie 27Cxxx) with Buck Boost circuit and relays for high-voltage programmer.
- LEDs and button to display and select EEPROM chip mode.
- Improved EEPROM power delivery for smaller ICs.
- SPDT switch to select between 32u4 and external on AVR ISP programmer. Maybe jumper pads as well?
