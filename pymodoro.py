ver = 1.75


# Init stuff(Imports, const, vars)
#region
# Imports
###################################
# Standard modules
import pathlib
import os
import datetime as dt
import time
import curses
import traceback
import pickle

# Custom modules


# Components


###########imprts##################


# Constants
################################### 
PATH = str(pathlib.Path(__file__).parent.resolve())
NOTIF_ID = 'pymodoro'
SCREENWIDTH     = 83    # These are magic num-
SCREENHEIGHT    = 43    ##  bers for *my* phone
START_MOUSE_CAPTURE   = '\033[?1003h'
STOP_MOUSE_CAPTURE    = '\033[?1003l'
VOLUMESTEPS = (50, 40, 30, 20, 15, 10, 5, 0)
DEFAULT_VOLUME_LEVEL = 3     # 0-7, according to VOLUMESTEPS
DEFAULT_SILENT = False
DEFAULT_TIME_SLICE = dt.timedelta(minutes=25)
DEFAULT_TIME_SHORT_BREAK = dt.timedelta(minutes=5)
DEFAULT_TIME_LONG_BREAK = dt.timedelta(minutes=30)
DEFAULT_SLICES_PER_BLOCK = 4
DEFAULT_LEAN_MODE = True
DEFAULT_NOTIFICATION_PRIORITY = 'default'
NOTIFICATION_PRIORITY_OPTIONS = ('max', 'high', 'default', 'low', 'min')
##############consts###############


# Variables
###################################
ptrVolumeLvl = [DEFAULT_VOLUME_LEVEL]
ptrSilentMode = [DEFAULT_SILENT]
ptrTimeSlice = [DEFAULT_TIME_SLICE]
ptrTimeShortBreak = [DEFAULT_TIME_SHORT_BREAK]
ptrTimeLongBreak = [DEFAULT_TIME_LONG_BREAK]
ptrSlicesPerBlock = [DEFAULT_SLICES_PER_BLOCK]
ptrLeanMode = [DEFAULT_LEAN_MODE]
ptrNotifPrio = [DEFAULT_NOTIFICATION_PRIORITY]
##############vars#################


# Helpers
###################################

##############hlprs################

#endregion
##############init#################

# Classes
#region
###################################
class BorderWindow:
    """Da window wit da border on it"""
    pass

class Button:
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

class Setting:
    #!!!(4) Can do this with list-pointers after all
    def __init__(self, pointer, text, ul:tuple, height, width):
        self.pointer = pointer
        self.text = text
        self.ul = ul
        self.height = height
        self.width = width
        self.window = curses.newwin(self.height, self.width, *self.ul) 
        
    def print_content(self):
        self.window.clear()
        self.window.border()
        self.window.addstr(2, 2,
                        self.text.replace('%setting',str(self.pointer[0])))
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
        
        oldType = type(self.pointer[0])
        if oldType == dt.timedelta:
            newValue = dt.timedelta(minutes=float(choice))
        elif oldType == bool:
            newValue = bool(int(choice))
        else:
            newValue = oldType(choice)
        self.pointer.clear()
        self.pointer.append(newValue)
        
        self.print_content()


class CycleSetting(Setting):
    """Setting that cycles through valid settings instead of taking input"""
    def __init__(self, pointer, text, change, states:tuple,
                 ul:tuple, height, width):
        super().__init__(pointer, text, ul, height, width)
        self.change = change
        self.states = states

    def edit(self):
        self.window.clear()
        self.window.border()
        position = self.states.index(self.pointer[0])
        if position + 1 == len(self.states):
            newValue = self.states[0]
        else:
            newValue = self.states[position + 1]
        self.pointer.clear()
        self.pointer.append(newValue)
        self.print_content()


distWindows = 0
settingsList = []
def setting_factory(pointer, text, change='manual', states=None):
    rowsPerColumn = 4
    heightWindows = 5
    widthWindows = 40
    y = 0
    #
    if len(settingsList) < rowsPerColumn:
        x = 0
        rowsThisColumn = len(settingsList)
    else:
        x = widthWindows
        rowsThisColumn = len(settingsList) - rowsPerColumn
    heightOffset = (heightWindows + distWindows) * rowsThisColumn
    #
    ul = (y+heightOffset, x)
    if change == 'manual':
        newSetting = Setting(pointer, text, ul, heightWindows, widthWindows)
    elif change == 'cycle':
        newSetting = CycleSetting(pointer, text, change, states,
                                  ul, heightWindows, widthWindows)
    else:
        raise Exception('Invalid "change type" for Setting')
    #
    settingsList.append(newSetting)
    return newSetting


def settings_menu():
    for item in settingsList:
        stdscr.refresh()
        item.print_content()    
  
    

class Timer:
    def __init__(self, length):
        start = time.time()
        self.end = start + length.seconds
    def done(self):
        if self.end <= time.time():
            return True
        else:
            return False
    def time_left(self):
        return dt.timedelta(seconds=self.end - time.time()).__str__()[:7]



#endregion
##############classes##############

# Functions
#region
###################################
def round_off(number):
    if number % 5 == 0:
        return number - 5
    else:
        return number - (number % 5)


def save_settings():
    #!!!(6) Both save and load could be a lot more dynamic. Or at all dynamic
    settingsDict = { 'volumeLvl'      : ptrVolumeLvl[0],
                     'silentMode'     : ptrSilentMode[0],
                     'timeSlice'      : ptrTimeSlice[0],
                     'timeShortBreak' : ptrTimeShortBreak[0],
                     'timeLongBreak'  : ptrTimeLongBreak[0],
                     'slicesPerBlock' : ptrSlicesPerBlock[0],
                     'leanMode'       : ptrLeanMode[0],
                     }
    with open(f'{PATH}/settings.pkl', 'wb') as file:
        pickle.dump(settingsDict, file)


def load_settings():
    def set_val(ptr:list, newVal):
        ptr.clear()
        ptr.append(newVal)
    with open (f'{PATH}/settings.pkl', 'rb') as file:
        settingsDict = pickle.load(file)
    set_val(ptrVolumeLvl, settingsDict['volumeLvl'])
    set_val(ptrSilentMode, settingsDict['silentMode'])
    set_val(ptrTimeSlice, settingsDict['timeSlice'])
    set_val(ptrTimeShortBreak, settingsDict['timeShortBreak'])
    set_val(ptrTimeLongBreak, settingsDict['timeLongBreak'])
    set_val(ptrSlicesPerBlock, settingsDict['slicesPerBlock'])
    set_val(ptrLeanMode, settingsDict['leanMode'])


def play_sound():
    """Play the alert sound/vibrate via terminal program"""
    volume = ptrVolumeLvl[0]
    silent = ptrSilentMode[0]
    file = f'{PATH}/resources/vam-{VOLUMESTEPS[volume]}.mp3'
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
    content = f"'{content}'"
    args =  f' -t {title}' +\
            f' -c {content}' +\
            f' -i {NOTIF_ID}' +\
            f' --priority {ptrNotifPrio[0]}' +\
            ' --alert-once'
    os.system(f'termux-notification{args}')


def finish(delay=2.211):
    #!!! (2) Would really be nicer if all three rings were in here,
    ## because the fuction call takes variable lengths of time
    """Special alert to mark end of block"""
    time.sleep(delay)
    play_sound()
    time.sleep(delay)
    play_sound()


def time_keeper(kind:str):
    """Universal countdown handler"""
    match kind:
        case 'slice':
            length = ptrTimeSlice[0]
        case 'short break':
            length = ptrTimeShortBreak[0]
        case 'long break':
            length = ptrTimeLongBreak[0]
        case _:
            raise Exception('Invalid {kind} of timer')

    countdownWin = curses.newwin(10, 40, 10, 10)

    timer = Timer(length)
    while not timer.done():
        timeLeft = timer.time_left()

        # Lean mode
        if ptrLeanMode[0]:
            minutesLeft = int(timeLeft[2:4])
            if minutesLeft > 6:
                countdownWin.clear()
                countdownWin.border()
                countdownWin.addstr(2, 2,
                                    f'< {minutesLeft + 1}min left in {kind}')
                send_notification(f'< {minutesLeft + 1}min left in {kind}')
                countdownWin.refresh()
                time.sleep(60 * 5)
            else:
                ptrLeanMode[0] = False

        # Real-time mode
        else:
            countdownWin.clear()
            countdownWin.border()
            countdownWin.addstr(2, 2, f'{timeLeft} left in {kind}')
            send_notification(f'{timeLeft} left in {kind}')
            countdownWin.refresh()
            time.sleep(1)

    # Finishing up
    play_sound()
    stdscr.refresh()


def block(slicesPtr=ptrSlicesPerBlock):
    """A block of multiple slices separated by breaks"""
    slices = slicesPtr[0]
    blockWin = curses.newwin(12, 42, 9, 9)
    for i in range(slices - 1):
        blockWin.clear()
        blockWin.border()
        blockWin.addstr(0, 2, f'Slice {i+1} of {slices}')
        blockWin.refresh()
        time_keeper('slice')
        time_keeper('short break')
    # Special case for last slice of block
    blockWin.clear()
    blockWin.border()
    blockWin.addstr(0, 2, f'Slice {slices} of {slices}')
    blockWin.refresh()
    time_keeper('slice')
    finish()
    

def slice_n_break():
    time_keeper('slice')
    time_keeper('short break')

#endregion
##############fncts################

# Objects
#region
###################################

#endregion
##############objcts###############



# Main Program
#region
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
    
    
    if os.path.exists(f'{PATH}/settings.pkl'):
        load_settings()
    
    # Initialize settings      
    timeSlice = setting_factory(ptrTimeSlice,
                                'Time per slice: %setting Mins')
    timeShortBreak = setting_factory(ptrTimeShortBreak,
                                'Time per short break: %setting Mins')
    timeLongBreak = setting_factory(ptrTimeLongBreak,
                                'Time per long break: %setting Mins')
    slicesPerBlock = setting_factory(ptrSlicesPerBlock, 
                             'Slices per block: %setting')
    volumeLvl = setting_factory(ptrVolumeLvl,
                                'Volume level(0-7): %setting')
    silentMode = setting_factory(ptrSilentMode,
                                 'Silent mode: %setting', 'cycle',
                                 (True, False))
    leanMode = setting_factory(ptrLeanMode,
                               'Lean mode: %setting', 'cycle',
                               (True, False))
    notifPrio = setting_factory(ptrNotifPrio,
                                'Notification priority: %setting', 'cycle',
                                NOTIFICATION_PRIORITY_OPTIONS)
    
    
    
    # Windows/Buttons for starting subroutines
    buttonY, buttonX = 30, 0
    Button(buttonY, buttonX, 'Slice', slice_n_break)
    buttonX += 25 #!!!(5) Width of buttons(duh), make this dynamic please
    Button(buttonY, buttonX, 'Block', block) #!!! Call of block not dynamic, attribute!
    buttonX += 25 #!!!
    Button(buttonY, buttonX, 'Long Break',
           lambda: time_keeper('long break'))   #!!! Again, not dynamic!
    
    
    # Main menu
    choice = 0
    nameInput = choice
    
   
    stdscr.refresh()
    while True:
        curses.flushinp()
        nameInput = choice
        stdscr.clear()
        stdscr.refresh()
        settings_menu()
        for item in Button.instances:
            item.print_content()
        
       
        
        stdscr.refresh()
        curses.setsyx(8, 0)
        choice = stdscr.getkey()
        windowList = settingsList.copy()
        windowList.extend(Button.instances)
        
        if choice == 'KEY_MOUSE':
            stdscr.refresh()
            choice = curses.getmouse()
            xClicked = choice[1]
            yClicked = choice[2]
            

            for window in windowList:
                if window.window.enclose(yClicked, xClicked):
                    if type(window) is Setting or type(window) is CycleSetting:
                        window.edit()
                        save_settings()
                        break
                    elif type(window) is Button:
                        os.system('termux-wake-lock')
                        window.action()
                        send_notification('All timers done!')
                        os.system('termux-wake-unlock')
                        break
                    
        elif choice == '\n':
            for window in windowList:
                window.print_content()
                window.window.redrawwin()
            stdscr.redrawwin()
            stdscr.refresh()
                        
        for item in Button.instances:
            item.print_content()
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
    os.system(f'termux-notification-remove {NOTIF_ID}')
    os.system('termux-wake-unlock')
    traceback.print_exception(exc)



#endregion
#############main##################

    


