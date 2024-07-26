import serial
from time import sleep, time
from config import configuration, currentVals
from threading import Thread


class BackgroundTask:
    def __init__(self):
        self.serialPort = None
        self.prevState = True
        self.badReads = []

    def freeSerialPort(self):
        self.serialPort.close()
        self.serialPort = None

    def openSerialPort(self):
        self.serialPort = serial.Serial(configuration.COMPort, configuration.baudRate, timeout=1)

    def start(self):
        thread = Thread(target=self.backgroundTask)
        thread.start()

    def backgroundTask(self):
        for i in range(1):
            if not currentVals.backgroundService and self.serialPort is not None:
                self.freeSerialPort()
            if not currentVals.backgroundService:
                break
            if not configuration.isConfigured:
                break
            if self.serialPort is None:
                try:
                    self.openSerialPort()
                    self.serialPort.flush()
                    data = self.serialPort.read_until(b"\n").rstrip(b"\r\n").decode("utf-8")
                    if not data.startswith("(") and not data.endswith(")"):
                        configuration.isBoardActive = False
                        break
                    data = data.replace("(", "")
                    data = data.replace(")", "")
                    if len(data.split('-')) != configuration.numOfSliders:
                        configuration.isConfigured = False
                        break
                    configuration.isBoardActive = True
                except Exception as e:
                    configuration.isBoardActive = False
                    break

            if configuration.isBoardActive:
                try:
                    self.serialPort.flush()
                    data = self.serialPort.read_until(b"\n").rstrip(b"\r\n").decode("utf-8")
                    print(data)
                    if not data.startswith("(") and not data.endswith(")"):
                        self.badReads.append(int(time() + 10))
                        self.badReads = [last10 for last10 in self.badReads if last10 >= time()]
                        if len(self.badReads) >= 10:
                            configuration.isBoardActive = False
                            break
                    data = data.replace("(", "")
                    data = data.replace(")", "")
                    if len(data.split('-')) != configuration.numOfSliders:
                        configuration.isConfigured = False
                        break
                    currentVals.sliderVals = data.split('-')

                except Exception as e:
                    configuration.isBoardActive = False
        print(configuration.isBoardActive, configuration.isConfigured)
        sleep(.03)
        thread = Thread(target=self.backgroundTask)
        thread.start()
