# -*- coding: utf-8 -*-
"""
Created on Mon Sep 27 14:13:27 2021

@author: dx.lai
"""


import matplotlib.pyplot as plt
import numpy as np
from pynverse import inversefunc
import time


def heat(t):
    '产热曲线'
    h = -4.0346*t**2 + 955.41*t 
    return h

def cooling(t):
    '散热曲线'
    cl = 0.000006*(t**4) - 0.005*(t**3) + 1.8279*(t**2) -389.04*t + 40023  
    return cl


invheat = inversefunc(heat) #产热曲线的反函数
invcooling = inversefunc(cooling) #散热函数的反函数



dt1 = np.random.randint(1,20)



def heat_dt1(dt1, h_initial):
    '''
    Parameters
    ----------
    n : int
        循环次数.
    dt1 : float
        曝光时间.
    
    h_initial : float
        初始热容.

    Returns 
    -------
    用以计算特定产热曲线在特定曝光时间下的热容

    '''
    
    t1 = invheat(h_initial)
    if 0 <= t1 <= 60: #定义域
        h = heat(t1+dt1)
        print("h =",h)
        
    return h
        

def cool_dt2(h,dt2):
    
    t2 = invcool(h)
    if 0 <= t2 <=300:
        


