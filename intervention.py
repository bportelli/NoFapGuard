import tkinter as tk
import random
import csv
import logging
from time import sleep
from monitorsetup import get_monitors_info
from confighandler import loadConfig, lockC
#from screengrab import getfullDisplayRects_tuple, getfullDisplayRects_noscaling_tuple
#from tkinter import ttk

# Constants
# These are only loaded once at the beginning
BIBLE_VER = loadConfig(lockC)['Intervention']['bible_ver'] # 'drb' or 't_asv'
BIBLE_CONTENT = []
BG_COLOR = "#000000"
LABEL_COLOR = "#ff9966"

# Variables
committedmode = None #Initially set to None

def iscommittedmode(cm=None):
    '''Get committedmode from CONFIG (or force it via arguments)'''
    global committedmode
    if cm == None:
        if committedmode == None:
            cm = loadConfig(lockC)['Intervention']['committedmode'] == 'True'
    else:
        committedmode = cm
    return committedmode

def readVerses(verses = []):
    '''Get verses of interest from CONFIG: to filter Bible verses further'''
    try:
        verses = loadConfig(lockC)['Verse_IDs']['verses']
        verses = verses.split() # can narrow this down with random.choices(list,k) if needed
    except:
        logging.error('Verse IDs not found: using all verses.')
    return verses

def readBible():
    #with lockB:
    global BIBLE_CONTENT
    verses = readVerses()
    with open('quotebooks/' + BIBLE_VER + '.csv') as csvfile:
        readCSV = csv.reader(csvfile, delimiter=',')
        firstline = True
        for row in readCSV:
            if (firstline): 
                firstline = False
                continue
            #if (int(row[1])==1): # sticks to first book
            thr = 0.2 if row[0] in verses else 0.9
            if (random.random() >= thr):
                if len(row[4]) < 400: # Make sure it fits
                    BIBLE_CONTENT.append(row[4])
    #print('Finished Reading Bible')
    #print("Bible Content: {}".format(len(BIBLE_CONTENT)))
                
def getRandomVerse():
    #with lockB:
    global BIBLE_CONTENT
    return random.choice(BIBLE_CONTENT)

def fullscreen_popup(withcountdown = False):
    # BG_COLOR = "#cc3300"
    # LABEL_COLOR = "#ff9966"
    if withcountdown:
        cd = CountDown()
        cd.mainloop()
    intervention = InterventionCover()
    intervention.mainloop()


##### COUNTDOWN TIMER #####
class CountDown(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Countdown")
        self.geometry("%dx%d+%d+%d" % (200, 150, 100, 100))
        self.attributes("-topmost", True)
        #self.attributes("-fullscreen", True)
        self.attributes("-alpha", 0.8)
        self.overrideredirect(1)
        self.config(bg=BG_COLOR)
        #self.attributes("-disabled", True)

        # Change the text on the label every second
        message = tk.StringVar()
        message.set(str(3))
        Timer = tk.Message(self, textvariable=message,  font=("Helvetica", 32), fg="#fff", bg=BG_COLOR, width=int(self.winfo_screenwidth()) - 100,  anchor="n")
        Timer.pack(fill=tk.BOTH, side=tk.TOP)

        # Timer
        c = 3
        while c > 0:
            message.set(str(c))
            self.update()
            sleep(1)
            c -= 1

        # Close after 3 seconds
        self.after(100,self.close)

    def close(self, event=None):
        # set the running flag to False to stop updating the image
        self.running = False
        # close the window
        self.destroy()

##### COVER FOR SECOND MONITOR #####
# See: https://stackoverflow.com/questions/26286660/how-to-make-a-window-fullscreen-in-a-secondary-display-with-tkinter
# See: https://www.pythontutorial.net/tkinter/tkinter-toplevel/

#The Master Class (runs both the cover and the intervention)
class InterventionCover(tk.Tk):
    def __init__(self, monitornum=1):
        super().__init__()
        #self.master = master

        self.title("Cover")
        self.committedmode=iscommittedmode()
        monitors = get_monitors_info()
        if len(monitors) >= 2: 
            sec = list(monitors)[monitornum] # select monitor
            x1=monitors[sec][0][0]
            y1=monitors[sec][0][1]
            w1=monitors[sec][0][2]
            h1=monitors[sec][0][3]
            # print("%dx%d+%d+%d" % (w1, h1, x1, y1))
            "Can move the window via root.geometry, but it cannot be moved to full screen on the secondary monitor via root.wm_attributes('-fullscreen',True) either"
            "The fullscreen top-level window created with overrideredirect(1) can be fullscreen on the secondary screen after moving the position。"
            self.geometry("%dx%d+%d+%d" % (w1, h1, x1, y1))
            # root.wm_attributes('-fullscreen', True)
            self.overrideredirect(True)
            self.attributes("-topmost", True)
            self.resizable(0,0)
            # self.attributes("-topmost", True)
        # The following only needed if you want to make the cover appear on a single monitor, for some reason
        # else:
        #     w1=monitors[0][2]
        #     h1 = monitors[0][3]
        #     self.geometry("%dx%d+%d+%d" % (w1, h1, 0, 0))
        #     self.overrideredirect(1)
        self.bind('<Double-Button-1>', self.toggle_fullscreen)
        self.bind("<F11>", self.toggle_fullscreen)
        self.bind('<Escape>', self.close)

        # Run the intervention
        self.open_window()

        # TEST: place a button on the main window (the cover)
        # ttk.Button(self,
        #         text='Open a window',
        #         command=self.open_window).pack(expand=True)

    def open_window(self):
        window = Intervention(master=self)
        window.grab_set() # block the main window until the child window is closed

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

##### END COVER FOR SECOND MONITOR #####

class Intervention(tk.Toplevel):
    def __init__(self, master=None):
        super().__init__(master)
        
        self.committedmode = iscommittedmode()
        self.overrideredirect(True)
        self.attributes("-topmost", True)
        self.geometry("{0}x{1}+0+0".format(self.winfo_screenwidth(), self.winfo_screenheight()))

        if not self.committedmode:
            self.bind("<Escape>", self.close)
        self.config(bg=BG_COLOR)

        # LABEL
        titleLabel = tk.Label(self, text="Take a break", bg=BG_COLOR, fg=LABEL_COLOR,  font=("Ubuntu", 40))
        titleLabel.pack(fill=tk.BOTH, side=tk.TOP, pady=15, padx=60)
        titleLabel2 = tk.Label(self, text="Type out the following:", bg=BG_COLOR, fg=LABEL_COLOR,  font=("Ubuntu", 20), anchor="n")
        titleLabel2.pack(fill=tk.BOTH, side=tk.TOP, pady=10, padx=60)

        # CANVAS (currently placeholder just for space)
        # TODO: add images that would turn people off?
        canvas = tk.Canvas(self, height=10,bg=BG_COLOR, highlightthickness=0)
        canvas.pack(fill=tk.X, side=tk.TOP, pady=30)

        # MESSAGE TEXT
        message = tk.StringVar()
        try:
            # 400 char test quote:
            #quote = 'Lorem ipsum dolor sit amet, consectetur adipiscing elit. Vestibulum congue odio id urna elementum, id accumsan justo maximus. Maecenas pulvinar elit diam. Phasellus congue leo a sagittis fringilla. Aliquam eu sagittis nulla. Phasellus et orci pulvinar purus fringilla condimentum non venenatis nisi. Suspendisse venenatis dui leo, eu egestas mi tincidunt at. Pellentesque volutpat vulputate lacus et.'
            quote = getRandomVerse()
        except:
            quote = 'Remember that not getting what you want is sometimes a wonderful stroke of luck. - Dalai Lama'
        # quote = 'ZZZ'
        # quote = """Scientists have finally been able to read the oldest biblical text ever found. The 2,000-year-old scroll has been in the hands of archaeologists for decades. But it hasn’t been possible to read it, since it was too dangerous to open the charred and brittle scroll. Scientists have now been able to read it, using special imaging technology that can look into what’s inside. And it has found what was in there: the earliest evidence of a biblical text in its standardised form."""
        # Replace special quotemarks with standard quotemarks
        chars = {'‘':"'",'’':"'",'“':'"','”':'"'}
        quote = quote.translate(str.maketrans(chars))
        quote_array = quote.split(" ")
        current_split_quote = quote_array[0]
        message.set(current_split_quote)
        Instruction = tk.Message(self, textvariable=message,  font=("Helvetica", 32), fg="#fff", bg=BG_COLOR, width=int(self.winfo_screenwidth()) - 100,  anchor="nw", pady=30, padx=60)
        Instruction.pack(fill=tk.X, side=tk.TOP)

        # INPUT TEXT
        textBox=tk.Text(self, height= 5, width=1, font=("Helvetica", 20))
        textBox.pack(fill=tk.X, side=tk.BOTTOM, pady=30, padx=60)

        # This function is called whenever a key is released
        split_counter = 1
        def typing(event):
            nonlocal split_counter, current_split_quote
            curr_input = textBox.get("1.0", "end-1c") 
            # print(curr_input + " = " + current_split_quote + "?")
            if (current_split_quote in curr_input):
                if (split_counter < len(quote_array)):
                    current_split_quote += " " + quote_array[split_counter]
                    message.set(current_split_quote)
                    split_counter += 1
                else: 
                    # Completed!
                    #print("COMPLETE!!!")
                    logging.info("Intervention run and completed.")
                    self.master.destroy() # should work even when there is no parent / master window

        textBox.bind('<KeyRelease>', typing) # bind responseEntry to keyboard keys being released, and have it execute the function typing when this occurs
        textBox.focus_set()  # <-- move focus to this widget

        self.lift()

    def close(self, event=None):
        # set the running flag to False to stop updating the image
        self.running = False
        # close the window
        # self.destroy()
        self.master.destroy() # close parent window

# Keep for testing
if __name__ == "__main__":
    #from threading import Lock
    #import time
    #t = time.monotonic()
    iscommittedmode(False) # For testing, set committedmode value
    #readVerses()
    readBible()
    sleep(1)
    #print("%0.2f seconds" % (time.monotonic() - t))
    #print("Bible Content: {}".format(len(BIBLE_CONTENT)))
    
    #app = InterventionCover()
    #app.mainloop()

    fullscreen_popup(withcountdown=True)
