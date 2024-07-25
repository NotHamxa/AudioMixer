import os
import customtkinter
from threading import Thread
from screens import *
from trayIcons import TrayIcons
from config import configuration

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
headerFrame = HeaderFrame(root)
menuFrame = MenuFrame(root)
mainFrame = MainFrame(root)
headerFrame.pack()
mainFrame.pack()
setDependencies()

Thread(target=trayIcons.start).start()
root.mainloop()
