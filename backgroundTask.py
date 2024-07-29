import serial
from time import sleep, time
from config import configuration, currentVals
from threading import Thread
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume, ISimpleAudioVolume
from comtypes import CLSCTX_ALL
from ctypes import cast, POINTER
import pythoncom

def checkForBrackets(data):
    return data.startswith("(") and data.endswith(")")


def removeBrackets(data):
    data = data.replace("(", "")
    data = data.replace(")", "")
    return data



class BackgroundTask:
    def __init__(self):
        self.serialPort = None
        self.prevState = True
        self.badReads = []

        self.startReadChances = 0
        self.redrawSliders = None
        self.devices = AudioUtilities.GetSpeakers()
        self.interface = self.devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
        self.volume = cast(self.interface, POINTER(IAudioEndpointVolume))


    def mapVolume(self,vol):

        return -65 + (65 * (vol / 100))

    def freeSerialPort(self):
        self.serialPort.close()
        self.serialPort = None

    def openSerialPort(self):
        self.serialPort = serial.Serial(configuration.COMPort, configuration.baudRate, timeout=1)

    def start(self):
        thread = Thread(target=self.backgroundTask)
        thread.start()

    def setVolume(self):

        x= self.mapVolume(int(currentVals.sliderVals[0]))
        print("Setting Master volume",x)
        self.volume.SetMasterVolumeLevel(x, None)
        sessions = AudioUtilities.GetAllSessions()
        for session in sessions:
            if session.Process and session.Process.name().lower() in configuration.slidersIndex:
                index = configuration.slidersIndex[session.Process.name().lower()]
                vol = int(currentVals.sliderVals[index])/100
                print("getting volume")
                volume = session._ctl.QueryInterface(ISimpleAudioVolume)
                print("volume got")
                volume.SetMasterVolume(vol, None)
                print(f"Setting {session.Process.name() }volume {vol}")
                pass

    def backgroundTask(self):
        pythoncom.CoInitialize()
        if not currentVals.isAppRunning:
            return
        for i in range(1):
            if not currentVals.backgroundService and self.serialPort is not None:
                self.freeSerialPort()
            if not currentVals.backgroundService:
                break
            if not configuration.isConfigured:
                break

            if self.serialPort is None:
                print("tryinn shi")
                try:
                    self.openSerialPort()
                    self.serialPort.flush()
                    data = self.serialPort.read_until(b"\n").rstrip(b"\r\n").decode("utf-8")
                    if not checkForBrackets(data):
                        sleep(.02)
                        for nums in range(10):
                            self.serialPort.flush()
                            data = self.serialPort.read_until(b"\n").rstrip(b"\r\n").decode("utf-8")
                            if not data.startswith("(") and not data.endswith(")"):
                                if nums == 9:
                                    print("prob with this")
                                    configuration.isBoardActive = False
                                    self.serialPort = None
                                    self.redrawSliders()
                                    break
                            else:
                                configuration.isBoardActive = True
                            sleep(.03)
                    data = removeBrackets(data)
                    if len(data.split('-')) != configuration.numOfSliders:
                        sleep(0.02)
                        for nums in range(10):
                            data = self.serialPort.read_until(b"\n").rstrip(b"\r\n").decode("utf-8")
                            if not checkForBrackets(data):
                                sleep(.03)
                                continue
                            data = removeBrackets(data)
                            if len(data.split('-')) != configuration.numOfSliders:
                                if nums == 10:
                                    print("prob with num")
                                    configuration.isBoardActive = False
                                    self.serialPort = None
                                    self.redrawSliders()
                                    break
                            else:
                                break
                            sleep(.03)
                    self.startReadChances = 0
                    configuration.isBoardActive = True
                    self.redrawSliders()
                except serial.serialutil.SerialException as e:
                    print(e)
                    configuration.isBoardActive = False
                    self.serialPort = None
                    self.redrawSliders()
                    break
                except Exception as e:
                    self.redrawSliders()
                    break

            if configuration.isBoardActive:
                try:
                    self.serialPort.flush()
                    data = self.serialPort.read_until(b"\n").rstrip(b"\r\n").decode("utf-8")

                    if not data.startswith("(") and not data.endswith(")"):
                        self.badReads.append(int(time() + 10))
                        self.badReads = [last10 for last10 in self.badReads if last10 >= time()]
                        if len(self.badReads) >= 10:
                            configuration.isBoardActive = False
                            self.serialPort = None
                            print("wrong n of sliders")
                            self.redrawSliders()
                            break
                    data = removeBrackets(data)
                    if len(data.split('-')) != configuration.numOfSliders:
                        for nums in range(10):
                            data = self.serialPort.read_until(b"\n").rstrip(b"\r\n").decode("utf-8")
                            if not checkForBrackets(data):
                                sleep(.03)
                                continue
                            data = removeBrackets(data)
                            if len(data.split('-')) != configuration.numOfSliders:
                                if nums == 10:
                                    print("prob with num")
                                    configuration.isBoardActive = False
                                    self.serialPort = None
                                    self.redrawSliders()
                                    break
                            else:
                                break
                    currentVals.sliderVals = data.split('-')
                    self.setVolume()
                except serial.serialutil.SerialException as e:
                    print(e)
                    self.serialPort = None
                    configuration.isBoardActive = False
                    self.redrawSliders()
                except Exception as e:
                    print(f"err:{e}")
                    self.redrawSliders()
                    break
        sleep(.03)
        thread = Thread(target=self.backgroundTask)
        thread.start()
