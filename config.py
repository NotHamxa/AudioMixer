import os
import json
from pydantic import BaseModel

class Configuration(BaseModel):
    isConfigured:bool = False
    isBoardActive:bool = False
    numOfSliders:int = 0
    COMPort:str = "COM5"
    baudRate:int =115200
    sliders:dict = {}

def loadConfig():
    if os.path.exists("config.json"):
        with open("conf.json", 'r') as f:
            config = json.load(f)
            configuration = Configuration(**config)
            print(configuration.model_dump())
            return
    configuration = Configuration()

ion = Configuration()

