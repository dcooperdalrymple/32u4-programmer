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

        self.defaultDir = '.'

    def run(self):
        self.frame = AppFrame(self, self.controller, None, -1, title = '32u4 Programmer Utility', size = (480, 420), style = self.frameStyle)
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

    def _log(self, message, color = (108, 117, 125)):
        start = len(self.frame.log.GetValue())
        self.frame.log.AppendText(message)
        self.frame.log.SetStyle(start, len(self.frame.log.GetValue()), wx.TextAttr(color))
        return True

    def Log(self, message, color = (108, 117, 125)):
        # Use CallAfter to prevent multithreading issues
        wx.CallAfter(self._log, '\n' + message, color)
        return True

    def LogError(self, message, title = "Error"):
        return self.Log(title + ": " + message, (220, 53, 69))

    def LogWarning(self, message, title = "Warning"):
        return self.Log(title + ": " + message, (255, 193, 7))

    def LogSuccess(self, message):
        return self.Log(message, (40, 167, 69))

    def updateDefaultDir(self, pathname):
        self.defaultDir = os.path.dirname(os.path.abspath(pathname))
        return True

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
        #self.microPanel = MicroPanel(self.notebook, self.view, self.controller)
        self.hexPanel = HexPanel(self.notebook, self.view, self.controller)
        self.debugPanel = DebugPanel(self.notebook, self.view, self.controller)

        self.notebook.AddPage(self.eepromPanel, self.eepromPanel.getTitle())
        #self.notebook.AddPage(self.microPanel, self.microPanel.getTitle())
        self.notebook.AddPage(self.hexPanel, self.hexPanel.getTitle())
        self.notebook.AddPage(self.debugPanel, self.debugPanel.getTitle())

        self.sizer.Add(self.notebook, 1, wx.EXPAND)

    def createLog(self):
        self.log = wx.TextCtrl(self.panel, size = (-1, 17 * 4), value = "", style = wx.TE_MULTILINE | wx.TE_RICH | wx.TE_READONLY | wx.TE_LEFT | wx.TE_BESTWRAP)
        self.sizer.Add(self.log, 0, wx.EXPAND)

    def createMenuBar(self):
        fileMenu = wx.Menu()
        importItem = fileMenu.Append(wx.ID_ANY, "&Import Hex File...\tCtrl-I", "Select a file to program to EEPROM or Microcontroller")
        fileMenu.AppendSeparator()
        exitItem = fileMenu.Append(wx.ID_EXIT)

        programMenu = wx.Menu()
        refreshItem = programMenu.Append(wx.ID_ANY, "&Refresh\tF5", "Refresh the list of programmers by querying serial COM ports.")
        programMenu.AppendSeparator()
        readItem = programMenu.Append(wx.ID_ANY, "&Read Device...\tCtrl-R", "Read ROM contents from selected device and programmer.")
        writeItem = programMenu.Append(wx.ID_ANY, "&Write Device...\tCtrl-W", "Write ROM contents from selected hex file to device from programmer.")

        helpMenu = wx.Menu()
        aboutItem = helpMenu.Append(wx.ID_ABOUT)

        menuBar = wx.MenuBar()
        menuBar.Append(fileMenu, "&File")
        menuBar.Append(programMenu, "&Program")
        menuBar.Append(helpMenu, "&Help")

        self.SetMenuBar(menuBar)

        self.Bind(wx.EVT_MENU, self.OnImport, importItem)
        self.Bind(wx.EVT_MENU, self.OnExit,  exitItem)

        self.Bind(wx.EVT_MENU, self.OnRefresh, refreshItem)
        self.Bind(wx.EVT_MENU, self.OnRead, readItem)
        self.Bind(wx.EVT_MENU, self.OnWrite, writeItem)

        self.Bind(wx.EVT_MENU, self.OnAbout, aboutItem)

    def refresh(self):
        self.eepromPanel.refresh()

    def OnImport(self, event):
        with wx.FileDialog(self, "Choose Hex file",
            wildcard = "Hex files (*.hex;*.bin)|*.hex;*.bin",
            style = wx.FD_OPEN | wx.FD_FILE_MUST_EXIST,
            defaultDir = self.view.defaultDir) as fileDialog:

            if fileDialog.ShowModal() == wx.ID_CANCEL:
                return

            pathname = fileDialog.GetPath()
            self.view.updateDefaultDir(pathname)

            data = self.controller.importFile(pathname)
            self.hexPanel.loadContents(data)

    def OnExit(self, event):
        self.controller.destroy()

    def OnRefresh(self, event):
        self.view.refresh()

    def OnRead(self, event):
        self.eepromPanel.onReadClick(event)

    def OnWrite(self, event):
        self.eepromPanel.onWriteClick(event)

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

        self.panel = wx.Panel(self)
        self.sizer = wx.BoxSizer(wx.VERTICAL)

        # Device List
        devicePanel = wx.Panel(self.panel)
        deviceSizer = wx.BoxSizer(wx.VERTICAL)

        deviceSizer.Add(wx.StaticText(devicePanel, wx.ID_ANY, "Device"), 0, wx.EXPAND | wx.BOTTOM | wx.ALIGN_LEFT, 4)

        self.deviceList = wx.Choice(devicePanel, choices = self.controller.getDevices(), name = 'Device', style = wx.CB_SORT)
        self.deviceList.Bind(wx.EVT_CHOICE, self.onDeviceSelect)
        deviceSizer.Add(self.deviceList, 0, wx.EXPAND)

        devicePanel.SetSizer(deviceSizer)
        self.sizer.Add(devicePanel, 0, wx.EXPAND | wx.BOTTOM, 16)

        # Programmer List
        programmerPanel = wx.Panel(self.panel)
        programmerSizer = wx.BoxSizer(wx.VERTICAL)

        programmerSizer.Add(wx.StaticText(programmerPanel, wx.ID_ANY, "Programmer"), 0, wx.EXPAND | wx.BOTTOM | wx.ALIGN_LEFT, 4)

        self.programmerList = wx.Choice(programmerPanel, choices = [], name = 'Programmer')
        self.programmerList.Bind(wx.EVT_CHOICE, self.onProgrammerSelect)
        programmerSizer.Add(self.programmerList, 0, wx.EXPAND)

        programmerPanel.SetSizer(programmerSizer)
        self.sizer.Add(programmerPanel, 0, wx.EXPAND | wx.BOTTOM, 16)

        # Action Buttons

        buttonPanel = wx.Panel(self.panel)
        buttonSizer = wx.BoxSizer(wx.HORIZONTAL)

        self.readButton = wx.Button(buttonPanel, wx.ID_ANY, "Read")
        self.readButton.Bind(wx.EVT_BUTTON, self.onReadClick)
        buttonSizer.Add(self.readButton, 0, wx.ALIGN_RIGHT | wx.ALIGN_BOTTOM)

        self.writeButton = wx.Button(buttonPanel, wx.ID_ANY, "Write")
        self.writeButton.Bind(wx.EVT_BUTTON, self.onWriteClick)
        buttonSizer.Add(self.writeButton, 0, wx.ALIGN_RIGHT | wx.ALIGN_BOTTOM | wx.LEFT, 8)

        buttonPanel.SetSizer(buttonSizer)
        self.sizer.Add(buttonPanel, 1, wx.ALIGN_RIGHT | wx.ALIGN_BOTTOM)

        # Add Full Panel to Eeprom Panel

        self.panel.SetSizer(self.sizer)

        self.panelSizer = wx.BoxSizer(wx.VERTICAL)
        self.panelSizer.Add(self.panel, 1, wx.EXPAND | wx.ALL, 16)
        self.SetSizer(self.panelSizer)

    def getTitle(self):
        return "EEPROM"

    def refresh(self):
        wx.CallAfter(self.disableControls)
        self.programmerList.SetItems(self.controller.getProgrammers())
        self.onProgrammerSelect(None)
        wx.CallAfter(self.enableControls)

    def onDeviceSelect(self, e):
        index = self.deviceList.GetSelection()
        name = self.deviceList.GetString(index)
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
            self.view.LogWarning("Invalid programmer selected.")
            return

        if self.controller.setProgrammer(portname):
            self.view.LogSuccess("Successfully connected with programmer on {}.".format(portname))

    def onReadClick(self, e):
        self.disableControls()

        self.view.Log("Beginning device read.")

        # Thread to perform read, save output, and re-enable controls once complete
        thread = threading.Thread(target = self.performRead)
        thread.start()

    def performRead(self):
        # Read contents of device from programmer
        data = self.controller.readDevice()

        if isinstance(data, list):
            # Display read data in hex viewer
            wx.CallAfter(self.view.frame.hexPanel.loadContents, data)

            # Select file to save hex file
            with wx.FileDialog(self, "Save ROM Hex File",
                wildcard = "Hex files (*.hex;*.bin)|*.hex;*.bin",
                style = wx.FD_SAVE | wx.FD_OVERWRITE_PROMPT,
                defaultDir = self.view.defaultDir) as fileDialog:

                if fileDialog.ShowModal() != wx.ID_CANCEL:
                    pathname = fileDialog.GetPath()
                    self.view.updateDefaultDir(pathname)

                    # Write data to file
                    self.controller.exportFile(pathname, data)

        self.view.Log("Device read process completed.")
        self.enableControls()

    def onWriteClick(self, e):
        self.disableControls()

        # Select file to import
        with wx.FileDialog(self, "Choose Hex File to Write Device",
            wildcard = "Hex files (*.hex;*.bin)|*.hex;*.bin",
            style = wx.FD_OPEN | wx.FD_FILE_MUST_EXIST,
            defaultDir = self.view.defaultDir) as fileDialog:

            if fileDialog.ShowModal() == wx.ID_CANCEL:
                self.enableControls()
                return

            pathname = fileDialog.GetPath()
            self.view.updateDefaultDir(pathname)

            self.view.Log("Beginning device write from {}.".format(pathname))

            # Thread to perform write and re-enable controls once complete
            thread = threading.Thread(target = self.performWrite, args = (pathname,))
            thread.start()

    def performWrite(self, pathname):
        # Display write data in hex viewer
        data = self.controller.importFile(pathname)
        if data != False and isinstance(data, list):
            wx.CallAfter(self.view.frame.hexPanel.loadContents, data)

        # Perform write to Eeprom from Programmer
        self.controller.writeFile(pathname)

        self.view.Log("Device write process completed.")
        self.enableControls()

    def disableControls(self):
        # Use CallAfter to prevent multithreading issues
        wx.CallAfter(self.deviceList.Disable)
        wx.CallAfter(self.programmerList.Disable)
        wx.CallAfter(self.readButton.Disable)
        wx.CallAfter(self.writeButton.Disable)

    def enableControls(self):
        # Use CallAfter to prevent multithreading issues
        wx.CallAfter(self.deviceList.Enable)
        wx.CallAfter(self.programmerList.Enable)
        wx.CallAfter(self.readButton.Enable)
        wx.CallAfter(self.writeButton.Enable)

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
        self.grid.EnableEditing(False)

        ## Labels
        self.grid.HideRowLabels()
        for i in range(self.columns):
            self.grid.SetColLabelValue(i * 2 + 0, "Address")
            self.grid.SetColLabelValue(i * 2 + 1, "Value")
        self.grid.SetColLabelValue(self.columns * 2, "")

        ## Font
        self.grid.SetDefaultCellAlignment(wx.ALIGN_LEFT, wx.ALIGN_TOP)
        self.grid.SetDefaultCellFont(wx.Font(wx.DEFAULT, wx.TELETYPE, wx.NORMAL, wx.NORMAL, False))

        # Add to Panel
        sizer = wx.BoxSizer(wx.HORIZONTAL)
        sizer.Add(self.grid, 1, wx.EXPAND | wx.ALL, 0)
        self.SetSizer(sizer)

    def getTitle(self):
        return "Hex"

    def loadContents(self, data):
        self.grid.ClearGrid()
        self.grid.GetTable().DeleteRows(0, self.grid.GetNumberRows())

        if not data or not isinstance(data, list):
            return False

        self.grid.GetTable().AppendRows(int(math.ceil(float(len(data)) / float(self.columns))))

        # Set Hex Addresses and Values
        col = 0
        row = 0
        for i, x in enumerate(data):
            self.grid.SetCellValue(row, col * 2 + 0, "{0:0{1}x}".format(i, 4))
            self.grid.SetCellValue(row, col * 2 + 1, "{0:0{1}x}".format(x, 2))

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

class DebugPanel(wx.Panel):

    def __init__(self, parent, view, controller):
        wx.Panel.__init__(self, parent)

        self.view = view
        self.controller = controller

        self.gutter = 16
        self.sizer = wx.BoxSizer(wx.VERTICAL)

        fieldPanel = wx.Panel(self)
        fieldSizer = wx.WrapSizer()

        # Command List
        commandPanel = wx.Panel(fieldPanel)
        commandSizer = wx.BoxSizer(wx.VERTICAL)

        commandSizer.Add(wx.StaticText(commandPanel, wx.ID_ANY, "Command"), 0, wx.BOTTOM | wx.ALIGN_LEFT, 4)

        self.commandList = wx.Choice(commandPanel, choices = self.controller.getCommands(), name = 'Command', style = 0)
        self.commandList.Bind(wx.EVT_CHOICE, self.onCommandSelect)
        commandSizer.Add(self.commandList, 0, wx.ALIGN_LEFT, 0)

        commandPanel.SetSizer(commandSizer)
        fieldSizer.Add(commandPanel, 0, wx.ALL, self.gutter / 2)

        # Start Address Field
        addressPanel = wx.Panel(fieldPanel)
        addressSizer = wx.BoxSizer(wx.VERTICAL)

        addressSizer.Add(wx.StaticText(addressPanel, wx.ID_ANY, "Address"), 0, wx.BOTTOM | wx.ALIGN_LEFT, 4)

        self.addressField = wx.TextCtrl(addressPanel, value = "", style = wx.TE_LEFT | wx.TE_DONTWRAP)
        addressSizer.Add(self.addressField, 0, wx.ALIGN_LEFT, 0)

        addressPanel.SetSizer(addressSizer)
        fieldSizer.Add(addressPanel, 0, wx.ALL, self.gutter / 2)

        # Data Length Field
        dataLengthPanel = wx.Panel(fieldPanel)
        dataLengthSizer = wx.BoxSizer(wx.VERTICAL)

        dataLengthSizer.Add(wx.StaticText(dataLengthPanel, wx.ID_ANY, "Data Length"), 0, wx.BOTTOM | wx.ALIGN_LEFT, 4)

        self.dataLengthField = wx.TextCtrl(dataLengthPanel, value = "", style = wx.TE_LEFT | wx.TE_DONTWRAP)
        dataLengthSizer.Add(self.dataLengthField, 0, wx.ALIGN_LEFT, 0)

        dataLengthPanel.SetSizer(dataLengthSizer)
        fieldSizer.Add(dataLengthPanel, 0, wx.ALL, self.gutter / 2)

        # Line Length Field
        lineLengthPanel = wx.Panel(fieldPanel)
        lineLengthSizer = wx.BoxSizer(wx.VERTICAL)

        lineLengthSizer.Add(wx.StaticText(lineLengthPanel, wx.ID_ANY, "Line Length"), 0, wx.BOTTOM | wx.ALIGN_LEFT, 4)

        self.lineLengthField = wx.TextCtrl(lineLengthPanel, value = "", style = wx.TE_LEFT | wx.TE_DONTWRAP)
        lineLengthSizer.Add(self.lineLengthField, 0, wx.ALIGN_LEFT, 0)

        lineLengthPanel.SetSizer(lineLengthSizer)
        fieldSizer.Add(lineLengthPanel, 0, wx.ALL, self.gutter / 2)

        # Action Button
        actionPanel = wx.Panel(fieldPanel)
        actionSizer = wx.BoxSizer(wx.VERTICAL)

        self.actionButton = wx.Button(actionPanel, wx.ID_ANY, "Send Command")
        self.actionButton.Bind(wx.EVT_BUTTON, self.onActionClick)
        actionSizer.Add(self.actionButton, 0, wx.ALIGN_RIGHT | wx.ALIGN_TOP | wx.TOP, 19 + 4)

        actionPanel.SetSizer(actionSizer)
        fieldSizer.Add(actionPanel, 1, wx.ALL, self.gutter / 2)

        # Add field panel to control panel
        fieldPanel.SetSizer(fieldSizer)
        self.sizer.Add(fieldPanel, 0, wx.EXPAND | wx.ALL, self.gutter / 2)

        # Result Text Box
        resultPanel = wx.Panel(self)
        resultSizer = wx.BoxSizer(wx.VERTICAL)

        resultSizer.Add(wx.StaticText(resultPanel, wx.ID_ANY, "Results"), 0, wx.BOTTOM | wx.ALIGN_LEFT, 4)

        self.resultField = wx.TextCtrl(resultPanel, value = "", style = wx.TE_MULTILINE | wx.TE_RICH | wx.TE_READONLY | wx.TE_LEFT | wx.TE_BESTWRAP)
        resultSizer.Add(self.resultField, 1, wx.EXPAND)

        resultPanel.SetSizer(resultSizer)
        self.sizer.Add(resultPanel, 1, wx.EXPAND | wx.RIGHT | wx.BOTTOM | wx.LEFT, self.gutter)

        self.SetSizer(self.sizer)

        # Set up input filtering
        self.addressField.SetMaxLength(4)
        self.addressField.Bind(wx.EVT_CHAR, self.filterHex)

        self.dataLengthField.SetMaxLength(4)
        self.dataLengthField.Bind(wx.EVT_CHAR, self.filterHex)

        self.lineLengthField.SetMaxLength(2)
        self.lineLengthField.Bind(wx.EVT_CHAR, self.filterHex)

        # Disable controls
        self.onCommandSelect(None)

    def getTitle(self):
        return "Debug"

    def getCommandInfo(self):
        index = self.commandList.GetSelection()
        str = self.commandList.GetString(index)
        if len(str) <= 0 or str is None:
            return False

        command = re.search("\[([a-zA-Z])\]", str).group(1)
        if len(command) <= 0:
            return False

        commandInfo = self.controller.getCommand(command)
        if not commandInfo:
            return False

        return commandInfo

    def onCommandSelect(self, e):
        index = self.commandList.GetSelection()
        str = self.commandList.GetString(index)
        if len(str) <= 0 or str is None:
            self.addressField.Disable()
            self.dataLengthField.Disable()
            self.lineLengthField.Disable()
            self.actionButton.Disable()
            return

        commandInfo = self.getCommandInfo()
        if not commandInfo:
            self.addressField.Disable()
            self.dataLengthField.Disable()
            self.lineLengthField.Disable()
            self.actionButton.Disable()
            self.view.LogWarning("Invalid command selected.")
            return

        self.actionButton.Enable()

        if commandInfo["address"] == True:
            self.addressField.Enable()
        else:
            self.addressField.Disable()

        if commandInfo["dataLength"] == True:
            self.dataLengthField.Enable()
        else:
            self.dataLengthField.Disable()

        if commandInfo["lineLength"] == True:
            self.lineLengthField.Enable()
        else:
            self.lineLengthField.Disable()

        self.view.Log("Configured debug for command: {}.".format(commandInfo["title"]))

    def onActionClick(self, event):
        commandInfo = self.getCommandInfo()
        if not commandInfo:
            self.view.LogWarning("No valid command selected.", "Unable to Send Command")
            return

        address = self.getHexValue(self.addressField, 4)
        if commandInfo["address"] == False: address = None

        dataLength = self.getHexValue(self.dataLengthField, 4)
        if commandInfo["dataLength"] == False: dataLength = None

        lineLength = self.getHexValue(self.lineLengthField, 2)
        if commandInfo["lineLength"] == False: lineLength = None

        # Request and send data input
        dataInput = ""
        if commandInfo["input"] != False and commandInfo["input"] == "dataLength" and dataLength != None:
            success = False
            quit = False
            while success == False and quit == False:
                # Dialog for input
                with wx.TextEntryDialog(self.view.frame, "Enter {} bytes of data in hexadecimal format.".format(dataLength), "Command Data Entry", style = wx.OK | wx.CANCEL) as dialog:
                    dialog.SetMaxLength(dataLength * 2)
                    dialog.SetValue(dataInput)

                    ret = dialog.ShowModal()
                    if ret == wx.ID_OK:
                        dataInput = str(dialog.GetValue())
                    elif ret == wx.ID_CANCEL:
                        quit = True

                    dialog.Destroy()
                if quit == True:
                    break

                # Validate input
                if len(dataInput) != dataLength * 2:
                    self.view.ShowErrorDialog("Not enough data to complete command.")
                elif re.search("^[a-fA-F0-9]{" + str(dataLength * 2) + "}$", dataInput) is None:
                    self.view.ShowErrorDialog("Invalid data entry. Must be all hexidecimal characters.")
                else:
                    success = True

            if quit == True:
                return

        if dataInput == False or not isinstance(dataInput, str) or (commandInfo["input"] == "dataLength" and dataLength != None and len(dataInput) != dataLength * 2): dataInput = None

        # Send command to programmer
        self.view.Log("Sending command to programmer.")
        if not self.controller.sendCommand(commandInfo["code"], address, dataLength, lineLength):
            self.view.LogError("Failed to send debug command.")
            return

        if dataInput is not None and isinstance(dataInput, str) and len(dataInput) > 0:
            self.view.Log("Sending data to programmer.")
            if not self.controller.writeString(dataInput):
                self.view.LogError("Failed to send debug input data.")
                return

        # Read programmer results
        if commandInfo["return"] != False:
            self.view.Log("Reading command response from programmer.")
            result = self.controller.readCommand(commandInfo, dataLength, lineLength)
            if result == False:
                self.view.LogError("Failed to read debug data from programmer.")
                self.resultField.SetValue("")
                return
            else:
                self.resultField.SetValue(result)
        else:
            self.resultField.SetValue("")

        self.view.LogSuccess("Programmer debug request successfully completed.")

    def filterHex(self, event):
        keycode = event.GetKeyCode()
        if keycode > 255 or keycode in [8, 9, 127] or re.match("[a-fA-F0-9]", chr(keycode)) is not None:
            event.Skip()

    def getHexValue(self, ctrl, length):
        # Check if valid entry
        val = str(ctrl.GetValue())
        if not isinstance(val, str) or len(val) > length or len(val) <= 0:
            return None

        # Format hex string
        val = "0x" + val.zfill(length)

        # Convert to integer
        return int(val, base = 16)

# NOTE: Maybe create HexGrid class based on HugeTableGrid example.
