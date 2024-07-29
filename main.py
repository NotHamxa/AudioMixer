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
    menuFrame.redrawSliders = mainFrame.drawSliders


def changeFrames(currentScreen, newScreen):
    frames = {"menuFrame": menuFrame,
              "mainFrame": mainFrame, }
    frames[currentScreen].forget()
    frames[newScreen].pack()


trayIcons = TrayIcons()
backgroundTaskHandler = BackgroundTask()

headerFrame = HeaderFrame(root)
menuFrame = MenuFrame(root)
mainFrame = MainFrame(root)
headerFrame.pack()
mainFrame.pack()
setDependencies()

Thread(target=trayIcons.start).start()
if configuration.isConfigured:
    try:
        backgroundTaskHandler.start()
    except Exception as e:
        pass


def sd():
    print(currentVals.sliderVals)
    root.after(200, sd)

root.after(200, sd)
root.mainloop()
