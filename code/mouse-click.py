#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Dec 20 15:22:47 2021

@author: laichenxm
"""


from pynput.mouse import Listener
import csv

def on_move(x, y):
    print('Pointer moved to {0}'.format((x, y)))

def on_click(x, y, button, pressed):
    if pressed:
        print('{0}'.format((x,y)))
        #return (x,y)
        with open ('./mouse_click_coord.csv','a+') as csvfile:
            writer = csv.writer(csvfile)
            xcoord, ycoord = (x,y)
            writer.writerow([xcoord, ycoord])
        
    # print('{0} at {1}'.format(
    #     'Pressed' if pressed else 'Released',
    #     (x, y)))
    # if not pressed:
    #     # Stop listener
    #     return False


def on_scroll(x, y, dx, dy):
    '返回滚动值，并结束线程'
    print('Scrolled {0}'.format((x, y)))
    #Stop listener
    return False


# def write_tocsv(tuple):
#     with open ('./mouse_click_coord.csv','w+') as csvfile:
#         writer = csv.writer(csvfile)
#         xcoord, ycoord = tuple
#         writer.writerow([xcoord, ycoord])
        
    


# Collect events until released
with Listener(
        #on_move=on_move,
        on_click=on_click,
        on_scroll=on_scroll
        ) as listener:
    listener.join()
    
# write_tocsv(on_click)