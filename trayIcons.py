import pystray
from images import getIconImage
from config import currentVals

class TrayIcons:
    def __init__(self):
        self.trayIcons = pystray.Icon("Audio Mixer", getIconImage(), menu=pystray.Menu(
            pystray.MenuItem("Open Window", self.trayIconHandler),
            pystray.MenuItem("Exit", self.trayIconHandler),
        ))
        self.root = None

    def start(self):
        self.trayIcons.run()

    def trayIconHandler(self, icon, item):
        if str(item) == "Exit":
            self.trayIcons.stop()
            currentVals.isAppRunning = False
            self.root.quit()
        elif str(item) == "Open Window":
            print(self.root.state())
            if self.root.state() == "normal":
                self.root.focus()
            elif self.root.state() == "withdrawn" or self.root.state() == "iconic":
                self.root.deiconify()
