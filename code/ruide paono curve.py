# -*- coding: utf-8 -*-
"""
Created on Mon Apr 25 11:26:37 2022

@author: dx.lai
"""


import numpy as np
import matplotlib.pyplot as plt
import xlrd


#获取excel表格中的速度值
def getcol_fromxl(directory,sheetindex,colindex):
    '''
    

    Parameters
    ----------
    directory : string
        Excel 文件地址，仅支持.xls，斜杠/
    sheetindex : int
        表序号，从0开始.
    colindex : int
        栏序号，从0开始.

    Returns
    -------
    cols: list
        读取的列

    '''
    worksheet = xlrd.open_workbook(directory)
    #sheet_names = worksheet.sheet_names() #返回sheet的name 
    #print(sheet_names)
    sheet = worksheet.sheet_by_index(sheetindex) # 取第1个sheet页data
    cols = sheet.col_values(colindex)
    print(cols)
    
    while type(cols[0]) == str:
        cols.pop(0)
        
    return np.array(cols)

#将速度列表转为累计位移列表
def v2disp(vlist,time_interval):
    '''
    

    Parameters
    ----------
    vlist : list
        速度或者角速度列表.
    time_interval : float
        时间间隔，对应速度列表的每个速度.

    Returns
    -------
    disp : list
        累计位移列表.

    '''
    
    disptemp = [v * time_interval for v in vlist]

    disp = [0]*140
    # for i in range(len(vlist)):
    #     disptemp[i] = vlist[i] * time_interval
        
    for i in range(len(vlist)):
        disp[i] = sum(disptemp[0:i+1])
    
    return np.array(disp)

#角度转弧度
def degree2rad(degree):
    return degree/180*np.pi


#目录    
directory = 'E:/项目/MK D1/2.MK D1 系统/电气/运动/瑞德全景 v-t曲线.xls'

#基本参数
Uni_circular_motion = True #是否使用匀速圆周运动
T = 14 # run time, unit:s
t_interval = 0.05
t = np.arange(0, T/2, t_interval)
OID = 160 # Object to Imager Distance, unit:mm
SAD = 400 # mm
SID = SAD + OID
angle = 220 # rotation angle, unit:degree
omega = angle/T # angle velocity, unit:degree/s
degree_offset = -20


velo = getcol_fromxl(directory,1,2) #速度
vdisp = v2disp(velo,t_interval) #位移

wvelo = getcol_fromxl(directory, 1, 1) #角速度
wvdisp = v2disp(wvelo,t_interval) #角度位移


#坐标 
if Uni_circular_motion:#匀速圆周运动
    x = OID * np.cos(degree2rad(omega*t + degree_offset))
    y = OID * np.sin(degree2rad(omega*t + degree_offset)) + vdisp
else:
    x = OID * np.cos(degree2rad(wvdisp + degree_offset))
    y = OID * np.sin(degree2rad(wvdisp + degree_offset)) + vdisp


x_n = OID * np.cos(degree2rad(wvdisp + degree_offset))
y_n = OID * np.sin(degree2rad(wvdisp + degree_offset)) + vdisp


#绘图
# fig, ax = plt.subplots(3,figsize=(7,10))
# plt.subplots_adjust(left=None, bottom=None, right=None, top=None, wspace=None, hspace=0.3)
# fig.suptitle('About pano motor movement of Ruide')


fig, axd = plt.subplot_mosaic([['upper left', 'right'],
                               ['lower left', 'right']],
                              figsize=(11, 7), constrained_layout=True)

plt.subplots_adjust(left=None, bottom=None, right=None, top=None, wspace=0.3, hspace=0.3)
fig.suptitle('About pano motor movement of Ruide')



axd['right'].plot(x[0:140], y[0:140], linewidth=1.0, color='blue',label='uniform circular')
# ax.plot(x[0:100], y[0:100], linewidth=2.0, color='red')
# ax.plot(x[0:70], y[0:70], linewidth=2.0, color='green')
# ax.plot(x[0:50], y[0:50], linewidth=2.0)
# ax.plot(x[0:30], y[0:30], linewidth=2.0, color='magenta')
axd['right'].plot(x_n[0:140], y_n[0:140], linestyle='dashed', linewidth=1.0, color='red',label='un-uniform')
axd['right'].set_xlabel('unit: mm')  # Add an x-label to the axes.
axd['right'].set_ylabel('unit: mm')  # Add a y-label to the axes.
axd['right'].set_title("half trace of FPD in pano mode (anti-clockwise)")  # Add a title to the axes.
axd['right'].axis('equal') #坐标轴尺度 equal
axd['right'].legend()


axd['upper left'].plot(t, vdisp, linewidth=1.0, color='black',label='pan displacement')
axd['upper left'].set_xlabel('unit: s')  # Add an x-label to the axes.
axd['upper left'].set_ylabel('unit: mm')  # Add a y-label to the axes.
axd['upper left'].set_title("pan displacement vs time")  # Add a title to the axes.

axd['lower left'].plot(t, wvdisp, linewidth=1.0, color='black',label='rotation displacement')
axd['lower left'].set_xlabel('unit: s')  # Add an x-label to the axes.
axd['lower left'].set_ylabel('unit: degree')  # Add a y-label to the axes.
axd['lower left'].set_title("rotation displacement vs time")  # Add a title to the axes.

plt.savefig('./halftrace-info-1.png', dpi=300)
plt.show()





