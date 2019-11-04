# 32u4 Programmer
Parallel EEPROM and ATtiny13A ISP programmer with native USB support using the Atmega32u4 microcontroller. Intended for making homebrew NES & VCS cartridges with easily rewritable EEPROM for prototyping.

![Breadboard Prototype](/assets/breadboard-prototype.jpg)

## Supported ICs

### EEPROM

Intended for use with Atmel AT28Cxxx ICs, but other pin-compatible chips might work as well.

- Atmel AT28C16 _16Kb (2K x 8)_
- Atmel AT28C256 _256Kb (32K x 8)_

### ISP

Intended for use with Atmel ATtiny13A for writing AVRCIC but other devices should be supported with no modifications or with jumper cables.

- Atmel ATtiny13A
- Atmel ATtiny25/45/85

Atmel ATtiny24/44/84 chips are not supported, _yet_.

## Programming Utility

The software for communicating with the 32u4 is written in Python 2.7 with PySerial and wxPython for cross platform support. With the correct packages, it should work on Linux, Windows, and macOS _(currently not tested)_. There are three main panels within the software, EEPROM, ISP, and Hex.

### EEPROM

This page presents all of the options needed to configure the programmer and its serial connection and perform the full device read and write tasks. Currently, the software only supports raw .bin and .hex files for writing the entire device's memory contents.

![Utility EEPROM Page](/assets/utility-eeprom.png)

### ISP

_The ISP functionality is still in development._

### Hex Viewer

Whenever a hex file is imported manually, read from an EEPROM device, or written to an EEPROM by the programmer, the hex viewer is updated to display all addreses and values of the binary data. It groups addressed data into rows of 8 with a string characterization preview in the last column which is useful for reading rom header data. You cannot currently edit rom data on this page, but this feature may be implemented in the future.

![Utility Hex Viewer Page](/assets/utility-hex.png)

### Debug Log

On all utility pages, the debug log is visible in the bottom of the software. This will display any informational, warning, error, or success messages in color coordinated fashion. This is useful for monitoring the progress of device programming.

## Possible Future Updates

- Support for EPROM devices (ie 27Cxxx) with Buck Boost circuit and relays for high-voltage programmer.
- LEDs and button to display and select EEPROM chip mode.
- Improved EEPROM power delivery for smaller ICs.
- SPDT switch to select between 32u4 and external on AVR ISP programmer. Maybe jumper pads as well?
- Hex file editing and performance improvements
- Debug page for sending specific commands to programmer.
- NES/VCS ROM file parsing.
