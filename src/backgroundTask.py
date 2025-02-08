import serial
from time import sleep, time
from src.config import configuration, currentVals
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

        self.masterVolumeSchematic = {
            0: -65.25, 1: -54.3125, 2: -49.6875, 3: -46.125, 4: -43.3125, 5: -40.9375, 6: -38.875, 7: -37.0625, 8: -35.4375, 9: -33.9375,
            10: -32.5625, 11: -31.375, 12: -30.25, 13: -29.1875, 14: -28.1875, 15: -27.25, 16: -26.375, 17: -25.5625, 18: -24.8125,
            19: -24.0625, 20: -23.3125, 21: -22.625, 22: -22.0, 23: -21.375, 24: -20.75, 25: -20.1875, 26: -19.625, 27: -19.0625,
            28: -18.5625, 29: -18.0625, 30: -17.5625, 31: -17.125, 32: -16.6875, 33: -16.25, 34: -15.8125, 35: -15.375, 36: -15.0,
            37: -14.5625, 38: -14.125, 39: -13.75, 40: -13.4375, 41: -13.125, 42: -12.75, 43: -12.375, 44: -12.0625, 45: -11.75,
            46: -11.375, 47: -11.0625, 48: -10.8125, 49: -10.5, 50: -10.1875, 51: -9.875, 52: -9.5625, 53: -9.3125, 54: -9.0625,
            55: -8.8125, 56: -8.5625, 57: -8.3125, 58: -8.0625, 59: -7.8125, 60: -7.5625, 61: -7.3125, 62: -7.0625, 63: -6.8125,
            64: -6.5625, 65: -6.3125, 66: -6.0625, 67: -5.875, 68: -5.6875, 69: -5.4375, 70: -5.1875, 71: -5.0, 72: -4.8125,
            73: -4.625, 74: -4.4375, 75: -4.1875, 76: -4.0, 77: -3.8125, 78: -3.625, 79: -3.4375, 80: -3.25, 81: -3.0625, 82: -2.875,
            83: -2.6875, 84: -2.5, 85: -2.375, 86: -2.1875, 87: -2.0, 88: -1.8125, 89: -1.625, 90: -1.5, 91: -1.3125, 92: -1.125,
            93: -1.0, 94: -0.875, 95: -0.6875, 96: -0.5, 97: -0.375, 98: -0.25, 99: -0.125, 100: 0.0
            }

        self.devices = AudioUtilities.GetSpeakers()
        self.interface = self.devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
        self.volume = cast(self.interface, POINTER(IAudioEndpointVolume))

    def freeSerialPort(self):
        self.serialPort.close()
        self.serialPort = None

    def openSerialPort(self):
        self.serialPort = serial.Serial(configuration.COMPort, configuration.baudRate, timeout=1)

    def start(self):
        thread = Thread(target=self.backgroundTask)
        thread.start()

    def setVolume(self):

        x = self.masterVolumeSchematic[int(currentVals.sliderVals[0])]
        print("Setting Master volume", x)
        self.volume.SetMasterVolumeLevel(x, None)
        print(self.volume.GetMasterVolumeLevelScalar()*100,"master volume level")
        sessions = AudioUtilities.GetAllSessions()
        for session in sessions:
            if session.Process and session.Process.name().lower() in configuration.slidersIndex:
                index = configuration.slidersIndex[session.Process.name().lower()]
                vol = int(currentVals.sliderVals[index]) / 100
                volume = session._ctl.QueryInterface(ISimpleAudioVolume)
                volume.SetMasterVolume(vol, None)

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
        sleep(.01)
        thread = Thread(target=self.backgroundTask)
        thread.start()
