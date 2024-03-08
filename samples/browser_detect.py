import psutil
#import screengrab_window

browser_names = ['firefox','msedge','chrome']

def p_iter():
    while True:
        ix = 0
        for p in psutil.process_iter():
            for b in browser_names:
                if (b in p.name()):
                    print('Found ' + b)
                    # screengrab.grab(ix, b)
                ix = ix + 1
        print('looped processes')
