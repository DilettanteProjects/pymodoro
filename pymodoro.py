# V 1.05
# Proudly written on termux in vim like a Cool Guy
## addendum: I have regrets

import os
import datetime as dt
import time
import pathlib

PATH = str(pathlib.Path(__file__).parent.resolve())

volumeSteps = (50, 40, 30, 20, 15, 10, 5, 0)
volumeLvl = 3   # 0-7

timeSlice = dt.timedelta(minutes=25)
timeBreak = dt.timedelta(minutes=5)
slicesPerBlock = 4


def play_sound(volume=volumeLvl):
    file = f'{PATH}/neg{volumeSteps[volume]}.mp3'
    os.system(f'play-audio -s notification {file} &')


def finish(delay=2.211):
    time.sleep(delay)
    play_sound()
    time.sleep(delay)
    play_sound()


def oneBreak(length=timeBreak):
    for seconds in range(int(length.seconds)):
        os.system('clear')
        timeLeft = length - dt.timedelta(seconds=seconds)
        print(timeLeft, 'left in break')
        time.sleep(1)
    play_sound()


def oneSlice(length=timeSlice):
    for seconds in range(int(length.seconds)):
        os.system('clear')
        timeLeft = length - dt.timedelta(seconds=seconds)
        print(timeLeft, 'left in slice')
        time.sleep(1)
    play_sound()
    


def block(slices=slicesPerBlock):
    for i in range(slices - 1):
        oneSlice()
        oneBreak()
    # Special case for last slice of block
    oneSlice()
    finish()
    

while True:
    os.system('clear')
    print('Time per slice:', timeSlice.seconds / 60, 'Minutes')
    print('Time per break:', timeBreak.seconds / 60, 'Minutes')
    print('Slices per block:', slicesPerBlock)
    print('\nEnter blank for single slice, any other character for full block:')
    choice = input()

    os.system('termux-wake-lock')

    # Only one slice
    if choice == '':
        oneSlice()
    
    # Full block
    else:
        block()

    os.system('termux-wake-unlock')
