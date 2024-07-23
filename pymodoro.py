# Proudly written on termux in vim like a Cool Guy
## addendum: I have regrets

import os
import datetime
import time

volumeSteps = (50, 40, 30, 20, 15, 10, 5, 0)
volumeLvl = 3   # 0-7

timeSlice = datetime.timedelta(minutes=25)
timeBreak = datetime.timedelta(minutes=5)
slicesPerBlock = 4


def play_sound(volume=volumeLvl):
    file = f'./neg{volumeSteps[volume]}.mp3'
    os.system(f'play-audio -s notification {file} &')


def finish(delay=2.211):
    play_sound()
    time.sleep(delay)
    play_sound()
    time.sleep(delay)
    play_sound()

def oneSlice(lengthMinutes=timeSlice):
    for seconds in range(int(lengthMinutes.strftime('%s'))):
        os.system('clear')
        print(seconds / 60, 'Minutes done of slice')
        time.sleep(1)
    play_sound()
    for seconds in range(int(timeBreak.strftime('%s'))):
        os.system('clear')
        print(seconds / 60, 'Minutes done of break')
        time.sleep(1)
    play_sound()

def block():
    pass



while True:
    os.system('clear')
    print('Time per slice:', timeSlice.strftime('%M'), 'Minutes')
    print('Time per break:', timeBreak.strftime('%M'), 'Minutes')
    print('Slices per block:', slicesPerBlock)
    print('\nEnter blank for single slice, any other character for full block:')
    choice = input()

    # Only one slice
    if choice == '':
        oneSlice()
