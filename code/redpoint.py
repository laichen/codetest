# -*- coding: utf-8 -*-
"""
Created on Fri Dec 10 21:43:44 2021

@author: dx.lai
"""

import cv2  
import numpy as np  
from PIL import Image
import statistics
from matplotlib import pyplot as plt 


def op_one_img(img):
    '''返回图像标记红色的图像阵列和坐标点（平均化）'''
    posl = [] #坐标列表
    #蓝色通道,因为是BGR。此处无法用split() 方法，因为不是PIL IMAGE 类型
    imb = img[:,:,0] 
    imb_gray = Image.fromarray(imb)#PIL IMAGE GRAY
    imb_color = imb_gray.convert("RGB")#PIL IMAGE RGB 
    imb_color_arr = np.array(imb_color)#ndarray，便于后续上色
    tu = np.where(imb == np.max(imb)) #获取最大值坐标，可能有多个点
    
    for i in range(len(tu[0])):
        row, col = tu[0][i], tu[1][i]
        posl.append([row, col])
        imb_color_arr[row, col] = [255,0,0] #此处为RGB顺序
    row_mean = statistics.mean(tu[0]) #求平均值，下同。行号在前，一般对应y轴
    col_mean = statistics.mean(tu[1])   
    return imb_color_arr[:,:,::-1], [col_mean, row_mean]  #行列互换，对应 x和y



videoinpath  = './postp/redpoint.mp4'  
videooutpath = './postp/redpoint-new.mp4'
capture = cv2.VideoCapture(videoinpath)
fps = capture.get(cv2.CAP_PROP_FPS)
frameCount = capture.get(cv2.CAP_PROP_FRAME_COUNT)
size = (int(capture.get(cv2.CAP_PROP_FRAME_WIDTH)), int(capture.get(cv2.CAP_PROP_FRAME_HEIGHT)))
writer = cv2.VideoWriter(videooutpath, cv2.VideoWriter_fourcc(*'MP4V'), fps, size) 

position_list = []
if capture.isOpened():
    while True:
        # 注意：cv2 处理后的 img_src 是 ndarray 类型，图通道顺序为 BGR
        success,frame =capture.read()

        if not success:break
        # 函数op_one_img()逐帧处理，返回图像标记红色的图像阵列和坐标点（平均化）
        frame_out, position = op_one_img(frame)    
        position_list.append(position)
        print(position)
        print(frame.shape)
        writer.write(frame_out)
else:
    print('视频打开失败！')
writer.release()



#位移（unit：pixel）
t = np.linspace(1,len(position_list),len(position_list))
pos_arr = np.array(position_list)
x = pos_arr[:,0]
y = pos_arr[:,1]

#位移差分（unit：pixel）   
df_x = []
df_y = []
for i in range(len(x)-1):
    df_x.append(x[i+1]-x[i])
    df_y.append(y[i+1]-y[i])    
t1 = np.delete(t, len(t)-1) #减去最后一项


#绘图，位移和差分位移
fig, (ax0, ax1) = plt.subplots(nrows=2,dpi=500,figsize=(10, 8))
ax0.plot(t, x, 'o', markersize=1,label='x')
ax0.plot(t, y, 'o', markersize=1,label='y')
ax0.set_title('x and y displacement vs frame time')
ax0.legend()
# ax1.plot(t1, df_x, 'x', markersize=1,label='x diff')
# ax1.plot(t1, df_y, 'x', markersize=1,label='y diff')
ax1.plot(t1, df_x, markersize=1,label='x diff')
ax1.plot(t1, df_y, markersize=1,label='y diff')
ax1.set_title('x and y diff-displacement vs frame time')
ax1.legend()
# Add a bit more space between the two plots.
fig.subplots_adjust(hspace=0.6)
plt.show()

