ver = 1.10



#%% Init stuff(Imports, const, vars)
# Imports
###################################
# Standard modules
import pathlib
import sys
import os
import datetime as dt
import time

# Custom modules


# Components


###########imprts##################


# Constants
################################### 
PATH = str(pathlib.Path(__file__).parent.resolve())
VOLUMESTEPS = (50, 40, 30, 20, 15, 10, 5, 0)
##############consts###############


# Variables
###################################

volumeLvl = 3   # 0-7, according to VOLUMESTEPS

timeSlice = dt.timedelta(minutes=25)
timeBreak = dt.timedelta(minutes=5)
slicesPerBlock = 4
##############vars#################


# Helpers
###################################

##############hlprs################


#%%###########init#################


#%% Classes
###################################

#%%###########classes##############


#%% Functions
###################################
def play_sound(volume=volumeLvl):
    """Play the alert sound via terminal program"""
    file = f'{PATH}/neg{VOLUMESTEPS[volume]}.mp3'
    os.system(f'play-audio -s notification {file} &')


def finish(delay=2.211):
    """Special alert to mark end of block"""
    time.sleep(delay)
    play_sound()
    time.sleep(delay)
    play_sound()


def oneBreak(length=timeBreak):
    """Break between slices"""
    for seconds in range(int(length.seconds)):
        os.system('clear')
        timeLeft = length - dt.timedelta(seconds=seconds)
        print(timeLeft, 'left in break')
        time.sleep(1)
    play_sound()


def oneSlice(length=timeSlice):
    """Work-'slice'"""
    for seconds in range(int(length.seconds)):
        os.system('clear')
        timeLeft = length - dt.timedelta(seconds=seconds)
        print(timeLeft, 'left in slice')
        time.sleep(1)
    play_sound()
    

def block(slices=slicesPerBlock):
    """A block of multiple slices separated by breaks"""
    for i in range(slices - 1):
        oneSlice()
        oneBreak()
    # Special case for last slice of block
    oneSlice()
    finish()
    
    
#%%###########fncts################


#%% Objects
###################################

#%%###########objcts###############




#%% Main Program
###################################
while True:
    os.system('clear')
    print('Time per slice:', timeSlice.seconds / 60, 'Minutes')
    print('Time per break:', timeBreak.seconds / 60, 'Minutes')
    print('Slices per block:', slicesPerBlock)
    print('\nEnter blank for single slice, ',
              'any other character for full block: ', sep='')
    choice = input()

    os.system('termux-wake-lock')

    # Only one slice
    if choice == '':
        oneSlice()
    
    # Full block
    else:
        block()

    os.system('termux-wake-unlock')

#%%##########main##################




    


