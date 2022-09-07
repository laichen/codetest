# -*- coding: utf-8 -*-
"""
Created on Fri Dec 10 21:43:44 2021

@author: dx.lai
"""

import cv2  
import numpy as np  
#from PIL import Image
#import statistics
from matplotlib import pyplot as plt 


def twolines(lines, gap = 25):
    '选出两个最接近特定平均值的直线'
    
    lines_arr = np.array(lines)
    theta_mean = lines_arr.mean(axis=0)[1]
    for line in lines:#逐个减去平均值
            line.append(abs(line[1]-theta_mean)) #暂时添加一列用以排序
            line[1] = line[1] - theta_mean
            
    #lines.sort(key = lambda x:x[2])#按第2列即绝对值大小排序，选出最接近平均值的
    #按第2列即绝对值大小排序，选出最接近平均值的
    print('lines is', lines)
    sorted_lines = sorted(lines,key = lambda x:x[2])
    print('sorted lines is',sorted_lines) 
    #筛掉一部分截距过于接近的元素
    while True:
        if len(sorted_lines) == 2:
            print('已经到最后一个元素')# i 初次生成就不再改变，列表却每次变短
            break
        if abs(sorted_lines[0][0] - sorted_lines[1][0]) < gap:
            sorted_lines.pop(1)
        else:
            print('已找到适配的元素')
            break
        
    twolines = sorted_lines[0:2] #取最接近平均值的两个
    for twoline in twolines:#逐个加上平均值
        twoline[1] = twoline[1] + theta_mean
        twoline.pop() #此处去掉之前暂时添加的一列
            
    return twolines

def cleanlines(lines):
    '''
    清除重复的线条
    
    '''
    if len(lines) == 4:
        print('nice!')
        
    elif len(lines) < 4:
        raise ValueError('错误：找不到足够的直线！')
    
    else:
        print('输入最初直线：',lines)
   
        hlines = []
        vlines = []
        # lines_arr = np.array(lines)
        # theta_mean = lines_arr.mean(axis=0)[1]
        for line in lines:
            if abs(line[1]) < 0.2:
                hlines.append(line)
            else:
                vlines.append(line)
       
        twohlines = twolines(hlines)
        twovlines = twolines(vlines) 
        lines = twohlines + twovlines
        
        
    return lines

def IntersectionPoints(lines):  
    #求出交点
    points = []
    if(len(lines)==4):
        horLine = []
        verLine = []
        for line in lines:
            if abs(line[1]) < 0.2:
                horLine.append(line)
            else:
                verLine.append(line)
        #print(horLine)
        for l1 in horLine:
            for l2 in verLine:
                a = np.array([
                    [np.cos(l1[1]), np.sin(l1[1])],
                    [np.cos(l2[1]), np.sin(l2[1])]
                ])
                b = np.array([l1[0],l2[0]])
                points.append(np.linalg.solve(a, b))
        return points
    else:
        print("the number of lines error")


def op_one_img(img):
    '''
    用以处理单帧图像的函数
    Parameters
    ----------
    img : ndarray 
        格式的图像矩阵 BGR.

    Returns
    -------
    含图像标记的图像阵列, 坐标点
    
    
    '''
    #posl = [] #坐标列表
    #红色通道,因为是BGR。此处无法用split() 方法，因为不是PIL IMAGE 类型
    imr = img[:,:,2] 
    gimg = cv2.GaussianBlur(imr, (5, 5), 0)
    gret, gim2 = cv2.threshold(gimg, 0, 255, cv2.THRESH_BINARY+cv2.THRESH_OTSU)
    #plt.imshow(gim2, plt.cm.gray)
    edges = cv2.Canny(gim2, 45,135)
    
    minLineLength = 20
    maxLineGap = 15
    lines = cv2.HoughLinesP(edges, 1, np.pi/180, 60, 0, minLineLength, maxLineGap)
    
    #将"两点式" 转为 rho - theta 式
    newlines = []
    for line in lines:
        
        theta = np.arctan((line[0][2]-line[0][0])/(line[0][1]-line[0][3]))
        rho = line[0][0]*np.cos(theta) + line[0][1]*np.sin(theta)
        newlines.append([rho, theta])
    
    print('ORIGINAL lines is', newlines)
    #得到四条线
    fourlines = cleanlines(newlines)
    #画四条线
    for line in fourlines:
        rho, theta = line
        #print(rho, theta)
        a = np.cos(theta)
        b = np.sin(theta)
        x0 = a*rho
        y0 = b*rho
        x1 = int(x0 + 2000*(-b))
        y1 = int(y0 + 2000*(a))
        x2 = int(x0 - 2000*(-b))
        y2 = int(y0 - 2000*(a))
        #img = img[:,:,::-1]
        cv2.line(img,(x1, y1), (x2, y2), (0, 255, 0), 2) 
    
    #求四个交点    
    points = IntersectionPoints(fourlines)        
    #画四个点
    for point in points:
        cv2.circle(img, (int(point[0]),int(point[1])), 10, (0,255,0),-1)
        
    #求中心点    
    midx = np.mean([point[0] for point in points])
    midy = np.mean([point[1] for point in points])
    #画中心点
    cv2.circle(img, (int(midx), int(midy)), 10, (255,255,255),-1)
    
    
    
    return img[:,:,::-1], [midx, midy]  #BGR to RGB



def info_plt(position_list):
    '''
    用于绘出坐标点变化的功能函数

    Parameters
    ----------
    position_list : list
        每帧图片激光中心点的坐标列表.

    Returns
    -------
    None.

    '''
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
    df_x = np.array(df_x)
    df_y = np.array(df_y)
    
    
    #绘图，位移和差分位移
    dx = 0.048   # unit:mm/pixel
    dy = 0.062  # unit:mm/pixel
    fig, (ax0, ax1) = plt.subplots(nrows=2,dpi=500,figsize=(10, 8))
    ax0.plot(t, x*dx, 'o', markersize=1,label='x')
    ax0.plot(t, y*dy, 'o', markersize=1,label='y')
    ax0.set_xlabel('frame number')
    ax0.set_ylabel('mm')
    ax0.set_title('x and y displacement vs frame time')
    ax0.legend()
    # ax1.plot(t1, df_x, 'x', markersize=1,label='x diff')
    # ax1.plot(t1, df_y, 'x', markersize=1,label='y diff')
    ax1.plot(t1, df_x*dx, markersize=1,label='x diff')
    ax1.plot(t1, df_y*dy, markersize=1,label='y diff')
    ax1.set_xlabel('frame number')
    ax1.set_ylabel('mm')
    ax1.set_title('x and y diff-displacement vs frame time \n (dx: %.3f mm/pixel; dy: %.3f mm/pixel)'%(dx,dy))
    ax1.legend()
    # Add a bit more space between the two plots.
    fig.subplots_adjust(hspace=0.6)
    plt.show()
    
    return None 


def mian():
    #视频位置
    videoinpath  = '/Users/laichenxm/Downloads/11s-c.mov'
    videooutpath = '/Users/laichenxm/Downloads/11s-c-new.mov'
    capture = cv2.VideoCapture(videoinpath)
    fps = capture.get(cv2.CAP_PROP_FPS)
    #frameCount = capture.get(cv2.CAP_PROP_FRAME_COUNT)
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
            #print(position)
            #print(frame.shape)
            writer.write(frame_out)
    else:
        print('视频打开失败！')
    writer.release()

    info_plt(position_list)




if __name__ == '__main__':
    mian()

