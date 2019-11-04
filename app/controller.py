#!/usr/bin/env python

import serial
import serial.tools.list_ports
import time

class AppController:
    def __init__(self, view):
        self.baudrate = 19200
        self.block_size = 0x0400
        self.devices = {
            "AT28C16": {
                "name": "AT28C16",
                "startAddress": 0x0000,
                "dataLength": 0x0800,
            },
            "AT28C256": {
                "name": "AT28C256",
                "startAddress": 0x0000,
                "dataLength": 0x8000
            },
        }
        self.device = False

        self.serial = serial.Serial()
        self.view = view(self)

    def run(self):
        self.view.run()

    def update(self):
        self.view.update()

    def destroy(self):
        self.view.destroy()
        self.closeProgrammer()

    def getDevices(self):
        return [str(name) for name in self.devices]

    def getDevice(self, name):
        if not name in self.devices:
            return False
        else:
            return self.devices[name]

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
        choices = []

        for n, (portname, desc, hwid) in enumerate(sorted(serial.tools.list_ports.comports())):
            if self.checkProgrammer(portname) == True:
                info = self.getInfo()
                choices.append("{} v{} [{}]".format(info['Title'], info['Software Version'], portname))

        return choices

    def checkProgrammer(self, portname):
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
        self.serial.baudrate = 19200
        self.serial.bytesize = 8
        self.serial.parity = 'N'
        self.serial.stopbits = 1
        self.serial.rtscts = False
        self.serial.xonxoff = False
        self.serial.timeout = 1

        try:
            self.serial.open()
        except serial.SerialException as e:
            self.view.LogError(str(e), "Serial Port Error")
            return False
        else:
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

        return False

    def closeProgrammer(self):
        if self.serial.is_open == True:
            self.serial.close()
            return True
        else:
            return False

    def sendCommand(self, code, startAddress = False, dataLength = False, lineLength = False):
        if len(code) < 1 or self.serial.is_open == False:
            return False

        # Build Command
        command = code[:1]
        if startAddress != False:
            if startAddress > 0xffff:
                startAddress = 0xffff
            command += ',' + "{0:0{1}x}".format(startAddress, 4)

            if dataLength != False:
                if dataLength > 0xffff:
                    dataLength = 0xffff
                command += ',' + "{0:0{1}x}".format(dataLength, 4)

                if lineLength != False:
                    if lineLength > 0xff:
                        lineLength = 0xff
                    command += ',' + "{0:0{1}x}".format(lineLength, 2)
        command += '\n'

        try:
            self.serial.write(command.encode('utf-8'))
            self.serial.flush()
        except serial.SerialException as e:
            self.view.LogError(str(e), "Serial Command Error")
            return False

        return True

    def getInfo(self):
        if self.serial.is_open == False:
            return False

        if self.sendCommand(u'V') == False:
            return False

        info_str = False
        try:
            info_str = self.serial.readline()
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

        return data

    def readBlock(self, startAddress, dataLength):
        if self.serial.is_open == False:
            return False

        if not self.sendCommand(u'r', startAddress, dataLength):
            return False

        time.sleep(0.1) # Wait for programmer to start working

#        block = []
#        while self.serial.in_waiting:
#            byte = self.serial.read(1)
#            if not byte:
#                break # Timed out
#            if byte == "\0":
#                break # End of response
#            block.append(ord(byte))

        try:
            block = self.serial.read_until("\0", dataLength)
        except serial.SerialException as e:
            self.view.LogError(str(e), "Block Read Error")
            return False

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

        error = False
        address = startAddress
        while address < endAddress:
            block_size = min(self.block_size, endAddress - address)

            relAddr = address - startAddress
            block = data[slice(relAddr, relAddr + block_size)]

            if not self.writeBlock(address, block):
                error = True
                break

        if error == True:
            self.view.LogError("Failed to write all blocks to device", "Device Write Error")
            return False

        return True

    def writeBlock(self, startAddress, data):
        if self.serial.is_open == False:
            return False

        if len(data) > self.block_size:
            return False

        if not self.sendCommand(u'w', startAddress, len(data)):
            return False

        try:
            self.serial.write(bytearray(data))
            self.serial.flush()
        except serial.SerialException as e:
            self.view.LogError(str(e), "Block Write Error")
            return False

        return True

    def writeFile(self, pathname):
        data = self.importFile(pathname)
        if data == False or not isinstance(data, list):
            self.view.LogError("Unable to read hex data from file, {}.".format(pathname))
            return False

        return self.writeDevice(data)

    def importFile(self, pathname):
        contents = False

        try:
            with open(pathname, 'r') as file:
                if file.mode == 'r':
                    contents = bytearray(file.read())
                file.close()
        except IOError:
            wx.LogError("Cannot open data in file '%s'." % pathname)

        if contents == False or not isinstance(contents, bytearray):
            return False

        return [x for x in contents]
