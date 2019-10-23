#!/usr/bin/env python

import serial
import serial.tools.list_ports

class AppController:
    def __init__(self, view):
        self.view = view(self)
        self.serial = serial.Serial()

    def run(self):
        self.view.run()

    def update(self):
        self.view.update()

    def destroy(self):
        self.view.destroy()

    def getDevices(self):
        return ['AT28C16', 'AT28C256', 'AT28C040']

    def getProgrammers(self):
        choices = []

        for n, (portname, desc, hwid) in enumerate(sorted(serial.tools.list_ports.comports())):
            if self.checkProgrammer(n):
                choices.append("{} - {}".format(portname, desc))

        return choices

    def checkProgrammer(self, n):
        #self.serial.write(u'V\n')
        #read = self.serial.read(self.serial.in_waiting or 1)
        return True

    def setProgrammer(self, n):
        self.serial.port = n
        self.serial.baudrate = 115200
        #self.serial.bytesize = ...
        #self.serial.stopbits = ...
        #self.serial.parity = ...
        #self.serial.rtscts = ...
        #self.serial.xonxoff = ...
        #self.serial.timeout = .../None

        try:
            self.serial.open()
        except serial.SerialException as e:
            self.view.ShowError(str(e), "Serial Port Error")
            return False
        else:
            print "Serial port successfully opened on {} [{},{},{},{}{}{}]".format(
                self.serial.portstr,
                self.serial.baudrate,
                self.serial.bytesize,
                self.serial.parity,
                self.serial.stopbits,
                ' RTS/CTS' if self.serial.rtscts else '',
                ' Xon/Xoff' if self.serial.xonxoff else '',
            )

            return True

        return False

    def importFile(self, pathname):
        try:
            with open(pathname, 'r') as file:
                if file.mode == 'r':
                    contents = file.read()
                file.close()
        except IOError:
            wx.LogError("Cannot open data in file '%s'." % pathname)
