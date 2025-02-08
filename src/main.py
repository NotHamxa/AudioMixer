import customtkinter
from screens import *
from trayIcons import TrayIcons
from backgroundTask import BackgroundTask
from config import configuration, currentVals

root = customtkinter.CTk()
root.geometry('1000x700')
root.resizable(False, False)
root.title('Audio Mixer')
root.protocol('WM_DELETE_WINDOW', root.withdraw)


#Function for setting all class dependencies
def setDependencies():
    trayIcons.root = root
    headerFrame.changeFrame = changeFrames
    headerFrame.configureSliderFrame = configureSliderFrame
    mainFrame.changeFrame = changeFrames
    mainFrame.configureSliderFrame = configureSliderFrame
    menuFrame.redrawSliders = mainFrame.drawSliders
    backgroundTaskHandler.redrawSliders = mainFrame.drawSliders

def changeFrames(currentScreen, newScreen):
    frames = {"menuFrame": menuFrame,
              "mainFrame": mainFrame,
              "configureSliderFrame":configureSliderFrame}
    frames[currentScreen].forget()
    frames[newScreen].pack()


trayIcons = TrayIcons()
backgroundTaskHandler = BackgroundTask()

headerFrame = HeaderFrame(root)
menuFrame = MenuFrame(root)
mainFrame = MainFrame(root)
configureSliderFrame = ConfigureSliderFrame(root)
headerFrame.pack()
mainFrame.pack()
setDependencies()

trayIcons.start()
backgroundTaskHandler.start()


root.mainloop()
