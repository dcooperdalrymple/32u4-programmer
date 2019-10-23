#!/usr/bin/env python

import wx
import wx.adv
import os

ABSPATH = os.path.dirname(os.path.abspath(__file__))
if ABSPATH.endswith('app'):
    ABSPATH = ABSPATH[:-3]

class AppView():

    def __init__(self, controller):
        self.controller = controller

        self.app = wx.App(False)

        frameStyle = wx.MINIMIZE_BOX | wx.MAXIMIZE_BOX | wx.RESIZE_BORDER | wx.SYSTEM_MENU | wx.CAPTION | wx.CLOSE_BOX | wx.CLIP_CHILDREN;
        self.frame = AppFrame(controller, None, -1, title = '32u4 Programmer Utility', size = (480, 360), style = frameStyle)

    def run(self):
        self.frame.Show()
        self.app.MainLoop()

    def update(self):
        return

    def _destroy(self, event):
        return

    def destroy(self):
        self.frame.Close()

    def ShowError(self, message, title="Error"):
        with wx.MessageDialog(self, message, title, wx.OK | wx.ICON_ERROR) as dialog:
            dialog.ShowModal()

class AppFrame(wx.Frame):

    def __init__(self, controller, *args, **kw):
        super(AppFrame, self).__init__(*args, **kw)
        self.controller = controller

        self.SetMinSize(self.GetSize())

        self.panel = wx.Panel(self)

        self.createPanels()

        self.createMenuBar()

        self.CreateStatusBar()
        self.SetStatusText("32u4 Programmer Utility")

        self.Centre()

    def createPanels(self):
        self.notebook = wx.Notebook(self.panel)

        self.eepromPanel = EepromPanel(self.notebook, self.controller)
        self.microPanel = MicroPanel(self.notebook, self.controller)

        self.notebook.AddPage(self.eepromPanel, self.eepromPanel.getTitle())
        self.notebook.AddPage(self.microPanel, self.microPanel.getTitle())

        sizer = wx.BoxSizer()
        sizer.Add(self.notebook, 1, wx.EXPAND)
        self.panel.SetSizer(sizer)

    def createMenuBar(self):
        fileMenu = wx.Menu()
        importItem = fileMenu.Append(-1, "&Import Hex File...\tCtrl-I", "Select a file to program to EEPROM or Microcontroller")
        fileMenu.AppendSeparator()
        exitItem = fileMenu.Append(wx.ID_EXIT)

        helpMenu = wx.Menu()
        aboutItem = helpMenu.Append(wx.ID_ABOUT)

        menuBar = wx.MenuBar()
        menuBar.Append(fileMenu, "&File")
        menuBar.Append(helpMenu, "&Help")

        self.SetMenuBar(menuBar)

        self.Bind(wx.EVT_MENU, self.OnImport, importItem)
        self.Bind(wx.EVT_MENU, self.OnExit,  exitItem)
        self.Bind(wx.EVT_MENU, self.OnAbout, aboutItem)

    def OnExit(self, event):
        self.Close(True)

    def OnImport(self, event):
        with wx.FileDialog(self, "Choose Hex file",
            wildcard="Hex files (*.hex;*.bin)|*.hex;*.bin",
            style=wx.FD_OPEN | wx.FD_FILE_MUST_EXIST) as fileDialog:

            if fileDialog.ShowModal() == wx.ID_CANCEL:
                return

            pathname = fileDialog.GetPath()
            self.controller.importFile(pathname)

    def OnAbout(self, event):
        self.showAboutDialog()

        #wx.MessageBox(self.getAboutMessage(), caption = "About 32u4 Programmer", style = wx.OK | wx.ICON_INFORMATION | wx.CENTRE)

    def showAboutDialog(self):
        global ABSPATH

        info = wx.adv.AboutDialogInfo()

        info.SetName("32u4 Programmer Utility")
        info.SetVersion("Version 0.1.0")
        info.SetCopyright("(c) 2019 D Cooper Dalrymple <me@dcdalrymple.com>")
        info.SetDescription(self.getAboutMessage())
        info.SetWebSite("https://github.com/dcooperdalrymple/32u4-programmer/", "32u4 Programmer Github Project")
        info.AddDeveloper("D Cooper Dalrymple")

        icon_path = ABSPATH + "assets/icon.png"
        if os.name == 'nt':
            icon_path = ABSPATH + "assets\\icon.png"
        info.SetIcon(wx.Icon(icon_path, type = wx.BITMAP_TYPE_PNG))

        with open(ABSPATH + "LICENSE", 'r') as file:
            if file.mode == 'r':
                info.License = file.read()
            file.close()

        wx.adv.AboutBox(info)

    def getAboutMessage(self):
        return "In conjunction with a 32u4 Programmer or other MEEPROMMER compatible device, you can use this utility to write hex files to a 28C series EEPROM or ATtiny series microcontroller.\n\nThis program is intended to aid in the production of 8-bit homebrew games on the NES and VCS."

class EepromPanel(wx.Panel):

    def __init__(self, parent, controller):
        wx.Panel.__init__(self, parent)
        self.controller = controller

        self.gridPanel = wx.Panel(self)
        self.grid = wx.GridSizer(rows=1, cols=2, hgap=16, vgap=16)

        self.createDeviceSelector()
        self.createProgrammerSelector()

        self.gridPanel.SetSizer(self.grid)

        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(self.gridPanel, wx.ID_ANY, wx.EXPAND | wx.ALL, 16)
        self.SetSizer(sizer)

    def getTitle(self):
        return "EEPROM"

    def createDeviceSelector(self):
        self.deviceList = wx.RadioBox(self.gridPanel, label = 'Device', choices = self.controller.getDevices(),
            majorDimension = 1, style = wx.RA_SPECIFY_COLS)
        self.deviceList.Bind(wx.EVT_RADIOBOX, self.onDeviceSelect)

        self.grid.Add(self.deviceList, wx.ID_ANY, wx.EXPAND)

    def createProgrammerSelector(self):
        self.programmerList = wx.RadioBox(self.gridPanel, label = 'Programmer', choices = self.controller.getProgrammers(),
            majorDimension = 1, style = wx.RA_SPECIFY_COLS)
        self.programmerList.Bind(wx.EVT_RADIOBOX, self.onProgrammerSelect)

        self.grid.Add(self.programmerList, wx.ID_ANY, wx.EXPAND)

    def onDeviceSelect(self, e):
        print self.deviceList.GetStringSelection(),' is selected'

    def onProgrammerSelect(self, e):
        print self.programmerList.GetStringSelection(),' is selected'

class MicroPanel(wx.Panel):

    def __init__(self, parent, controller):
        wx.Panel.__init__(self, parent)
        self.controller = controller

        t = wx.StaticText(self, wx.ID_ANY, "This is the microcontroller tab.", (20, 20))

    def getTitle(self):
        return "Microcontroller"
