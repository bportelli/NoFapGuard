from time import sleep
from threading import Thread

#"chrome" in (p.name() for p in psutil.process_iter())

## Internal Modules
import browser_detect


##################
# Start the Loop

t = Thread(target=browser_detect.p_iter)  # run the some_task function in another
                              # thread
t.daemon = True               # Python will exit when the main thread
                              # exits, even if this thread is still
                              # running
t.start()


##################
# End the Loop


# Auto-timeout
#sleepafter = int(raw_input('Enter the amount of seconds you want to run this: '))
sleepafter = 2
sleep(sleepafter)