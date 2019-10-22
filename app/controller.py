#!/usr/bin/env python

class AppController:
    def __init__(self, view):
        self.view = view(self)

    def run(self):
        self.view.run()

    def update(self):
        self.view.update()

    def destroy(self):
        self.view.destroy()

    def getDevices(self):
        return ['AT28C16', 'AT28C256', 'AT28C040']

    def getProgrammers(self):
        return ['COM0', 'COM1', 'COM2']

    def importFile(self, pathname):
        try:
            with open(pathname, 'r') as file:
                if file.mode == 'r':
                    contents = file.read()
                file.close()
        except IOError:
            wx.LogError("Cannot open data in file '%s'." % pathname)
