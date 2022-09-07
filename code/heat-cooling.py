#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Feb  2 20:13:38 2021
Updated on 2021/9/26

@author: laichenxm

旨在计算最大功率使用CEI OX 115-05 时不同的曝光时间-冷却时间组合（duty cycle）的稳定值。
或者根本不稳定
"""


import matplotlib.pyplot as plt
import numpy as np
from pynverse import inversefunc


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




def heat_cool(n, dt1, dt2, t1_initial):
    '''
    Parameters
    ----------
    n : int
        循环次数.
    dt1 : float
        曝光时间.
    dt2 : float
        冷却时间.
    t1_initial : float
        初始时间-在产热曲线上的时间.

    Returns 每次循环在两条曲线（产热-散热）留下的点（x坐标与 y坐标的 LIST）
    -------
    用以计算特定产热散热曲线在特定曝光冷却时间下循环稳定点

    '''
    
    xp = [0,]
    yp = [0,]
    
    t1 = t1_initial
    for i in range(n):
        h = heat(t1+dt1)
        print("h =",h)
        xp.append(t1+dt1)
        yp.append(h)
        t2 = invcooling(h)
        if 0 <= t2 <= 250: #必须符合定义域
            xp.append(t2)
            yp.append(h)
            cl = cooling(t2+dt2)
            print("cl =",cl)
            xp.append(t2+dt2)
            yp.append(cl)
        else:
            print("t2 =",t2)
            break
        t1temp = invheat(cl)
        if 0 <= t1temp <= 60: #定义域
            t1 = t1temp
            print("t1 =",t1)
            xp.append(t1)
            yp.append(cl)
        else:
            print("t1temp =",t1temp)
            break
    
    return xp, yp
    




def main():

    dt1 = 10 #单次曝光时间长度
    dt2 = 55 #单次散热时间长度
    t1_initial = 0 #产热曲线上的初始时间点
    
    xp, yp = heat_cool(3000, dt1, dt2, t1_initial) #返回循环点
   
    #定义箭头
    u = np.diff(xp)
    v = np.diff(yp)
    pos_x = xp[:-1] + u/2
    pos_y = yp[:-1] + v/2
    norm = np.sqrt(u**2+v**2) 
    
    t_cl = np.linspace(0, 300, 1000)
    t_h = np.linspace(0, 60, 500)
    cl = 0.000006*(t_cl**4) - 0.005*(t_cl**3) + 1.8279*(t_cl**2) -389.04*t_cl + 40023 
    h = -4.0346*(t_h**2) + 955.41*t_h
    
    fig = plt.figure(dpi=300)
    fig.add_axes()
    ax = fig.add_subplot(111)
    #绘出散热与产热曲线
    ax.plot(t_cl,cl,color='lightblue',linewidth=3)
    ax.plot(t_h,h,color='red',linewidth=3)
    ax.plot(xp, yp, marker="o")
    ##TODO 绘出点到点的箭头和点本身 DONE
    ax.quiver(pos_x, pos_y, u/norm, v/norm, angles="xy", zorder=5, pivot="mid")
    #最后稳定的参考线
    ax.hlines(y=[yp[-1],yp[-3]],xmin=0, xmax=300, linestyles='dotted')
    plt.show()
    


if __name__ == "__main__":
    main()        
    
    
