# -*- coding: utf-8 -*-
"""
Created on Wed Aug 24 15:29:20 2022

@author: dx.lai
"""


#import math
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.widgets import Slider


beta = 0.94  # v/c
theta = np.arange(0, 2*np.pi, 0.01)
rho = (np.power(np.sin(theta),2))/(np.power((1-beta*np.cos(theta)),5))


F, ax = plt.subplots(subplot_kw={'projection': 'polar'})  # 创建一个Figure
#axes_for_plot = F.add_axes([0.2, 0.2, 0.6, 0.6])  # 增加一个Axes，用于绘图
plot_object, = ax.plot(theta, rho)  # 在这个Axes上绘图


def slider_event(event):
    new_beta = slider_object.val  # 获取控件值
    new_rho =  (np.power(np.sin(theta),2))/(np.power((1-new_beta*np.cos(theta)),5)) # 计算更新后的数据
    plot_object.set_ydata(new_rho)  # 利用新数据更新已有的图
    


axes_for_slider = F.add_axes([0.2, 0.05, 0.6, 0.05])  # 增加一个Axes，放置滑块
slider_object = Slider(label='beta',
                       valmin=0.01, valmax=0.8, valinit=0.44,
                       ax=axes_for_slider)
slider_object.on_changed(slider_event)  # 为滑块绑定方法


plt.show()



# fig, ax = plt.subplots(subplot_kw={'projection': 'polar'})
# ax.plot(theta, rho)
# ax.grid(True)
# plt.show()


