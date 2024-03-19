import tkinter as tk
from threading import Lock
from confighandler import loadConfig, lockC, editConfigFile

# Variables
APPRUNNING = True
lockAR = Lock() # Lock for AppRunning

#### MAIN APP WINDOW ####
#Open Main App window (App should stop when this is closed)
def appwindow(lockAR):
    nfgapp = MainWindow()
    nfgapp.mainloop()
    with lockAR:
        global APPRUNNING
        APPRUNNING = False
        print('setting AR to FALSE')
    return

def checkapprunning():
    with lockAR:
        return APPRUNNING

#The Master Class (runs both the cover and the intervention)
class MainWindow(tk.Tk):
    def __init__(self, monitornum=1):
        super().__init__()
        #self.master = master

        self.title("NF Guard")
        self.geometry("%dx%d+%d+%d" % (200, 150, 100, 100))
        # root.wm_attributes('-fullscreen', True)
        #self.overrideredirect(True)
        self.attributes("-topmost", True)
        #self.resizable(0,0)

        self.bind('<Double-Button-1>', self.toggle_fullscreen)
        self.bind("<F11>", self.toggle_fullscreen)
        self.bind('<Escape>', self.close)

        #Place buttons on the main window to re-load + edit config
        tk.Button(self,
                text='Reload Config',
                command=self.reload_config).pack(expand=True)
        
        tk.Button(self,
                text='Edit Config',
                command=self.edit_config).pack(expand=True)
        
        
    def reload_config(self):
        loadConfig(lockC, forcereload=True)

    def edit_config(self):
        editConfigFile()


    def toggle_fullscreen(self, event=None):
        overrideredirect_value = self.overrideredirect()
        if(overrideredirect_value):
            self.overrideredirect(0)
        else:
            self.overrideredirect(1)
            
    def close(self, event=None):
        # set the running flag to False to stop updating the image
        self.running = False
        # close the window
        self.destroy()


# Keep for testing
if __name__ == "__main__":
    #print("%0.2f seconds" % (time.monotonic() - t))
    app = MainWindow()
    app.mainloop()
