#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Feb  2 20:13:38 2021

@author: laichenxm
"""

from pynverse import inversefunc

def heat(t):
    h = -4.0346*t**2 + 955.41*t #产热
    return h

def cooling(t):
    cl = 0.000006*(t**4) - 0.005*(t**3) + 1.8279*(t**2) -389.04*t + 40023  #散热
    return cl

dt1 = 15
dt2 = 30
invheat = inversefunc(heat)
invcooling = inversefunc(cooling)


t1 = 0
for i in range(1000):
    h = heat(t1+dt1)
    print("h =",h)
    t2 = invcooling(h)
    if 0 <= t2 <= 250: #必须符合定义域
        cl = cooling(t2+dt2)
        print("cl =",cl)
    else:
        print("t2 =",t2)
        break
    t1temp = invheat(cl)
    if 0 <= t1temp <= 60: #定义域
        t1 = t1temp
        #print("t1 =",t1)
    else:
        print("t1temp =",t1temp)
        break


import matplotlib.pyplot as plt
import numpy as np

   
t = np.array(range(0,300))
y1 = 0.000006*(t**4) - 0.005*(t**3) + 1.8279*(t**2) -389.04*t + 40023 
#y2 = -4.0346*(t**2) + 955.41*t

fig = plt.figure(dpi=300)
fig.add_axes()
ax = fig.add_subplot(111)
ax.plot(t,y1,color='lightblue',linewidth=3)
#ax.plot(t,y2,color='blue',linewidth=3)