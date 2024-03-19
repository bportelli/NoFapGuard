from time import sleep
from threading import Thread

## Internal Modules
from launchers import mainloop  #, lockB, lockK, lockC
from confighandler import loadConfig, lockC
from intervention import readBible
#from mainwindow import appwindow, lockAR
from systray import appsystray

##################
# Setup Threads
# Setup Config    
t_loadC = Thread(target=loadConfig, args=[lockC]) # add args=[lockC] to add a lock

# Setup Main Window OR System Tray Icon
#t_runM = Thread(target=appwindow, args=[lockAR])
t_runM = Thread(target=appsystray)

# Setup Keyword Check
kwCheckisOn = loadConfig(lockC)['General']['kwcheckison'] == 'True' 
if kwCheckisOn:
    from kwdetect import readKeyWords
    t_readK = Thread(target=readKeyWords)
# Setup Quotes    
t_readB = Thread(target=readBible)  # run the function in another thread

# Setup Main Loop
t_main = Thread(target=mainloop)

##################
# Start the Loop
# More info + diagram on threading: https://stackoverflow.com/questions/15085348/what-is-the-use-of-join-in-threading
# See also: https://superfastpython.com/thread-mutex-lock/

t_loadC.daemon = True
t_readB.daemon = True               # Python will exit when the main thread exits, even if this thread is still running. Set to false to keep running in the background
t_main.daemon = True
t_runM.daemon = True

if kwCheckisOn:
    t_readK.daemon = True

t_runM.start()
t_loadC.start()
t_readB.start()
if kwCheckisOn:
    t_readK.start()
    
t_main.start()

t_main.join()                      # wait for the thread to finish

##################
# End the Loop


# Auto-timeout (not currently active due to daemon / join)
#sleepafter = int(raw_input('Enter the amount of seconds you want to run this: '))
print('CLOSING...')
sleepafter = 1
sleep(sleepafter)