#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Aug  8 21:55:21 2022

@author: laichenxm

该脚本用于描绘球管光场。采集图像实验需保证焦点垂足在探测器中心，且探测器不旋转
"""


import matplotlib.pyplot as plt
from matplotlib import collections
import skimage.io as skio
import numpy as np
import math



#拍摄用的平板像素
pixel = 0.14 #mm
#拍摄距离
SID = 395 #mm


# This custom formatter removes trailing zeros, e.g. "1.0" becomes "1", and
# then adds a percent sign.
# 该函数用于转换数值为百分比，且小数点后0位
def fmt_percent(x):
    x = x*100
    s = f"{x:.1f}"
    if s.endswith("0"):
        s = f"{x:.0f}"
    return rf"{s} \%" if plt.rcParams["text.usetex"] else f"{s} %"


# 该函数用于转换数值为度数，且小数点后0位
def fmt_degree(x):
    s = f"{x:.1f}"
    if s.endswith("0"):
        s = f"{x:.0f}"
    return rf"{s} °" if plt.rcParams["text.usetex"] else f"{s} °"




#读入单张tif图像
im  = skio.imread("G:/X ray coverage/g7-60kv-2mA.tif", plugin="tifffile")
#计算强度百分比。归一化。
im_percent = im/np.max(im)


#根据探测器中心绘制不同像素对应的张角
row, col = np.shape(im_percent)

for i in range(row):
    for j in range(col):
        rad = math.sqrt((row/2-i)**2 + (col/2-j)**2)*pixel
        im[i,j] = math.degrees(math.atan2(rad, SID))

        

#绘图
fig, ax = plt.subplots()

#不同强度的等高线图
cs = ax.contour(im_percent, levels=[0.5, 0.8, 0.95],linewidths=0.5,cmap='spring')

#不同张角的的等高线图
cs2 = ax.contour(im, levels=[5,9,10,11,12,15,16,17,18,19,20, 25, 30],alpha=0.4,colors='gray' ,linewidths=0.3, linestyles='dashed') 




#绘出中心点                  
ax.plot([col/2], [row/2], 'o', markersize=2)

#横纵坐标尺度1比1
ax.axis('equal')
#optional 取消边框
ax.axis('off')
#optional 纵坐标逆序
ax.invert_yaxis()

#画线：横竖线
plt.hlines(row/2, 0,row, color="grey",alpha=0.3,linewidths=0.5, linestyles='dashed')
plt.vlines(col/2 ,0,row, color="grey",alpha=0.3,linewidths=0.5, linestyles='dashed')


#画线：斜线
#linewidths --> lw; linestyles --> ls 。否则报错。 

line_1 = [(0, 0), (col/2, row/2)]
line_2 = [(0, row), (col/2, row/2)]
line_3 = [(col, 0), (col/2, row/2)]
line_4 = [(col, row), (col/2, row/2)]

collection_lines = collections.LineCollection([line_1, line_2, line_3, line_4], color="grey",alpha=0.3,lw=0.5, ls='dashed')
ax.add_collection(collection_lines)

# ax.plot([100, 2800], [100, 2800],color="grey",alpha=0.3,lw=0.5, ls='dashed')
# ax.plot([200, 2872], [2872, 200],color="grey",alpha=0.3, lw=0.5, ls='dashed') 

#增加等高线的数字标记
ax.clabel(cs,fontsize=4,inline=True, inline_spacing=8, colors='black', fmt=fmt_percent)
ax.clabel(cs2,fontsize=2,inline=True, colors='blue',fmt=fmt_degree)

#增加标题
ax.set_title('Xray coverage of MK D1 #6')


#保存高清图
plt.savefig("./Xray distribution.png",dpi=600)



