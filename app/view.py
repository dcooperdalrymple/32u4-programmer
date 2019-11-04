#!/usr/bin/env python

import threading
import wx
import wx.grid
import wx.adv
import os
import re
import math

ABSPATH = os.path.dirname(os.path.abspath(__file__))
if ABSPATH.endswith('app'):
    ABSPATH = ABSPATH[:-3]

class AppView():

    def __init__(self, controller):
        self.controller = controller
        self.app = wx.App(False)

        self.frameStyle = wx.MINIMIZE_BOX | wx.MAXIMIZE_BOX | wx.RESIZE_BORDER | wx.SYSTEM_MENU | wx.CAPTION | wx.CLOSE_BOX | wx.CLIP_CHILDREN;

    def run(self):
        self.frame = AppFrame(self, self.controller, None, -1, title = '32u4 Programmer Utility', size = (480, 360), style = self.frameStyle)
        self.frame.Show()
        wx.CallAfter(self.OnLoad)

        self.app.MainLoop()

    def OnLoad(self):
        self.refresh()

    def refresh(self):
        thread = threading.Thread(target=self.frame.refresh)
        thread.start()

    def update(self):
        return

    def _destroy(self, event):
        return

    def destroy(self):
        self.frame.Destroy()

    def ShowErrorDialog(self, message, title="Error"):
        with wx.MessageDialog(self.frame, message, title, wx.OK | wx.ICON_ERROR) as dialog:
            dialog.ShowModal()

    def Log(self, message, color = (108, 117, 125)):
        start = len(self.frame.log.GetValue())
        self.frame.log.AppendText(message + '\n')
        self.frame.log.SetStyle(start, len(self.frame.log.GetValue()), wx.TextAttr(color))
        return True

    def LogError(self, message, title = "Error"):
        return self.Log(title + ": " + message, (220, 53, 69))

    def LogWarning(self, message, title = "Warning"):
        return self.Log(title + ": " + message, (255, 193, 7))

    def LogSuccess(self, message):
        return self.Log(message, (40, 167, 69))

class AppFrame(wx.Frame):

    def __init__(self, view, controller, *args, **kw):
        super(AppFrame, self).__init__(*args, **kw)

        self.view = view
        self.controller = controller

        self.SetMinSize(self.GetSize())

        self.panel = wx.Panel(self)

        self.sizer = wx.BoxSizer(wx.VERTICAL)
        self.createPanels()
        self.createLog()
        self.panel.SetSizer(self.sizer)

        self.createMenuBar()

        self.CreateStatusBar()
        self.SetStatusText("32u4 Programmer Utility")

        self.Centre()

        self.Bind(wx.EVT_CLOSE, self.OnClose)

    def createPanels(self):
        self.notebook = wx.Notebook(self.panel)

        self.eepromPanel = EepromPanel(self.notebook, self.view, self.controller)
        self.microPanel = MicroPanel(self.notebook, self.view, self.controller)
        self.hexPanel = HexPanel(self.notebook, self.view, self.controller)

        self.notebook.AddPage(self.eepromPanel, self.eepromPanel.getTitle())
        self.notebook.AddPage(self.microPanel, self.microPanel.getTitle())
        self.notebook.AddPage(self.hexPanel, self.hexPanel.getTitle())

        self.sizer.Add(self.notebook, 1, wx.EXPAND)

    def createLog(self):
        self.log = wx.TextCtrl(self.panel, size = (-1, 17 * 4), value = "", style = wx.TE_MULTILINE | wx.TE_RICH | wx.TE_READONLY | wx.TE_LEFT | wx.TE_BESTWRAP)
        self.sizer.Add(self.log, 0, wx.EXPAND)

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

    def refresh(self):
        self.eepromPanel.refresh()

    def OnExit(self, event):
        self.controller.destroy()

    def OnImport(self, event):
        with wx.FileDialog(self, "Choose Hex file",
            wildcard="Hex files (*.hex;*.bin)|*.hex;*.bin",
            style=wx.FD_OPEN | wx.FD_FILE_MUST_EXIST) as fileDialog:

            if fileDialog.ShowModal() == wx.ID_CANCEL:
                return

            pathname = fileDialog.GetPath()
            self.controller.importFile(pathname)
            data = self.controller.importFile(pathname)
            self.hexPanel.loadContents(data)

    def OnAbout(self, event):
        self.showAboutDialog()

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

    def OnClose(self, event):
        self.controller.destroy()

class EepromPanel(wx.Panel):

    def __init__(self, parent, view, controller):
        wx.Panel.__init__(self, parent)

        self.view = view
        self.controller = controller

        self.gridPanel = wx.Panel(self)
        self.grid = wx.GridSizer(rows=1, cols=2, hgap=16, vgap=16)

        # Device List
        self.deviceList = wx.RadioBox(self.gridPanel, label = 'Device', choices = self.controller.getDevices(),
            majorDimension = 1, style = wx.RA_SPECIFY_COLS)
        self.deviceList.Bind(wx.EVT_RADIOBOX, self.onDeviceSelect)

        self.grid.Add(self.deviceList, 1, wx.EXPAND | wx.ALL)

        # Right Column Grid
        rightGridPanel = wx.Panel(self.gridPanel)
        rightGrid = wx.GridSizer(rows=2, cols=1, hgap=0, vgap=16)

        # Programmer List
        programmerPanel = wx.Panel(rightGridPanel)
        programmerSizer = wx.BoxSizer(wx.VERTICAL)

        programmerSizer.Add(wx.StaticText(programmerPanel, wx.ID_ANY, "Programmer"), 0, wx.EXPAND | wx.BOTTOM | wx.ALIGN_LEFT, 2)

        self.programmerList = wx.Choice(programmerPanel, choices = [], name = 'Programmer')
        self.programmerList.Bind(wx.EVT_CHOICE, self.onProgrammerSelect)
        programmerSizer.Add(self.programmerList, 0, wx.EXPAND)

        programmerPanel.SetSizer(programmerSizer)
        rightGrid.Add(programmerPanel, 1, wx.EXPAND)

        # Action Buttons

        buttonPanel = wx.Panel(rightGridPanel)
        buttonSizer = wx.BoxSizer(wx.HORIZONTAL)

        self.readButton = wx.Button(buttonPanel, wx.ID_ANY, "Read")
        self.readButton.Bind(wx.EVT_BUTTON, self.onReadClick)
        buttonSizer.Add(self.readButton, 0, 0)

        self.writeButton = wx.Button(buttonPanel, wx.ID_ANY, "Write")
        self.writeButton.Bind(wx.EVT_BUTTON, self.onWriteClick)
        buttonSizer.Add(self.writeButton, 0, wx.LEFT, 8)

        buttonPanel.SetSizer(buttonSizer)
        rightGrid.Add(buttonPanel, 0, wx.EXPAND)

        # Add Right Grid

        rightGridPanel.SetSizer(rightGrid)
        self.grid.Add(rightGridPanel, 1, wx.EXPAND)

        # Add Full Grid to Eeprom Panel

        self.gridPanel.SetSizer(self.grid)

        self.panelSizer = wx.BoxSizer(wx.VERTICAL)
        self.panelSizer.Add(self.gridPanel, wx.ID_ANY, wx.EXPAND | wx.ALL, 16)
        self.SetSizer(self.panelSizer)

    def getTitle(self):
        return "EEPROM"

    def refresh(self):
        self.programmerList.SetItems(self.controller.getProgrammers())
        self.onProgrammerSelect(None)

    def onDeviceSelect(self, e):
        name = self.deviceList.GetStringSelection()
        if not name or len(name) <= 0:
            self.view.LogWarning("Invalid device selected")

        self.controller.setDevice(name)

    def onProgrammerSelect(self, e):
        index = self.programmerList.GetSelection()
        str = self.programmerList.GetString(index)

        if len(str) <= 0:
            return

        portname = re.search("\[(COM\d+)\]", str).group(1).strip()
        if len(portname) <= 0:
            self.view.LogWarning("Invalid programmer selected")

        self.controller.setProgrammer(portname)

    def onReadClick(self, e):
        return

    def onWriteClick(self, e):
        return

class MicroPanel(wx.Panel):

    def __init__(self, parent, view, controller):
        wx.Panel.__init__(self, parent)

        self.view = view
        self.controller = controller

        t = wx.StaticText(self, wx.ID_ANY, "This is the microcontroller tab.", (20, 20))

    def getTitle(self):
        return "Microcontroller"

class HexPanel(wx.Panel):

    def __init__(self, parent, view, controller):
        wx.Panel.__init__(self, parent)

        self.view = view
        self.controller = controller

        self.columns = 8

        # Setup Grid
        self.grid = wx.grid.Grid(self, wx.ID_ANY, style = 0)
        self.grid.CreateGrid(1, self.columns * 2 + 1)

        ## Labels
        self.grid.HideRowLabels()
        for i in range(self.columns):
            self.grid.SetColLabelValue(i * 2 + 0, "Address")
            self.grid.SetColLabelValue(i * 2 + 1, "Value")
        self.grid.SetColLabelValue(self.columns * 2, "")

        ## Font
        self.grid.SetDefaultCellAlignment(wx.ALIGN_LEFT, wx.ALIGN_TOP)
        self.grid.SetDefaultCellFont(wx.Font(wx.DEFAULT, wx.TELETYPE, wx.NORMAL, wx.NORMAL, False))

        # Setup Editor
        #self.gridEditor = wx.grid.GridCellTextEditor(maxChars = 2)
        #self.grid.SetDefaultEditor(self.gridEditor)

        # Add to Panel
        sizer = wx.BoxSizer(wx.HORIZONTAL)
        sizer.Add(self.grid, 1, wx.ALL, 0)
        self.SetSizer(sizer)

    def getTitle(self):
        return "Hex"

    def loadContents(self, data):
        self.grid.ClearGrid()
        self.grid.GetTable().DeleteRows(0, self.grid.GetNumberRows())

        if not data or not isinstance(data, list):
            return False

        self.grid.AppendRows(math.ceil(len(data) / self.columns))

        # Set Hex Addresses and Values
        col = 0
        row = 0
        for i, x in enumerate(data):
            self.grid.SetCellValue(row, col * 2 + 0, "0x{0:0{1}x}".format(i, 4))
            self.grid.SetCellValue(row, col * 2 + 1, "0x{0:0{1}x}".format(x, 2))

            col = col + 1
            if col >= self.columns:
                col = 0
                row = row + 1

        # Set String Visualization
        row = 0
        val = ""
        for i, x in enumerate(data):
            char = " "
            try:
                char = chr(x).encode('utf-8').decode('utf-8')
            except UnicodeDecodeError:
                char = " "

            val = val + char
            if len(val) > self.columns or i >= len(data) - 1:
                self.grid.SetCellValue(row, self.columns * 2, val)
                val = ""
                row = row + 1

        self.Layout()

        return True
