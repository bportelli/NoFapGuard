
import os
import time
import logging
import random
from win32.win32gui import GetWindowText, GetForegroundWindow, GetWindowRect
from win32.win32api import MonitorFromWindow
#from threading import Lock
# Internal
from confighandler import loadConfig, lockC
from monitorsetup import get_monitors_info
from screengrab import grab_rect
from imgdetect import focus_img_on_landmarks, detect_unsafe_img, convertImgtoArray
from intervention import fullscreen_popup, countdown_popup, iswithcountdown
from debugging import blurshrinkImgArray, compareImgs, saveArrayasImgCensored # TODO: is this last one still needed?
#from mainwindow import checkapprunning
from systray import checkapprunning

## Setup Variables
# CONSTANTS
BROWSER_NAMES = ['Firefox', 'Mozilla Firefox Private Browsing', 'Microsoft\u200b Edge', 'Edge', 'Google Chrome', 'Brave']
LOGTOFILEANDIMG = loadConfig(lockC)['General']['logtofileandimg'] == 'True'
# HIGH_FREQ = 5 # wait 5 sec before checking again
# LOW_FREQ = 60 # wait 60 sec before checking again

# Setup Interventions
time_since_last_intervention = 0

# Setup Logging
if LOGTOFILEANDIMG:
    dirs = ['logs', 'logs/passing', 'logs/no-intervention']
    for directory in dirs:
        if not os.path.exists(directory):
            os.mkdir(directory)

    logging.basicConfig(
        filename="logs/logfile.log",
        format='%(asctime)s %(levelname)-8s %(message)s',
        level=logging.DEBUG,
        datefmt='%Y-%m-%d %H:%M:%S')

# Create a shared lock
# lockB = Lock() # Lock for Bible content
# lockK = Lock() # Lock for Keywords

# Setup Keyword Check
kwCheckisOn = loadConfig(lockC)['General']['kwcheckison'] == 'True' 
if kwCheckisOn:
    from kwdetect import kw_check

# Setup visual check
last_screenshot = None

# Functions
def getwindowrect(hwnd):
    '''Get the rectangle of a window'''
    rect = GetWindowRect(hwnd)
    x = rect[0]
    y = rect[1]
    w = rect[2]
    h = rect[3]

    return(x,y,w,h)

def activewindow(fgwindow=None, winrect=False, checkfreq=60, isbrowser=False, BROWSER_NAMES=BROWSER_NAMES):
    if not fgwindow:
        fgwindow = GetWindowText(GetForegroundWindow())
    # if any of the browser_names are in the active window name
    for b in BROWSER_NAMES:
        if b in fgwindow:
            isbrowser = True
            winrect = getwindowrect(GetForegroundWindow())
            winMonitorH = str(MonitorFromWindow(GetForegroundWindow()).handle) # Which monitor is this (mostly/fully) on? Return handle.
            monitorinfo = get_monitors_info()[str(winMonitorH)] 
            fontscale = monitorinfo[1] / 100
            # fix for monitor scaling (where there is none, this will be x 1)
            winrect = tuple(int(fontscale * c) for c in winrect)
            checkfreq = min(checkfreq, 5) # check again in 5 seconds (or fewer)
            break # break for loop
    # if browser_names are not in the active window name, return defaults / inputs
    return (fgwindow, winrect, checkfreq, isbrowser)

def run_intervention(censorrect=None, withcountdown=False, runintervention = True):
    global time_since_last_intervention
    global last_screenshot
    #global lockB

    last_screenshot = None # reset last screenshot

    if withcountdown:
        ## Fix censorrect for monitor scaling (NOTE: this is based on foreground window)
        winMonitorH = str(MonitorFromWindow(GetForegroundWindow()).handle) # Which monitor is this (mostly/fully) on? Return handle.
        monitorinfo = get_monitors_info()[str(winMonitorH)] 
        fontscale = monitorinfo[1] / 100
        # fix for monitor scaling (where there is none, this will be x 1)
        censorrect = tuple(int(c / fontscale) for c in censorrect)
        ##

        countdown_popup(censorrect)
        
        # Check if user has cleaned up
        fgwindow, winrect, checkfreq, isbrowser = activewindow()
        image_grabbed, winrect, fulldisplays = grab_rect(winrect)
        image = convertImgtoArray (image_grabbed)
        image, croprect, originalshape = focus_img_on_landmarks(image)
        detected = detect_unsafe_img(image) # can take a path or a numpy array / image
        runintervention = detection_threshold(detected, lockC) 
        
    if runintervention:
        fullscreen_popup()
        logging.debug('Intervention concluded / exited.')
    checkfreq = 5
    t = time.monotonic() # time at end of intervention
    time_since_last_intervention = t

    return checkfreq, t

def convertcoords(winrect, fulldisplays, convto='img'):
    x_offset = abs(fulldisplays[0])
    y_offset = abs(fulldisplays[1])
    if convto == 'img':
        # Calculate image coordinates
        coords = (winrect[0] + x_offset, winrect[1] + y_offset, winrect[2] + x_offset, winrect[3] + y_offset)
    else:
        # Calculate display coordinates
        coords = (winrect[0] - x_offset, winrect[1] - y_offset, winrect[2] - x_offset, winrect[3] - y_offset)

    return coords

def findpriorityclass(detected):
    '''Returns the detected class with the lowest threshold'''
    class_thresholds = loadConfig(lockC)['Class_Thresholds'] 
    
    # Initialise with first detected
    classfound = detected[0]
    for d in detected:
        # find the class (from detected) with the lowest threshold
        if (float(class_thresholds[d['class'].lower()]) < float(class_thresholds[classfound['class'].lower()])):
            classfound = d

    return classfound

def getdetectionrect(winrect, fulldisplays, croprect, detected):
    '''Returns a rect (on-screen location) for a detected item'''
    winrect_img = convertcoords(winrect,fulldisplays,'img')
    totalcrop = [croprect[0]+winrect_img[0], croprect[1]+winrect_img[1], croprect[2]+winrect_img[0], croprect[3]+winrect_img[1]]
    if detected:
        # Identify the "highest-priority" class (class with lowest threshold)
        classfound = findpriorityclass(detected)
        detectrect = classfound['box']
        # converting from xywh to xyxy
        detectrect = [detectrect[0], detectrect[1], detectrect[2] + detectrect[0], detectrect[3] + detectrect[1]]
        censorrect = [detectrect[0] + totalcrop[0], detectrect[1] + totalcrop[1], detectrect[2] + totalcrop[0], detectrect[3] + totalcrop[1]]
        censorrect = convertcoords(censorrect,fulldisplays,'disp')
        
    return censorrect

def detection_threshold (detected, lockC, min_threshold = 0.27):
    if not detected:
        return False # return runintervention
    
    class_thresholds = loadConfig(lockC)['Class_Thresholds']

    score, avg_score = (0, 0)
    avg_across = len(detected)
    runintervention = False # should intervention run?
    detectedclasses = []

    for d in detected:
        if (d['score'] < float(class_thresholds[d['class'].lower()])): # NOTE: .lower is needed: see loadConfig in confighandler.py
            avg_across = avg_across-1
            continue
        score = score + d['score']
        detectedclasses.append(d['class'])
        
    # Needed here as well, because of "continue"
    if (avg_across == 0): # if nothing of interest detected
        return False # return runintervention

    avg_score = score / avg_across
    if (avg_score > min_threshold):
        # Logging
        logging.info("Threshold of %.2f breached: avg. likelihood detected %.2f." % (min_threshold, avg_score))
        logging.info("Detected: {}".format(detectedclasses))
        runintervention = True
    return runintervention

def p_iter(fgwindow=None, winrect=None, checkfreq=None, isbrowser=None):
    global time_since_last_intervention
    global last_screenshot
    global lockC
    # If no inputs, get them from activewindow (check if browser is active window, or use full screen/s)
    if not fgwindow:
        fgwindow, winrect, checkfreq, isbrowser = activewindow()

    try: # force through exceptions for now (TODO: handle exceptions)
    #if True:
        #Grab screenshot
        image_grabbed, winrect, fulldisplays = grab_rect(winrect)

        # Compare current screenshot to last
        # Skip visual testing if the images are the same
        if last_screenshot is not None:
            curr_image_grabbed = blurshrinkImgArray(image_grabbed)
            diff = compareImgs(last_screenshot, curr_image_grabbed)
            if diff > 0:
                # the images are different
                #logging.debug('Images differ!')
                last_screenshot = curr_image_grabbed
            else:
                # the images are the same
                # skip visual testing
                logging.debug('Images match: skipping visual.')
                return checkfreq
        else:
            last_screenshot = blurshrinkImgArray(image_grabbed)

        #Convert image to array and correct color channels
        image = convertImgtoArray (image_grabbed)

        #Focus on landmarks (croprect: how much has the image been cropped by)
        image, croprect, originalshape = focus_img_on_landmarks(image)

        #Detect & classify unsafe elements
        detected = detect_unsafe_img(image) # can take a path or a numpy array / image
        
        # Threshold: if threshold is surpassed, run intervention
        runintervention = detection_threshold(detected, lockC)

        # If not running intervention, maybe double-check to see if it's needed...
        # Occasionally: If a browser is active (isbrowser), double-check using the grabbed image (in case MP cropped too much), or a full screenshot
        dieroll = random.random()
        if (not runintervention) and isbrowser and (dieroll >= 0.5):
            logging.debug('Double-checking...')
            if (dieroll >= 0.75): # use full screen grab if dieroll >= 0.75, otherwise use existing image_grabbed, wich may be just window
                image_grabbed_rt, rect, fulldisplays = grab_rect(False)
            else:
                image_grabbed_rt = image_grabbed 
            # Replace the current "image" that is being tested
            image = convertImgtoArray(image_grabbed_rt)
            detected = detect_unsafe_img(image) # can take a path or a numpy array / image
            runintervention = detection_threshold(detected, lockC)

        #Debugging
        # from debugging import saveArrayasImg
        # saveArrayasImg(image, filename_prefix='logs/passing/')

        #Intervention
        global LOGTOFILEANDIMG
        if runintervention:
            # Identify the location (on screen) of a detection
            if iswithcountdown():
                censorrect = getdetectionrect(winrect, fulldisplays, croprect, detected)
            else:
                censorrect = None
            #Logging
            if LOGTOFILEANDIMG:
                #from debugging import saveArrayasImgCensored
                # saves 2 versions: censored and uncensored
                fn = saveArrayasImgCensored(image, filename_prefix='logs/', small=True, detections=detected, includeuncensored=True)
                logging.info('Saved image: %s' % (fn))

            #Intervention
            checkfreq, t = run_intervention(censorrect, iswithcountdown())

        #TODO: Logging for testing / debugging - remove when done   
        elif detected: # if detected but no intervention run
            if LOGTOFILEANDIMG:
                logging.info("Detected: {}".format([d['class'] for d in detected]))
                fn = saveArrayasImgCensored(image, filename_prefix='logs/no-intervention/', small=True, detections=detected, includeuncensored=True)
                logging.info('Saved image: %s [No Intervention]' % (fn))
            checkfreq = 60

        else: # if not detected and no intervention run
            checkfreq = 60

    except:
        #print("An exception occurred when this was in foreground: " + fgwindow)
        logging.error("An exception occurred with this window in foreground: %s" % (fgwindow))
        checkfreq = 10 # check again in 10 seconds
    
    #print(time.monotonic()) # TODO: For testing
    return checkfreq

# Main Loop
def mainloop(): # call p_iter()
    #global lockK
    # first run
    checkfreq = 0
    t = time.monotonic()
    while checkapprunning():
        #logging.debug('Loop started at time: %s' % (t) + '.')
        # On every loop, check if any of the browser_names are in the active window name and, if so, update the check frequency to 5 seconds.
        fgwindow, winrect, checkfreq, isbrowser = activewindow(None, False, checkfreq, False) # only passing in check frequency

        # TODO: DEBUG / TESTING: log when window changes
        # if ('fgwindow' not in locals()) or (fgwindow2 != fgwindow):
        #     logging.debug(fgwindow2)
        #     logging.debug('Is browser: %s' % isbrowser)
        #     logging.debug('Check frequency: %d' % checkfreq)
        #     fgwindow = fgwindow2

        # Unsafe keyword check when on browser
        if time.monotonic() - time_since_last_intervention >= 4: # Give 4 sec after an intervention to clear up
            if kwCheckisOn and isbrowser:
                us_kwfound, kwissearch, kw, score = kw_check(fgwindow)
                if us_kwfound: 
                    matchtype = '%d (fuzzy match)' % (score) if score else 'exact match.'
                    windoworsearch = 'as search term' if kwissearch else 'in window'
                    logging.info('Unsafe keyword %s: %s || Match Keyword: %s || Score: %s' % (windoworsearch, fgwindow, kw, matchtype))
                    
                    # if kw is found, score is None, and keyword is a search term, then this is an exact match with a search term, so run intervention!
                    if (score == None) and kwissearch:
                        checkfreq, t = run_intervention()
                    else:
                        checkfreq = 0 if checkfreq > 5 else checkfreq # check immediately if current checkfreq setting is high, else wait (may need time to correct after intervention)

        if time.monotonic() - t >= checkfreq: 
            # if the wait time has elapsed, run again
            logging.debug('Visual check started at time: %s' % (time.monotonic()) + '.')

            checkfreq = p_iter(fgwindow, winrect, checkfreq, isbrowser)
            t = time.monotonic() # time at conclusion of p_iter
            logging.debug('Visual check ended at time: %s' % (t) + '.')

        # Sleep for 2 seconds
        time.sleep(2)

# Keep for testing
if __name__ == "__main__":
    mainloop()