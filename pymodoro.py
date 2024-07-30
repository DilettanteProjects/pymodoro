ver = 1.40



#%% Init stuff(Imports, const, vars)
# Imports
###################################
# Standard modules
import pathlib
import os
import datetime as dt
import time
import curses
import traceback

# Custom modules


# Components


###########imprts##################


# Constants
################################### 
PATH = str(pathlib.Path(__file__).parent.resolve())
SCREENWIDTH     = 83    # These are magic num-
SCREENHEIGHT    = 43    ##  bers for *my* phone
START_MOUSE_CAPTURE   = '\033[?1003h'
STOP_MOUSE_CAPTURE    = '\033[?1003l'
VOLUMESTEPS = (50, 40, 30, 20, 15, 10, 5, 0)
DEFAULT_VOLUME_LEVEL = 3 # 0-7, according to VOLUMESTEPS
DEFAULT_SILENT = False
DEFAULT_TIME_SLICE = dt.timedelta(minutes=25)
DEFAULT_TIME_BREAK = dt.timedelta(minutes=5)
DEFAULT_SLICES_PER_BLOCK = 4
##############consts###############


# Variables
###################################

##############vars#################


# Helpers
###################################

##############hlprs################


#%%###########init#################


#%% Classes
###################################
class BorderWindow():
    """Da window wit da border on it"""
    pass


class Button():
    instances = []
    def __init__(self, y, x, label, action):
        height = 10 
        width = 25
        self.label = label
        self.action = action
        self.window = curses.newwin(height, width, y, x)
        Button.instances.append(self)
    
    def print_content(self):
        self.window.clear()
        self.window.border()
        self.window.addstr(2, 2, self.label)
        self.window.refresh()


class Setting():
    #!!!(4) Can do this with list-pointers after all
    def __init__(self, value, text, ul:tuple, height, width):
        self.value = value
        self.text = text
        self.ul = ul
        self.height = height
        self.width = width
        self.window = curses.newwin(self.height, self.width, *self.ul) 
        
    def print_content(self):
        self.window.clear()
        self.window.border()
        self.window.addstr(2, 2,
                        self.text.replace('%setting',str(self.value)))
        self.window.refresh()
        
    def edit(self):
        self.window.clear()
        self.window.border()
        self.window.addstr(2, 2, 'Enter new value: ')
        curses.curs_set(1)
        curses.mousemask(0)
        curses.echo(True)
        choice = self.window.getstr()
        curses.echo(False)
        curses.mousemask(
            curses.ALL_MOUSE_EVENTS | curses.REPORT_MOUSE_POSITION)
        curses.curs_set(0)
        oldType = type(self.value)
        if oldType == dt.timedelta:
            self.value = dt.timedelta(minutes=float(choice))
        else:
            self.value = oldType(choice)
        self.print_content()
        

class Timer():
    def __init__(self, length:dt.timedelta):
        start = time.time()
        self.end = start + length.seconds
    def done(self):
        if self.end <= time.time():
            return True
        else:
            return False
    def timeLeft(self):
        return dt.timedelta(seconds=self.end - time.time()).__str__()[:7]
        
      

#%%###########classes##############


#%% Functions
###################################
distWindows = 0

settingsList = []
def setting_factory(value, text):
    rowsPerColumn = 4
    heightWindows = 5
    widthWindows = 35
    y = 0
    if len(settingsList) < rowsPerColumn:
        x = 0
        rowsThisColumn = len(settingsList)
    else:
        x = widthWindows
        rowsThisColumn = len(settingsList) - rowsPerColumn
    heightOffset = (heightWindows + distWindows) * rowsThisColumn
    newSetting = Setting(value, text, (y+heightOffset, x),
                   heightWindows, widthWindows)
    settingsList.append(newSetting)
    return newSetting


def settings_menu():
    for item in settingsList:
        stdscr.refresh()
        item.print_content()


def play_sound(volume, silent):
    """Play the alert sound/vibrate via terminal program"""
    file = f'{PATH}/neg{VOLUMESTEPS[volume]}.mp3'
    vibratePattern = (2150,)
    if not silent:
        os.system(f'play-audio -s notification {file} &')
    else:
        i = 0
        while i < len(vibratePattern):
            ms = vibratePattern[i]
            os.system(f'termux-vibrate -f -d {ms}')
            if i < len(vibratePattern) - 1:
                time.sleep(ms / 1000)
            i += 1
        

def send_notification(content):
    title = 'pymodoro'
    notifId = 'pymodoro'
    content = f"'{content}'"
    args =  f' -t {title}' +\
            f' -c {content}' +\
            f' -i {notifId}' +\
            ' --alert-once'
    os.system(f'termux-notification{args}')


def finish(delay=2.211):
    #!!! (2) Would really be nicer if all three rings were in here,
    ## because the fuction call takes variable lengths of time
    """Special alert to mark end of block"""
    time.sleep(delay)
    play_sound(volumeLvl.value, silentMode.value)
    time.sleep(delay)
    play_sound(volumeLvl.value, silentMode.value)


def shortBreak(length:dt.timedelta):
    #!!! (3) Def a case of DRY with the timekeeping in break, slice, longBreak
    """Break between slices"""
    shortBreakWin = curses.newwin(10, 40, 10, 10)
    timer = Timer(length)
    while not timer.done():
        shortBreakWin.clear()
        shortBreakWin.border()
        timeLeft = timer.timeLeft()
        shortBreakWin.addstr(2, 2, f'{timeLeft} left in break')
        send_notification(f'{timeLeft} left in break')
        shortBreakWin.refresh()
        time.sleep(1)
    play_sound(volumeLvl.value, silentMode.value)
    stdscr.refresh()


def longBreak(length:dt.timedelta=dt.timedelta(minutes=30)):
    """Break after a block"""
    longBreakWin = curses.newwin(10, 40, 10, 10)
    timer = Timer(length)
    while not timer.done():
        longBreakWin.clear()
        longBreakWin.border()
        timeLeft = timer.timeLeft()
        longBreakWin.addstr(2, 2, f'{timeLeft} left in long break')
        send_notification(f'{timeLeft} left in long break')
        longBreakWin.refresh()
        time.sleep(1)
    play_sound(volumeLvl.value, silentMode.value)
    stdscr.refresh()
    

def oneSlice(length:dt.timedelta=dt.timedelta(minutes=25)):
    """Work-'slice'"""
    sliceWin = curses.newwin(10, 40, 10, 10)
    timer = Timer(length)
    while not timer.done():
        sliceWin.clear()
        sliceWin.border()
        timeLeft = timer.timeLeft()
        sliceWin.addstr(2, 2, f'{timeLeft} left in slice')
        send_notification(f'{timeLeft} left in slice')
        sliceWin.refresh()
        time.sleep(1)
    play_sound(volumeLvl.value, silentMode.value)
    

def block(slices=4):
    """A block of multiple slices separated by breaks"""
    blockWin = curses.newwin(12, 42, 9, 9)
    for i in range(slices - 1):
        blockWin.clear()
        blockWin.border()
        blockWin.addstr(0, 2, f'Slice {i+1} of {slices}')
        blockWin.refresh()
        oneSlice(timeSlice.value)
        shortBreak(timeBreak.value)
    # Special case for last slice of block
    blockWin.clear()
    blockWin.border()
    blockWin.addstr(0, 2, f'Slice {slices} of {slices}')
    blockWin.refresh()
    oneSlice(timeSlice.value)
    finish()
    

def sliceNBreak(timeSlice=dt.timedelta(minutes=25),
                timeBreak=dt.timedelta(minutes=5)):
    oneSlice(timeSlice)
    shortBreak(timeBreak)

#%%###########fncts################


#%% Objects
###################################

#%%###########objcts###############




#%% Main Program
###################################

try:
    # Initialize curses
    stdscr = curses.initscr()
    # stdscr = curses.newwin(SCREENHEIGHT, SCREENWIDTH, 0, 0) #!!!
    stdscr.keypad(True)
    curses.echo(False)
    curses.start_color()
    curses.curs_set(0)
    curses.mousemask(curses.ALL_MOUSE_EVENTS | curses.REPORT_MOUSE_POSITION)
    # print(START_MOUSE_CAPTURE)
    
    
    # Initialize settings      
    timeSlice = setting_factory(DEFAULT_TIME_SLICE,
                                'Time per slice: %setting Minutes')
    timeBreak = setting_factory(DEFAULT_TIME_BREAK,
                                'Time per break: %setting Minutes')
    slicesPerBlock = setting_factory(DEFAULT_SLICES_PER_BLOCK, 
                             'Slices per block: %setting')
    volumeLvl = setting_factory(DEFAULT_VOLUME_LEVEL,
                                'Volume level(0-7): %setting')
    silentMode = setting_factory(DEFAULT_SILENT,
                                 'Silent mode: %setting')
    
    
    
    # Sub-window for input
    # inputWin = stdscr.derwin(6, 50, 30, 0)
    
    # Windows/Buttons for starting subroutines
    buttonY, buttonX = 30, 0
    Button(buttonY, buttonX, 'Slice', sliceNBreak)
    buttonX += 25 #!!!(5) Width of buttons(duh), make this dynamic please
    Button(buttonY, buttonX, 'Block', block) #!!! Call of block not dynamic, attribute!
    buttonX += 25 #!!!
    Button(buttonY, buttonX, 'Long Break', longBreak)#!!! Again, not dynamic!
    
    
    # Main menu
    choice = 0
    nameInput = choice
    
    # inputWin.clear()
    # inputWin.border()
    # inputWin.addstr(2, 1, 'Enter blank for single slice,')
    # inputWin.addstr(3, 1, 'any other character for full block: ')
    # inputWin.refresh()
    
    stdscr.refresh()
    while True:
        curses.flushinp()
        nameInput = choice
        stdscr.clear()
        stdscr.refresh()
        settings_menu()
        for item in Button.instances:
            item.print_content()
        
        # inputWin.clear()
        # inputWin.border()
        # # inputWin.addstr(1, 1, str(nameInput))
        # inputWin.addstr(2, 1, 'Hit return for single slice,')
        # inputWin.addstr(3, 1, 'any other character for full block: ')
        # inputWin.refresh()
        
        stdscr.refresh()
        curses.setsyx(8, 0)
        choice = stdscr.getkey()
        if choice == 'KEY_MOUSE':
            stdscr.refresh()
            choice = curses.getmouse()
            xClicked = choice[1]
            yClicked = choice[2]
            
            windowList = settingsList.copy()
            windowList.extend(Button.instances)
            
            for window in windowList:
                if window.window.enclose(yClicked, xClicked):
                    if type(window) is Setting:
                        window.edit()
                        break
                    elif type(window) is Button:
                        os.system('termux-wake-lock')
                        window.action()
                        os.system('termux-wake-unlock')
                        break
                    else:
                        raise Exception(
                            'Clicked window type recognition borked')
        
        stdscr.refresh()

# Exit handling
except BaseException as error:
    exc = error
finally:
    # Denitialize curses
    print(STOP_MOUSE_CAPTURE)
    curses.curs_set(1)
    curses.endwin()
    curses.echo(True)
    os.system('termux-wake-unlock')
    traceback.print_exception(exc)



#%%##########main##################


    


