# from desktopmagic.screengrab_win32 import (
# 	getDisplayRects, saveScreenToBmp, saveRectToBmp, getScreenAsImage,
# 	getRectAsImage, getDisplaysAsImages)
from desktopmagic.screengrab_win32 import (getDisplayRects, getRectAsImage)
from monitorsetup import get_monitors_info

def getfullDisplayRects_tuple ():
    displayrects = getDisplayRects()
    monitorsinfo = get_monitors_info() # This code will assume that the order of monitors is the same in both of these functions 
    l, t, r, b = (0,0,0,0) # left, top, right, bottom
    for i, d in enumerate(displayrects):
        # fix for monitor scaling
        monitorinfo = monitorsinfo[list(monitorsinfo)[i]]
        fontscale = monitorinfo[1] / 100
        d = tuple(int(fontscale * c) for c in d)

        l = min(l, d[0])
        t = min(t, d[1])
        r = max(r, d[2])
        b = max(b, d[3])

    return (l, t, r, b)

def getfullDisplayRects_noscaling_tuple ():
    displayrects = getDisplayRects()
    l, t, r, b = (0,0,0,0) # left, top, right, bottom
    for d in displayrects:
        l = min(l, d[0])
        t = min(t, d[1])
        r = max(r, d[2])
        b = max(b, d[3])

    return (l, t, r, b)

def grab_rect (rect):
    '''Grab a rectangular screenshot; return the image, the rect grabbed and the full display coordinates'''
    fulldisplays = getfullDisplayRects_tuple()
    if type(rect) is bool and rect is False:
        rect = fulldisplays
    imDisplay = getRectAsImage(rect)

    return imDisplay, rect, fulldisplays