#!/usr/bin/env python

import serial
import serial.tools.list_ports
import time
import math
import os

class AppController:
    def __init__(self, view):
        self.default_timeout = 0.25
        self.block_timeout = 10
        self.block_size = 0x0400
        self.write_cycles = 3

        self.devices = {
            "AT28C16": {
                "name": "AT28C16",
                "startAddress": 0x0000,
                "dataLength": 0x0800,
            },
            "AT28C256": {
                "name": "AT28C256",
                "startAddress": 0x0000,
                "dataLength": 0x8000,
            },
        }
        self.device = False

        self.commands = {
            "V": {
                "code": "V",
                "title": "Version",
                "description": "",
                "address": False,
                "dataLength": False,
                "lineLength": False,
                "input": False,
                "return": "\n",
            },
            "A": {
                "code": "A",
                "title": "Set Address",
                "description": "",
                "address": True,
                "dataLength": False,
                "lineLength": False,
                "input": False,
                "return": False,
            },
            "D": {
                "code": "D",
                "title": "Set Data",
                "description": "",
                "address": True,
                "dataLength": False,
                "lineLength": False,
                "input": False,
                "return": False,
            },
            "T": {
                "code": "T",
                "title": "Play Tone",
                "description": "Uses the programmer's piezo speaker to play a tone to indicate process completion.",
                "address": False,
                "dataLength": False,
                "lineLength": False,
                "input": False,
                "return": False,
            },
            "R": {
                "code": "R",
                "title": "Read Hexadecimal",
                "description": "",
                "address": True,
                "dataLength": True,
                "lineLength": True,
                "input": False,
                "return": "lineLength",
            },
#            "r": {
#                "code": "r",
#                "title": "Read Binary",
#                "description": "",
#                "address": True,
#                "dataLength": True,
#                "lineLength": False,
#                "input": False,
#                "return": "\0",
#            },
            "W": {
                "code": "W",
                "title": "Write Hexadecimal",
                "description": "",
                "address": True,
                "dataLength": True,
                "lineLength": False,
                "input": "dataLength",
                "return": "%",
            },
#            "w": {
#                "code": "w",
#                "title": "Write Binary",
#                "description": "",
#                "address": True,
#                "dataLength": True,
#                "lineLength": False,
#                "input": "dataLength",
#                "return": "%",
#            },
        }

        self.serial = serial.Serial(
            baudrate = 19200,
            bytesize = 8,
            parity = 'N',
            stopbits = 1,
            rtscts = False,
            xonxoff = False,
            timeout = self.default_timeout,
            write_timeout = self.default_timeout
        )

        self.view = view(self)

    def run(self):
        self.view.run()

    def update(self):
        self.view.update()

    def destroy(self):
        self.closeProgrammer()
        self.view.destroy()

    def getDevices(self):
        return [str(name) for name in self.devices]

    def getDevice(self, name):
        if not name in self.devices:
            return False
        else:
            return self.devices[name]

    def getCommands(self):
        choices = []
        for command in self.commands:
            choices.append("{} [{}]".format(self.commands[command]["title"], self.commands[command]["code"]))
        return choices

    def getCommand(self, command):
        if not command in self.commands:
            return False
        else:
            return self.commands[command]

    def setDevice(self, name):
        if not name in self.devices:
            self.device = False
            self.view.LogWarning("Device does not exist in database")
            return False
        else:
            self.device = name
            self.view.LogSuccess('Programmer configured to use ' + self.devices[name]["name"])
            return self.devices[name]

    def getProgrammers(self):
        self.view.Log("Querying serial COM ports for programming devices.")

        choices = []
        for n, (portname, desc, hwid) in enumerate(sorted(serial.tools.list_ports.comports())):
            if self.checkProgrammer(portname) == True:
                info = self.getInfo()
                choices.append("{} v{} [{}]".format(info['Title'], info['Software Version'], portname))

        plural = ""
        if len(choices) > 1: plural = "s"

        self.view.Log("Done querying COM ports. {} device{} found.".format(len(choices), plural))
        return choices

    def checkProgrammer(self, portname):
        self.view.Log("Checking device on {}.".format(portname))

        if self.setProgrammer(portname) == False:
            return False

        info = self.getInfo()

        if info != False and len(info) > 0 and info['Title'] == '32u4 Programmer':
            self.view.LogSuccess("Successfully identified programmer on {}".format(portname))
            return True
        else:
            self.view.LogWarning("Invalid device on {}".format(portname))
            return False

    def setProgrammer(self, portname):
        self.closeProgrammer()

        self.serial.port = portname
        try:
            self.serial.open()
        except serial.SerialException as e:
            self.view.LogError(str(e), "Serial Port Error")
            return False

        self.view.LogSuccess("Serial port successfully opened on {} [{},{},{},{}{}{}]".format(
            self.serial.portstr,
            self.serial.baudrate,
            self.serial.bytesize,
            self.serial.parity,
            self.serial.stopbits,
            ' RTS/CTS' if self.serial.rtscts else '',
            ' Xon/Xoff' if self.serial.xonxoff else '',
        ))

        return True

    def closeProgrammer(self):
        if self.serial.is_open == True:
            self.serial.close()
            return True
        else:
            return False

    def sendCommand(self, code, startAddress = None, dataLength = None, lineLength = None):
        if len(code) < 1 or self.serial.is_open == False:
            return False

        # Build Command
        command = code[:1]
        if startAddress is not None:
            if startAddress > 0xffff:
                startAddress = 0xffff
            command += ',' + "{0:0{1}x}".format(startAddress, 4)

            if dataLength is not None:
                if dataLength > 0xffff:
                    dataLength = 0xffff
                command += ',' + "{0:0{1}x}".format(dataLength, 4)

                if lineLength is not None:
                    if lineLength > 0xff:
                        lineLength = 0xff
                    command += ',' + "{0:0{1}x}".format(lineLength, 2)
        command += '\n'

        try:
            command = command.encode('utf-8')
        except UnicodeEncodeError:
            self.view.LogError("Failed to encode data as UTF-8.", "Serial Command Error")
            return False

        self.view.Log("Sending Command: {}".format(command[:-1]))
        try:
            self.serial.write(command)
            self.serial.flush()
        except serial.SerialException as e:
            self.view.LogError(str(e), "Serial Command Error")
            return False

        return True

    def readCommand(self, commandInfo, dataLength = None, lineLength = None):
        if commandInfo["return"] == False:
            return False

        if isinstance(commandInfo["return"], str):
            read = False

            if len(commandInfo["return"]) == 1:
                self.serial.timeout = self.block_timeout
                try:
                    read = str(self.serial.read_until(commandInfo["return"]))
                except serial.SerialException as e:
                    self.view.LogError(str(e), "Command Read Error")
                    self.serial.timeout = self.default_timeout
                    return False

            elif commandInfo["return"] == "lineLength":
                if dataLength is None or not isinstance(dataLength, int) or dataLength <= 0 or lineLength is None or not isinstance(lineLength, int) or lineLength <= 0:
                    return False

                lines = int(math.ceil(float(dataLength) / float(lineLength)))

                read = ""
                self.serial.timeout = self.block_timeout
                try:
                    for line in range(lines):
                        read += str(self.serial.read_until('\n')) + '\n'
                except serial.SerialException as e:
                    self.view.LogError(str(e), "Command Read Error")
                    self.serial.timeout = self.default_timeout
                    return False

            elif commandInfo["return"] == "dataLength":
                if dataLength is None or not isinstance(dataLength, int) or dataLength <= 0:
                    return False

                self.serial.timeout = self.block_timeout
                try:
                    read = str(self.serial.read(dataLength))
                    terminator = self.serial.read(1)
                except serial.SerialException as e:
                    self.view.LogError(str(e), "Command Read Error")
                    self.serial.timeout = self.default_timeout
                    return False

            self.serial.timeout = self.default_timeout
            if read == False or len(read) <= 0:
                return False
            else:
                return read

        return False

    def getInfo(self):
        if self.serial.is_open == False:
            return False

        if self.sendCommand(u'V') == False:
            return False

        info_str = False
        try:
            info_str = str(self.serial.read_until('\n'))
        except serial.SerialException as e:
            self.view.LogError(str(e), "Serial Read Error")
            return False
        if info_str == False or len(info_str) <= 0 or '$' in info_str == False:
            return False

        info_arr = info_str.split("$")
        info_data = {}
        for info_line_str in info_arr:
            if len(info_line_str) <= 1 or ':' in info_line_str == False:
                continue

            info_line_arr = info_line_str.split(':')
            if len(info_line_arr) < 2:
                continue

            info_data[info_line_arr[0].strip()] = info_line_arr[1].strip()

        return info_data

    def playTone(self):
        return self.serial.is_open != False and self.sendCommand(u'T') != False

    def readDevice(self):
        if not self.device or not self.device in self.devices:
            self.view.LogError("Device not selected.", "Device Read Error")
            return False

        if self.serial.is_open == False:
            self.view.LogError("Programmer not connected.", "Device Read Error")
            return False

        startAddress = self.devices[self.device]["startAddress"]
        dataLength = self.devices[self.device]["dataLength"]
        endAddress = dataLength + startAddress

        data = []
        address = startAddress
        while address < endAddress:
            block_size = min(self.block_size, endAddress - address)

            block = self.readBlock(address, block_size)
            if block == False or len(block) <= 0:
                break

            data = data + block
            address += block_size

        if len(data) != dataLength:
            self.view.LogError("Failed to read all {} bytes from ROM. Only received {}.".format(dataLength, len(data)), "Device Read Error")
            return False

        self.playTone() # Play tone on programmer to indicate read completion
        return data

    def readBlock(self, startAddress, dataLength):
        if self.serial.is_open == False:
            return False

        if not self.sendCommand(u'r', startAddress, dataLength):
            return False

        time.sleep(0.1) # Wait for programmer to start working

        self.serial.timeout = self.block_timeout
        try:
            block = self.serial.read(dataLength)
            terminator = self.serial.read(1)
        except serial.SerialException as e:
            self.view.LogError(str(e), "Block Read Error")
            self.serial.timeout = self.default_timeout
            return False
        self.serial.timeout = self.default_timeout

        # Convert bytes to array of ints
        block = [ord(x) for x in block]

        return block

    def writeDevice(self, data):
        if not self.device or not self.device in self.devices:
            self.view.LogError("Device not selected.", "Device Write Error")
            return False

        if self.serial.is_open == False:
            self.view.LogError("Programmer not connected.", "Device Write Error")
            return False

        startAddress = self.devices[self.device]["startAddress"]
        dataLength = self.devices[self.device]["dataLength"]
        endAddress = dataLength + startAddress

        if len(data) != dataLength:
            self.view.LogError("ROM data not the appropriate length for device. Must be {} bytes.".format(dataLength), "Device Write Error")
            return False


        # Write data and verify results for a number of write cycles until device is fully written
        cycle = 0
        verified = False
        error = False
        while error == False and verified == False and cycle < self.write_cycles:

            # Write blocks
            address = startAddress
            while address < endAddress:
                block_size = min(self.block_size, endAddress - address)

                relAddr = address - startAddress
                block = data[slice(relAddr, relAddr + block_size)]

                if not self.writeBlock(address, block):
                    error = True
                    break

                address += block_size

            if error == True:
                break

            # Verify data
            readData = self.readDevice()
            if self.compareData(data, readData) == True:
                verified = True
                break

            cycle += 1

        if error == True:
            self.view.LogError("Failed to write all blocks to device.", "Device Write Error")
            return False

        if verified == False:
            self.view.LogError("Unable to verify data was written to Eeprom device.", "Device Write Error")
            return False

        self.playTone() # Play tone on programmer to indicate write completion
        return True

    def writeBlock(self, startAddress, data):
        if self.serial.is_open == False:
            return False

        if len(data) > self.block_size:
            return False

        if not self.sendCommand(u'w', startAddress, len(data)):
            return False

        self.view.Log("Writing {} bytes to programmer starting at {}.".format(len(data), "0x{0:0{1}x}".format(startAddress, 4)))

        self.serial.timeout = self.block_timeout
        try:
            # Write Data
            self.serial.write(bytearray(data))
            self.serial.flush()

            # Wait for completion
            self.serial.read_until('%')
            self.serial.reset_input_buffer() # Clears newline

        except serial.SerialException as e:
            self.serial.timeout = self.default_timeout
            self.view.LogError(str(e), "Block Write Error")
            return False
        self.serial.timeout = self.default_timeout

        return True

    def writeString(self, data):
        if self.serial.is_open == False:
            return False

        self.view.Log("Writing {} bytes to programmer.".format(len(data)))

        try:
            data = data.encode('utf-8')
        except UnicodeEncodeError:
            self.view.LogError("Failed to encode data as UTF-8.", "Serial Write Error")
            return False

        try:
            # Write Data
            self.serial.write(data)
            self.serial.flush()
        except serial.SerialException as e:
            self.view.LogError(str(e), "Serial Write Error")
            return False

        return True

    def writeFile(self, pathname):
        data = self.importFile(pathname)
        if data == False or not isinstance(data, list):
            self.view.LogError("Unable to read hex data from file, {}.".format(pathname))
            return False

        return self.writeDevice(data)

    def compareData(self, a, b):
        if not isinstance(a, list) or not isinstance(b, list):
            return False

        if len(a) != len(b):
            return False

        diff = 0
        for i, val in enumerate(a):
            if val != b[i]:
                diff += 1

        return diff == 0

    def importFile(self, pathname):
        self.view.Log("Reading contents of binary file, {}.".format(pathname))

        contents = False
        try:
            with open(pathname, 'rb') as file:
                if file.mode == 'rb':
                    contents = bytearray(file.read())
                file.close()
        except IOError:
            wx.LogError("Cannot open data in file '%s'." % pathname)

        if contents == False or not isinstance(contents, bytearray):
            return False

        return [x for x in contents]

    def exportFile(self, pathname, data):
        self.view.Log("Writing data with {} bytes to binary file, {}.".format(len(data), pathname))

        try:
            with open(pathname, 'wb') as file:
                if file.mode == 'wb':
                    file.write(bytearray(data))
                file.close()
        except IOError:
            self.view.LogError("Unable to save data to hex file, {}.".format(pathname))
