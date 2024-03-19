# NoFapGuard
*The app that intervenes against lustful infractions with a distracting obstruction.*

This app runs in the background. If the app detects an inappropriate image on screen, a fullscreen window (the intervention) will prompt you to type out a verse selected randomly from the Bible to get you to cool off. It won't get out of your way until the task is complete. You then get a few seconds to quickly close your windows before the next check.

Fair warning, for anyone attempting to use this seriously to help with NoFap (or a similar commitment): **This app is not a substitute for discipline.** It takes some harsher actions against browser activity, esp. searches, via the keyword-scanning feature, with the assumption that the user is a). relying on a browser to access triggering media (because the user has already deleted anything troublesome from their computer... right? RIGHT?) and b). already has a url scanner/blocker in place against triggering websites.

## Installation
This project has a number of dependencies, so these instructions assume that you'll use a virtual environment. From within the project folder:
```
python -m venv [venv-name-here]
cd [venv-name-here]
Scripts\activate
cd ..
pip install -r requirements.txt
```

## Usage
Modify config.ini to suit your preferences. (I would advise running with default settings on the first run.) When you're ready to run (and with the virtual environment activated) run:
```
python -m main
```
If you would like to run this without a visible terminal, you can also create a .bat file with the following: 
```
@echo off
start [venv-name-here]\Scripts\pythonw.exe -m main.py
```
The app can then be closed from the system tray icon (Right-click -> Exit program).
### Image Scans
Full screenshots are taken (of multiple monitors if available) regularly, and with increased frequency when the main active window is a browser. This is a core feature of this app.

### Keyword Scans
The keyword scanner searches window titles for "unsafe" keywords (which you define in config.ini). The keyword scanner looks, particularly, for browsers where a search-engine search has just been run, and an exact match of a search against an unsafe keyword immediately triggers an intervention. A fuzzy match triggers a visual scan.

### Committed Mode
"Committed mode" (set to "True" by default) means that the user can't press Esc to close the intervention window; the window will close when the task is complete.

## Developer Notes
- Logging is **ON** by default, and this includes images. Low-res, blurred images of detections are stored in the logs/ directory for debugging purposes, and to help you choose a suitable threshold level for your needs. You may wish to delete these (and/or switch off this feature).
- The config file allows you to choose which Bible to take quotes from, and verses are selected randomly from your chosen book. With some minor modifications to interventions.py and config.ini you could substitute any csv file list of quotes of your choice.
- The app should categorise the image from multiple monitors *and* block up to two monitor screens during an intervention.
- App waits 5 seconds after an intervention before classifying again, to give you time to correct course. 

## Issues
- Not tested on cartoons / drawings
- ~~No way to stop, besides a keyboard interrupt, closing the command prompt, or Task Manager~~ *System tray icon allows modification of some config items (e.g. committedmode on/off and detection thresholds), and allows app to be turned on and off*
- Interventions only block up to 2 monitors
- Images too small / low-qual to classify: I have mitigated this with MediaPipe to 'focus in' on body parts (and crop out the rest of the screen), but MP can be thrown off by images where... "not enough"... of a body is visible. Ideally, there would be a better way to trim off the parts of a screen that aren't part of "the image".
- Sound is still on while the intervention is running.
- This is a Windows app: Mac/Linux users can possibly be catered for by swapping out DesktopMagic for [MSS](https://pypi.org/project/mss/) and writing a new set of functions for detecting window locations, getting handles, etc.
- Testing tempts developers... for most of testing, you can mitigate this by using images that trigger the detector, and not yourself, such as what you might find on an Image search for "3d model human upperbody".

## Credits
- Huge thanks to [Chris Kok for the NoFapApp](https://github.com/chriskok/NoFapApp) i.e. the inspiration for this app. 
- This app relies heavily on [Bedapudi Praneeth's NSFW Classification Project](https://github.com/notAI-tech/NudeNet), and the work he's done to classify nudity with an ensemble of neural networks.
- The ASV Bible is from [Oswin Hartono's Kaggle Dataset Contribution](https://www.kaggle.com/oswinrh/bible), the DRB Bible is a compilation from sources around the web, including Project Gutenberg and [Douay-Rheims Bible Online](https://www.drbo.org/). 

## Final
The Software and related documentation are provided "as is" and without any warranty of any kind.
