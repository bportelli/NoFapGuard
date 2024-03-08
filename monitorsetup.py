import ctypes
import ctypes.wintypes
#import win32api

MONITORS_INFO = {}

def get_monitors_info():
    """Obtain and return (x, y, width and height) and scaling factors for each monitor."""
    """Windows only."""
    global MONITORS_INFO
    # if MONITORS_INFO: # cache
    #     return MONITORS_INFO
    
    user32 = ctypes.windll.user32
    shcore = ctypes.windll.shcore
    pScale = ctypes.c_uint()
    def _get_monitors_resolution():
        monitors = {}
        monitor_enum_proc = ctypes.WINFUNCTYPE(
            ctypes.c_int, ctypes.c_ulong, ctypes.c_ulong, ctypes.POINTER(ctypes.wintypes.RECT), ctypes.c_double)
        # Callback function,to obtain information for each display
        def callback(hMonitor, hdcMonitor, lprcMonitor, dwData):
            shcore.GetScaleFactorForMonitor(hMonitor, ctypes.byref(pScale))
            monitors[str(hMonitor)] = [(lprcMonitor.contents.left, lprcMonitor.contents.top,
                             lprcMonitor.contents.right - lprcMonitor.contents.left,
                             lprcMonitor.contents.bottom - lprcMonitor.contents.top),
                             pScale.value]
            return 1
        # Enumerate all Monitors
        user32.EnumDisplayMonitors(None, None, monitor_enum_proc(callback), 0)
        return monitors
    # All monitors information
    monitors = _get_monitors_resolution()
    return monitors
# Returns, for each monitor, a tuple of (x, y, width, height) and a scaling factor, e.g.:
# {'0000000': [(0, 0, 1536, 864), 125], '00000': [(-1234, 0, 1234, 1010), 100]}

if __name__ == "__main__":
    #print_dpi()
    #sfs = getscalefactors()
    #print(sfs)
    print(get_monitors_info())

# PROCESS_PER_MONITOR_DPI_AWARE = 2
# MDT_EFFECTIVE_DPI = 0

# def print_dpi():
#     shcore = ctypes.windll.shcore
#     monitors = win32api.EnumDisplayMonitors()
#     hresult = shcore.SetProcessDpiAwareness(PROCESS_PER_MONITOR_DPI_AWARE)
#     assert hresult == 0
#     dpiX = ctypes.c_uint()
#     dpiY = ctypes.c_uint()
#     pScale = ctypes.c_uint()
#     for i, monitor in enumerate(monitors):
#         shcore.GetDpiForMonitor(
#             monitor[0].handle,
#             MDT_EFFECTIVE_DPI,
#             ctypes.byref(dpiX),
#             ctypes.byref(dpiY)
#         )
#         shcore.GetScaleFactorForMonitor(monitor[0].handle, ctypes.byref(pScale))
#         print(
#             f"Monitor {i} (hmonitor: {monitor[0]}) = dpiX: {dpiX.value}, dpiY: {dpiY.value}"
#         )
#         print(
#             f"Monitor {i} (hmonitor: {monitor[0]}) = Scale Factor: {pScale.value}"
#         )
