import serial
from time import sleep
from config import configuration


class BackgroundTask():
    def __init__(self):
        pass

    def start(self):
        try:
            serialPort = serial.Serial()
        except Exception as e:
            pass