# -*- coding: utf-8 -*-
"""
Created on Fri Jul  1 13:56:37 2022

@author: dx.lai
"""


import skimage.io as skio
from skimage.filters import threshold_isodata
from skimage.transform import hough_circle, hough_circle_peaks
#import skimage.color as skic
# import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import logging
import traceback



#处理单帧图像的函数
#简单遍历得到钨丝的第一个点
def op_one_img_pin(img):
    thresh = threshold_isodata(img) #确定二值化的阈值，使用isodata方法
    binary = img > thresh #产生二值化图像
    col, row = binary.shape
    for i in range(col):
        for j in range(row):
            if binary[i,j] == False: #找到第一个为0的值
                return i,j
                break
    
                
    #tu = np.where(im == np.max(im)) #获取最大值坐标，可能有多个点

#处理单帧图像2
#利用霍夫变换识别圆形并得到圆心坐标
def op_one_img_ball(img,hough_radii):
    thresh = threshold_isodata(img) #确定二值化的阈值，使用isodata方法
    binary = img > thresh #产生二值化图像
    hough_res = hough_circle(binary, hough_radii)
    accums, cx, cy, radii = hough_circle_peaks(hough_res, hough_radii,total_num_peaks=1) 
    return float(cx), float(cy)


#差分计算
def diff_list(list):
    zero = 0    
    df_list = []
    for i in range(len(list)-1):
        df_list.append(list[i+1]-list[i])         

    #df_list = np.array(df_list)
    df_list.append(zero) # 补齐规格
    return df_list




#写入excel
def lists_to_excel(filename="./Xray pointer curve.xlsx",sheetname="W wire point position",**kwargs):
    #kwargs 本质是个字典，key：vlaue 
    
    df = pd.DataFrame(kwargs)
    df.to_excel(filename, sheet_name=sheetname)
    


def calc():
    # 引入日志
    logging.basicConfig(filename='log_record.txt',
                        level=logging.DEBUG, filemode='w', 
                        format='[%(asctime)s] [%(levelname)s] >>>  %(message)s',
                        datefmt='%Y-%m-%d %I:%M:%S')

    try:#主要代码
    	#读取tiff图像
        imstack1 = skio.imread("E:/code/抖动测试-更换底座/2022.08.12-03-1.tif", plugin="tifffile")    
        col_listp = []
        row_listp = []
        col_listb = []
        row_listb = []
        
        hough_radii = np.arange(10, 20, 1)
        #遍历图像并找出关注点
        for i in range(len(imstack1)):
            im = imstack1[i,:,:]
            #gray_imi = skic.rgb2gray(im_i)
            
            
            #获取钨丝针尖
            col_p, row_p = op_one_img_pin(im)
            col_listp.append(col_p)
            row_listp.append(row_p)
            
            #获取钢珠圆心
            col_b, row_b = op_one_img_ball(im,hough_radii)
            col_listb.append(col_b)
            row_listb.append(row_b)  
            
        
        #差分
        df_colp = diff_list(col_listp) 
        df_rowp = diff_list(row_listp)
        
        df_colb = diff_list(col_listb) 
        df_rowb = diff_list(row_listb)
        
        
        #写入 电子表格
        lists_to_excel(column_p=col_listp, df_col_p=df_colp, row_p=row_listp, df_row_p=df_rowp,\
                       column_b=col_listb, df_col_b=df_colb, row_b=row_listb, df_row_b=df_rowb)
            #不能使用这样的变量做键：row-b=row_listb 。 会被认为是个row减b = row_listb从而出现“keyword can't be an expression”
            #https://stackoverflow.com/questions/30407568/syntaxerror-keyword-cant-be-an-expression
    
        # lists_to_excel(column_p=1, df_col_p=2, row_p=3, df_row_p=4,\
        #                column_b=2, df_col_b=3, row_b=3, df_row_b=5)
    
    
    except Exception as e:
        logging.error("Main program error:")
        logging.error(e)
        logging.error(traceback.format_exc())
    
    
##绘图
# plt.plot(row_list)
# plt.show()
# plt.plot(df_row)
# plt.show()
    
# call main
if __name__ == '__main__':
    main()