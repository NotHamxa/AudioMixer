import os
import json
from pydantic import BaseModel

class CurrentVals(BaseModel):
    sliderVals:list=[]
    backgroundService:bool=True
class Configuration(BaseModel):
    isConfigured: bool = False
    isBoardActive: bool = False
    numOfSliders: int = 0
    COMPort: str = "COM5"
    baudRate: int = 115200
    sliders: dict = {}


def loadConfig():
    if os.path.exists("conf.json"):
        with open("conf.json", 'r') as f:
            config = json.load(f)
            configuration = Configuration(**config)
            print(configuration.model_dump())
            return configuration
    configuration = Configuration()
    return configuration


def saveConfig():
    with open("conf.json", "w") as confFile:
        json.dump(configuration.model_dump(), confFile)


configuration = loadConfig()
currentVals = CurrentVals()

