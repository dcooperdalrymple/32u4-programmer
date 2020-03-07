# 32u4 Programmer

> 32u4-based Eeprom and AVR Programmer<br />
> Created by D Cooper Dalrymple 2019 - [dcdalrymple.com](https://dcdalrymple.com/)<br />
> Licensed under GNU GPL V3.0<br />
> Last revision on November 6th, 2019

Parallel EEPROM and ATtiny13A ISP programmer with native USB support using the Atmega32u4 microcontroller. Intended for making homebrew NES & VCS cartridges with easily rewritable EEPROM for prototyping.

![Breadboard Prototype](/assets/breadboard-prototype.jpg)

## Supported ICs

### EEPROM

Intended for use with Atmel AT28Cxxx ICs, but other pin-compatible chips might work as well.

- Atmel AT28C16 _16Kb (2K x 8)_
- Atmel AT28C64 _64Kb (8K x 8)_
- Atmel AT28C256 _256Kb (32K x 8)_

### ISP

Intended for use with Atmel ATtiny13A for writing AVRCIC but other devices should be supported with no modifications or with jumper cables.

- Atmel ATtiny13A
- Atmel ATtiny25/45/85

## Software Utility

The software for communicating with the 32u4 is written in Python 2.7 with PySerial and wxPython for cross platform support. With the correct packages, it should work on Linux, Windows, and macOS _(currently not tested)_. You can run this program with the IDLE Python GUI or by running the command `python ./32u4-programmer.py` in the root directory of this project.

There are four main panels within the software, EEPROM, ISP, Hex, and Debug:

### EEPROM

This page presents all of the options needed to configure the programmer and its serial connection and perform the full device read and write tasks. Currently, the software only supports raw .bin and .hex files for writing the entire device's memory contents.

![Utility EEPROM Page](/assets/utility-eeprom.png)

### ISP

_The ISP software functionality is still in development._

### Hex Viewer

Whenever a hex file is imported manually, read from an EEPROM device, or written to an EEPROM by the programmer, the hex viewer is updated to display all addreses and values of the binary data. It groups addressed data into rows of 8 with a string characterization preview in the last column which is useful for reading rom header data. You cannot currently edit rom data on this page, but this feature may be implemented in the future.

![Utility Hex Viewer Page](/assets/utility-hex.png)

### Command Debugger

This page gives you the ability to send commands directly to the programmer, specify each parameter with hexadecimal notation, and display the response from the programmer if applicable. This page is mostly useful for testing address and data lines on the programmer or reading and writing small sets of data to verify an eeprom device's functionality.

![Utility Debug Page](/assets/utility-debug.png)

### Program Log

On all utility pages, the log is visible in the bottom of the software. This will display any informational, warning, error, or success messages in color coordinated fashion. This is useful for monitoring the progress of device programming.

## Programmer Hardware

At the moment, hardware development is still in the prototyping phase. You can built your own breadboard prototype by following the [Fritzing project](/hardware/prototype/32u4-programmer.fzz) wiring diagram with an Adafruit ItsyBitsy 32u4 5V microcontroller and 2 74HC595 ICs, but a more complete, alpha version of the hardware will be developed soon (and possibly distributed) based on the updated [schematic](/hardware/32u4-programmer.pdf). These KiCad project files are located in the `/32u4-programmer/hardware/` directory.

## Feature Requests

The hardware, firmware, and software for this project is still in active development. Follow this project if you would like to receive future updates or contact me at <me@dcdalrymple.com> to learn more about how you can contribute.

### Hardware

- EPROM device support (ie 27Cxxx) with Buck Boost circuit and relays
- Standalone operation after being configured by the utility software
- Automatic device hardware configuration for power and address lines
- ATtiny24/44/84 ISP support
- Complete ISP firmware

### Software

- Hex file editing and performance improvements
- NES/VCS ROM file parsing
- Global environment settings
- ISP programming

## License

This project is licensed under GNU GPL V3.0 - see the [LICENSE](LICENSE) file for details.
