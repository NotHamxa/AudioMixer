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
from config import configuration, saveConfig

projectLowerFont = ("Roboto", 20)
projectUpperFont = ("Roboto", 24)
print(configuration.model_dump())


class HeaderFrame(CTkFrame):
    def __init__(self, root):
        super().__init__(root)
        self.changeFrame = None
        self.menuActive = False
        menuFrame = CTkFrame(self, fg_color="transparent")
        titleFrame = CTkFrame(self, fg_color="transparent")
        menuButton = CTkButton(menuFrame, text="☰", font=projectUpperFont, fg_color="transparent",
                               command=self.toggleMenu)
        mainTitle = CTkLabel(titleFrame, text="", font=projectUpperFont)
        menuButton.pack()
        mainTitle.pack()
        menuFrame.grid(row=0, column=0)
        titleFrame.grid(row=0, column=1, padx=(460, 400))

    def toggleMenu(self):
        if self.menuActive:
            self.changeFrame("menuFrame", "mainFrame")
        else:
            self.changeFrame("mainFrame", "menuFrame")
        self.menuActive = not self.menuActive


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
        try:
            serialPort = serial.Serial(comport, baudRate, timeout=1)
            serialPort.readline()
            data = serialPort.read_until(b"\n")
            data = data.rstrip(b"\r\n").decode("utf-8")

            if not data.startswith("(") and not data.endswith(")"):
                self.errorMessage.configure(text="Please check if valid configuration has been entered")
                self.isFetching = False
                return

            data = data.removeprefix("(")
            data = data.removesuffix(")")

            sliderNums = len(data.split('-'))
            if sliderNums == 0:
                self.errorMessage.configure(text="No Sliders Detected")
                self.isFetching = False
                return
            inputField = CTkInputDialog(
                text=f'{sliderNums} slider(s) detected\nType "confirm" to override current configuration')
            confirmChange = inputField.get_input()
            if confirmChange is None or not confirmChange.lower() == "confirm":
                self.isFetching = False
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
        except Exception as e:
            self.errorMessage.configure(text="Board Not Detected")
            print(str(e))
        self.isFetching = False


class MainFrame(CTkFrame):
    def __init__(self, root):
        super().__init__(root, fg_color="transparent")

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
        for i in range(configuration.numOfSliders):
            slider = VerticalSlider(self)
            slider.grid(column=i, row=0, padx=50)


class VerticalSlider(CTkFrame):
    def __init__(self, root):
        super().__init__(root, fg_color="transparent")
        barTitle = CTkLabel(self, text="Slider 1", font=projectUpperFont)
        barTitle.grid(row=0, column=0, pady=(0, 20))
        progressBar = CTkProgressBar(self, orientation="vertical", width=40, height=350)
        progressBar.grid(row=1, column=0)

    def updateSliderInfo(self):
        if not configuration.isConfigured or not configuration.isBoardActive:
            return
