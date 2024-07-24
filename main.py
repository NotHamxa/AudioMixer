import os
import customtkinter
import pystray
from threading import Thread
from images import getIconImage
from screens import *
from config import *


#Configure tkinter window
def startBackgroundService():
    root.withdraw()


root = customtkinter.CTk()
root.geometry('1000x700')
root.resizable(False, False)
root.title('Audio Mixer')
root.protocol('WM_DELETE_WINDOW', startBackgroundService)


#Function for setting frame dependencies
def setFrameDependencies():
    headerFrame.changeFrame = changeFrames


def changeFrames(currentScreen, newScreen):
    frames = {"menuFrame": menuFrame,
              "mainFrame": mainFrame, }
    frames[currentScreen].forget()
    frames[newScreen].pack()


def trayIconHandler(icon, item):
    if str(item) == "Exit":
        trayIcons.stop()
        root.quit()
    elif str(item) == "Open Window":
        print(root.state())
        if root.state() == "normal":
            root.focus()
        elif root.state() == "withdrawn" or root.state() == "iconic":
            root.deiconify()


trayIcons = pystray.Icon("Audio Mixer", getIconImage(), menu=pystray.Menu(
    pystray.MenuItem("Open Window", trayIconHandler),
    pystray.MenuItem("Exit", trayIconHandler),
))

headerFrame = HeaderFrame(root)
menuFrame = MenuFrame(root)
mainFrame = MainFrame(root)
headerFrame.pack()
setFrameDependencies()



Thread(target=trayIcons.run).start()
root.mainloop()
