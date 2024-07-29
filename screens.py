import serial
from customtkinter import (CTkFrame,
                           CTkLabel,
                           CTkButton,
                           CTkEntry,
                           CTkScrollableFrame,
                           CTkProgressBar,
                           CTkComboBox,
                           CTkToplevel,
                           CTkInputDialog, )
from time import sleep
from threading import Thread
from serial.tools.list_ports import comports
from config import configuration, saveConfig, currentVals

projectLowerFont = ("Roboto", 20)
projectUpperFont = ("Roboto", 24)
print(configuration.model_dump())


class HeaderFrame(CTkFrame):
    def __init__(self, root):
        super().__init__(root)
        self.changeFrame = None
        self.menuActive = False
        self.menuIconToggled = False
        self.configureSliderFrame = None
        self.menuFrame = CTkFrame(self, fg_color="transparent")
        self.titleFrame = CTkFrame(self, fg_color="transparent")
        self.menuButton = CTkButton(self.menuFrame, text="☰", font=projectUpperFont, fg_color="transparent",
                               command=self.toggleMenu)
        self.mainTitle = CTkLabel(self.titleFrame, text="", font=projectUpperFont)
        self.menuButton.pack()
        self.mainTitle.pack()
        self.menuFrame.grid(row=0, column=0)
        self.titleFrame.grid(row=0, column=1, padx=(460, 400))
        self.after(200,self.toggleMenuIcon)
    def toggleMenuIcon(self):
        self.menuIconToggled = True if self.configureSliderFrame.winfo_ismapped() else False
        if self.menuIconToggled:
            self.menuButton.configure(text="<",require_redraw=True)
        else:
            self.menuButton.configure(text="☰",require_redraw=True)
        self.after(200,self.toggleMenuIcon)
    def toggleMenu(self):
        if not self.menuIconToggled:
            if self.menuActive:
                self.changeFrame("menuFrame", "mainFrame")
            else:
                self.changeFrame("mainFrame", "menuFrame")
            self.menuActive = not self.menuActive
        else:
            self.changeFrame("configureSliderFrame","mainFrame")

class MenuFrame(CTkFrame):
    def __init__(self, root):
        super().__init__(root, fg_color="transparent")
        self.availableCOMPorts = [str(port).split(" ")[0] for port in comports()]
        self.isFetching = False
        self.redrawSliders = None

        self.currentConfigFrame = CTkFrame(self, fg_color="transparent")
        self.currentCOMPort = CTkLabel(self.currentConfigFrame,
                                       text=f'Current COM Port: {configuration.COMPort if configuration.isConfigured else "None"}',
                                       font=projectLowerFont)
        self.currentCOMPort.pack()
        self.currentBaudRate = CTkLabel(self.currentConfigFrame,
                                        text=f'Current Baud Rate: {configuration.baudRate if configuration.isConfigured else "None"}',
                                        font=projectLowerFont)
        self.currentBaudRate.pack()
        self.currentConfigFrame.pack(pady=10)

        self.buttonsFrame = CTkFrame(self, fg_color="transparent")
        self.changeConfig = CTkLabel(self.buttonsFrame, text="Change Configuration", font=projectUpperFont)
        self.changeConfig.pack()
        self.comPortLabel = CTkLabel(self.buttonsFrame, text="Select Comport", font=projectLowerFont)
        self.comPortLabel.pack(pady=5)
        self.comPortDropdown = CTkComboBox(self.buttonsFrame, values=self.availableCOMPorts)
        self.comPortDropdown.pack(pady=5)
        self.refreshInfoButton = CTkButton(self.buttonsFrame, text="Refresh COM Ports", command=self.refreshInfo)
        self.refreshInfoButton.pack(pady=5)
        self.baudRateLabel = CTkLabel(self.buttonsFrame, text="Enter Baud Rate", font=projectLowerFont)
        self.baudRateLabel.pack(pady=5)
        self.baudRateEntry = CTkEntry(self.buttonsFrame, placeholder_text="Enter Baud Rate")
        self.baudRateEntry.pack(pady=5)
        self.confirmBoardConfigButton = CTkButton(self.buttonsFrame, text="Confirm Config",
                                                  command=self.confirmBoardConfig)
        self.confirmBoardConfigButton.pack(pady=(5))
        self.errorMessage = CTkLabel(self.buttonsFrame, text="", text_color="red", font=projectLowerFont)
        self.errorMessage.pack()
        self.buttonsFrame.pack()

    def refreshInfo(self):
        self.availableCOMPorts = [str(port).split(" ")[0] for port in comports()]
        self.comPortDropdown.configure(values=self.availableCOMPorts)
        print(self.availableCOMPorts)

    def confirmBoardConfig(self):
        print(self.isFetching)
        if self.isFetching:
            return
        self.isFetching = True
        self.errorMessage.configure(text="")
        comport = self.comPortDropdown.get()
        baudRate = self.baudRateEntry.get()
        if not baudRate.isnumeric():
            self.errorMessage.configure(text="Please enter a valid Baud Rate")
            self.isFetching = False
            return
        currentVals.backgroundService = False
        sleep(.05)
        try:
            serialPort = serial.Serial(comport, baudRate, timeout=1)
            serialPort.readline()
            data = serialPort.read_until(b"\n")
            data = data.rstrip(b"\r\n").decode("utf-8")

            if not data.startswith("(") and not data.endswith(")"):
                self.errorMessage.configure(text="Please check if valid configuration has been entered")
                self.isFetching = False
                currentVals.backgroundService = True
                serialPort.close()
                return

            data = data.removeprefix("(")
            data = data.removesuffix(")")

            sliderNums = len(data.split('-'))
            if sliderNums == 0:
                self.errorMessage.configure(text="No Sliders Detected")
                self.isFetching = False
                currentVals.backgroundService = True
                serialPort.close()
                return
            inputField = CTkInputDialog(
                text=f'{sliderNums} slider(s) detected\nType "confirm" to override current configuration')
            confirmChange = inputField.get_input()
            if confirmChange is None or not confirmChange.lower() == "confirm":
                self.isFetching = False
                currentVals.backgroundService = True
                serialPort.close()
                return
            sliders = {"slider1": "main"}
            for i in range(sliderNums - 1):
                sliders.update({"slider" + str(i + 2): []})

            configuration.COMPort = comport
            configuration.baudRate = int(baudRate)
            configuration.numOfSliders = sliderNums
            configuration.isConfigured = True
            configuration.isBoardActive = True
            configuration.sliders = sliders
            saveConfig()
            serialPort.close()
        except Exception as e:

            self.errorMessage.configure(text="Board Not Detected")
            print(str(e))
        currentVals.backgroundService = True
        self.isFetching = False


class MainFrame(CTkFrame):
    def __init__(self, root):
        super().__init__(root, fg_color="transparent")
        self.changeFrame = None
        self.configureSliderFrame = None
        self.errorMessageLabel = CTkLabel(self, text="", font=projectUpperFont, text_color="red")
        self.drawSliders()

    def drawSliders(self):
        for child in self.winfo_children():
            child.forget()
        if not configuration.isConfigured:
            self.errorMessageLabel.configure(text="Program is not configured")
            self.errorMessageLabel.pack()
            return
        if not configuration.isBoardActive:
            self.errorMessageLabel.configure(text="Board not connected")
            self.errorMessageLabel.pack()
            return
        for index in range(configuration.numOfSliders):
            slider = VerticalSlider(self, index,self.changeFrame,self.configureSliderFrame )
            slider.grid(column=index, row=0, padx=50)


class VerticalSlider(CTkFrame):
    def __init__(self, root, index, changeFrame, configureSliderFrame):
        super().__init__(root, fg_color="transparent")
        self.index = index
        self.changeFrame = changeFrame
        self.configureSliderFrame = configureSliderFrame
        self.barTitle = CTkLabel(self, text=f"Slider {index + 1}", font=projectUpperFont)
        self.barTitle.grid(row=0, column=0, pady=(0, 20))
        self.progressBar = CTkProgressBar(self, orientation="vertical", width=40, height=350)
        self.progressBar.grid(row=1, column=0)
        if self.index == 0:
            self.masterLabel = CTkLabel(self, text="Master Volume", font=projectUpperFont)
            self.masterLabel.grid(column=0, row=2, pady=10)
        else:
            self.configureButton = CTkButton(self, text="Configure", font=projectUpperFont,command=self.openConfigurationScreen)
            self.configureButton.grid(column=0, row=2, pady=10)
        self.after(30, self.updateSliderInfo)
    def openConfigurationScreen(self):
        self.configureSliderFrame.resetCurrentApplications(self.index)
        self.changeFrame("mainFrame","configureSliderFrame")
    def updateSliderInfo(self):

        if not configuration.isConfigured or not configuration.isBoardActive:
            return
        try:
            self.progressBar.set(int(currentVals.sliderVals[self.index]) / 100)
        except Exception as e:
            print(e)
        self.after(30, self.updateSliderInfo)

class ConfigureSliderFrame(CTkFrame):
    def __init__(self, root):
        super().__init__(root)
        self.configureTitle = CTkLabel(self, text="Configure Slider Applications", font=projectUpperFont)
        self.configureTitle.pack(pady=5)
        self.index = 0
        self.currentApplications = []
        self.currentApplicationsLabel = CTkLabel(self, text="", font=projectLowerFont)
        self.currentApplicationsLabel.pack(pady=5)
        self.addApplicationLabel = CTkLabel(self, text="Add New Application", font=projectUpperFont)
        self.addApplicationLabel.pack(pady=5)
        self.addApplicationFrame = CTkFrame(self,fg_color="transparent")
        self.addApplicationEntry = CTkEntry(self.addApplicationFrame, placeholder_text="Application Name", font=projectLowerFont)
        self.addApplicationEntry.grid(pady=5, row=1, column=0,padx=5)
        self.addApplicationButton = CTkButton(self.addApplicationFrame, text="+", font=projectUpperFont, command=self.addNewApplication)
        self.addApplicationButton.grid(pady=5,row=1,column=1,padx=5)
        self.addApplicationFrame.pack(pady=5)

    def resetCurrentApplications(self, index):
        self.index = index
        self.currentApplications = configuration.sliders[f'slider{index + 1}']
        if not self.currentApplications:
            text = "No Applications Are Configured"
        else:
            text = '\n'.join(self.currentApplications)

        self.currentApplicationsLabel.configure(text=text, require_redraw=True)

    def addNewApplication(self):
        applicationName = self.addApplicationEntry.get()
        if applicationName == "":
            return
        applicationName+=".exe"
        for slider in configuration.sliders:
            for appName in configuration.sliders[slider]:
                if applicationName == appName:
                    return
        self.currentApplications.append(applicationName)
        configuration.sliders[f'slider{self.index+1}'] = self.currentApplications
        configuration.slidersIndex.update({applicationName:self.index})
        saveConfig()
        self.resetCurrentApplications(self.index)
        self.addApplicationEntry.delete(0,len(applicationName))