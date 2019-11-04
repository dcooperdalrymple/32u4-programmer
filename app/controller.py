#!/usr/bin/env python

import serial
import serial.tools.list_ports

class AppController:
    def __init__(self, view):
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
        return ['AT28C16', 'AT28C256', 'AT28C040']

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

    def readChip(self):
        # Iterate through 1024 byte blocks
        return False

    def readBlock(self):
        return False

    def writeChip(self):
        # Write hex file to chip in 1024 byte blocks
        return False

    def writeBlock(self):
        return False

    def importFile(self, pathname):
        try:
            with open(pathname, 'r') as file:
                if file.mode == 'r':
                    contents = file.read()
                file.close()
        except IOError:
            wx.LogError("Cannot open data in file '%s'." % pathname)
