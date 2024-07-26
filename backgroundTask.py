import serial
from time import sleep,time
from config import configuration, currentVals
from threading import Thread
class BackgroundTask():
    def __init__(self):
        self.serialPort = None
        self.prevState = True
        self.badReads = []
    def freeSerialPort(self):
        self.serialPort.close()
    def openSerialPort(self):
        self.serialPort = serial.Serial(configuration.COMPort,configuration.baudRate,timeout=1)
    def start(self):
        thread = Thread(target=self.backgroundTask)
        thread.start()
    def backgroundTask(self):
        if self.prevState!=currentVals.backgroundService:
            try:
                if not currentVals.backgroundService:
                    self.freeSerialPort()
                else:
                    self.openSerialPort()
            except Exception as e:
                configuration.isBoardActive=False
                print(str(e))
        if currentVals.backgroundService:
            if not configuration.isBoardActive and configuration.isConfigured:
                try:
                    self.openSerialPort()
                    self.serialPort.flush()
                    data = self.serialPort.read_until(b"\n").rstrip(b"\r\n").decode("utf-8")
                    if not data.startswith("(") and not data.endswith(")"):
                        raise Exception
                    data = data.replace("(","")
                    data = data.replace(")","")
                    if len(data.split('-'))!=configuration.numOfSliders:
                        configuration.isConfigured = False
                        raise Exception
                    configuration.isBoardActive = True
                except Exception as e:
                    print(str(e))
            if configuration.isConfigured and configuration.isBoardActive:
                try:
                    self.serialPort.flush()
                    data = self.serialPort.read_until(b"\n").rstrip(b"\r\n").decode("utf-8")
                    print(data)
                    if not data.startswith("(") and not data.endswith(")"):
                        self.badReads.append(int(time()+10))
                        self.badReads = [last10 for last10 in self.badReads if last10>=time()]
                        if len(self.badReads)>=10:
                            configuration.isBoardActive = False
                    data = data.replace("(","")
                    data = data.replace(")","")
                    if len(data.split('-'))!=configuration.numOfSliders:
                        configuration.isConfigured = False
                        raise Exception
                    print(data)
                    currentVals.sliderVals = data.split('-')

                except Exception as e:
                    configuration.isBoardActive = False
                    print(str(e))
        print(configuration.isBoardActive,configuration.isConfigured)
        sleep(.03)
        thread = Thread(target=self.backgroundTask)
        thread.start()

