# -*- coding: utf-8 -*-
"""
Created on Fri Jul  8 11:54:00 2022

@author: dx.lai
"""


import skimage.io as skio
import matplotlib.pyplot as plt
import numpy as np


#输入图像 tiff格式，单张
imstack1 = skio.imread("G:/No6_Sprint/20220708_Tube_Angle_Height_and_FoL/NO3-Prototype-22-04-01-rad-gain-int-g4-30.0fps.tif", plugin="tifffile")   

#设置阈值
threshold = 1.3

#遍历图像，大于阈值的赋黑，小于则白
imthreshold = np.zeros(shape=imstack1.shape)
for index, pixel in np.ndenumerate(imstack1): 
    x, y = index
    if imstack1[x, y] >= threshold:
        imthreshold[x, y] = 0
    else:
        imthreshold[x, y] = 255
                
#画图
#plt.imshow(imstack1,cmap = 'gray')
plt.imshow(imthreshold,cmap = 'gray')
