# -*- coding: utf-8 -*-
"""
Created on Tue Sep 14 10:55:47 2021

@author: dx.lai

此程序旨在计算牙科机PANO模式下一维直行电机的运动曲线。
计算条件：
旋转机架半圈匀速旋转拍摄牙弓，速度为半圈15s
牙弓曲线：需作为下方输入参数输入
几何：默认直行电机运动方向为与牙弓中线重合，且以会厌指向门牙方向为负方向

"""


import numpy as np
import math
from matplotlib import pyplot as plt 
from sympy import Symbol
from sympy.utilities import lambdify
#from sympy import *
import pwlf


#------------------基本的定义域区间、牙弓曲线等输入参数--------------------------

#total_time:运行总时间:默认15s。单位s
total_time = 15
#时间步长
t_step = 150
#由于对称性，取总时间一半
#考虑到一半时间的最后一步时，直线斜率无限大，将其删除。
t = np.delete(np.linspace(0,total_time/2,t_step),t_step-1)



#TODO 若未来可以直接提取曲线，可从曲线上/图像上直接获得牙弓深度
#FIXME 可以尝试直接用 scipy.optimize.minimize() 函数 取得牙弓的最大值和最小值
#牙弓深度，此处可指单个牙弓，也可指包含下颌骨对的牙弓，单位mm
dental_depth = 60
#截距步长，决定线簇的精细度，从而决定电机运动曲线的精度
b_step = 200

#U臂的拍摄方向的线（簇）由角度tan（th）和截距b确定。
#在特定角度下，取一系列截距b。加上下颌骨的曲线的Normal模式，负方向需要相应加长 
b = np.linspace(-40, -10 + dental_depth, b_step)



#TODO 若未来可以直接提取曲线，可从曲线上/图像上直接获得牙弓宽度
#牙弓宽度，此处可指单个牙弓，也可指包含下颌骨对的牙弓，单位mm
dental_width = 80
#x坐标步长,配合判定条件，影响求交点的精确度
x_step = 600

#默认牙弓曲线对称于y轴两侧，开口朝上，最低点位于原点。配合t，先取一半。
x = np.linspace(0, dental_width/2, x_step)




#TODO 如何能直接从图像中自动提取出曲线
#二次方牙弓拟合曲线及包含下颌骨的曲线
##poly1d 更新为 polynomial.Polynomial, 更新后，高次在后。故列表逆序。下同
dental_2 = np.poly1d([0.7474, 0.0635, -5.4247])
#四次方牙弓拟合曲线
dental_4 = np.poly1d([0.1021, 0.0292, 0.1151, -0.0396, -4.8448])

#四次方下颌骨+牙弓曲线
dental_jawbone_4 = np.poly1d([-0.0000202053, 0.0000856488, 0.0694342332, -0.1518252708, 0.0301734764])

#---下述注释部分定义函数可能有问题
# def dental_4(x):
#     "四次方牙弓拟合曲线"
#     #dental = 0.1021*x^4 + 0.0292*x^3 + 0.1151*x^2 - 0.0396*x - 4.8448
#     #上述书写仅为示意，不可用于代码。unsupported operand type(s) for ^: 'Mul' and 'Add'
#     dental = np.polynomial([0.1021, 0.0292, 0.1151, -0.0396, -4.8448])
#     return dental(x)

# def dental_2(x):
#     "二次方牙弓拟合曲线"
#     #dental = 0.7474*x^2 + 0.0635*x - 5.4247 
#     #上述书写仅为示意，不可用于代码。unsupported operand type(s) for ^: 'Mul' and 'Add'
#     dental = np.polynomial([0.7474, 0.0635, -5.4247])
#     return dental(x)



#---------------------------------- 工具函数  ------------------------------
def theta_m(t,degree=200,angle_start=-10,total_time=15):
    '''
    参数：
        t:时间，单位s
        degree:转动角度，默认200度。单位°
        angle_start:起始角度，默认-10（垂直颌骨，人侧面方向为0°，人后方为负）。单位°
        total_time:运行总时间:默认15s。单位s
    返回：
        时间t下对应的弧度制角度
    '''
    
    th_degree = degree*t/total_time + (90 + angle_start)
    #转换为弧度
    th = math.radians(th_degree)
    return th


def lines_m(th,b,x):
    "定义U臂转动时的投影直线 "
    lines = (1/math.tan(th)) * x + b
    return lines    


def cal_distance(p1, p2):
    "计算平面上两点的欧氏距离"
    l = math.sqrt(math.pow((p2[0] - p1[0]), 2) + math.pow((p2[1] - p1[1]), 2))
    return l



#---------------------------------关于引入pwlf包后使用分段函数的一些工具函数 -----------


def get_symbolic_eqn(pwlf_, segment_number):
    '专用以返回分段函数某一段的符号函数公式'
    x = Symbol('x')
    if pwlf_.degree < 1:
        raise ValueError('Degree must be at least 1')
    if segment_number < 1 or segment_number > pwlf_.n_segments:
        raise ValueError('segment_number not possible')
    # assemble degree = 1 first
    for line in range(segment_number):
        if line == 0:
            my_eqn = pwlf_.beta[0] + (pwlf_.beta[1])*(x-pwlf_.fit_breaks[0])
        else:
            my_eqn += (pwlf_.beta[line+1])*(x-pwlf_.fit_breaks[line])
    # assemble all other degrees
    if pwlf_.degree > 1:
        for k in range(2, pwlf_.degree + 1):
            for line in range(segment_number):
                beta_index = pwlf_.n_segments*(k-1) + line + 1
                my_eqn += (pwlf_.beta[beta_index])*(x-pwlf_.fit_breaks[line])**k
    return my_eqn.simplify()



def get_pw_func_eqn(pwlf_):
    '用以返回分段函数的表达式'
    x = Symbol('x')
    eqn_list = []
    f_list = []
    for i in range(pwlf_.n_segments):
        eqn_list.append(get_symbolic_eqn(pwlf_, i + 1))
        print('Equation number: ', i + 1)
        print(eqn_list[-1])
        f_list.append(lambdify(x, eqn_list[-1]))
    return eqn_list, f_list



# TODO：完成这个函数，返回导数
def pw_diff(pwlf_,t_break,t):
    '用以对分段函数的路径函数进行求导'
    if pwlf_.degree < 1:
        raise ValueError('Degree must be at least 1 to diff')
    if pwlf_.degree == 1:
        slopes = pwlf_.calc_slopes()
        for i in range(len(t_break)):            
            if t_break[i] <= t < t_break[i+1]:
                return slopes[i]
            return 0.0
    else:
        raise ValueError('Degree over 1 is not supported yet')
        
        

def unif_v(slopes, t_break, t):
    ''''
    slopes：列表。拟合分段直线的斜率
    t_break：列表。分段点
    t：列表。横坐标
    
    仅仅hardcode，适用分段点有两个，且速度为常数的情况
    -------
    一个返回速度分段函数的函数
    '''
    conditions =  [(t > t_break[0]) & (t< t_break[1]), 
                   (t > t_break[1]) & (t < t_break[2]),  
                   (t > t_break[2])&(t< t_break[3])]
    functions = slopes
    
    velocity = np.piecewise(t, conditions, functions)
    return velocity



        



#------------------------------ 两种场景下的计算函数，返回 时间-电机位移 两个对应的列表------------------------
def Equidistance(t,b,x,dental):
    '''计算等距情况下的数值解。其中:
    t为时间区间（array），
    b为截距区间（array），
    x为定义域区间（array），
    返回 时间-电机位移 两个对应的列表
    '''
    #TODO ATD_aim 后续应该由牙弓深度和宽度两个参数计算而得    
    #ATD Axis to Tooth Distance, unit:mm
    ATD_aim = 40 #过大会导致找不到点或者点很少
    #用于统计的”全部信息列表“
    intersect_and = []
    #m用于统计“全部信息列表”的数据点index
    m = -1
    #ctr 即counter，用于判断『全部信息列表』是否已被检查过
    ctr = 0
    #求出的时间和截距的列表，用于函数返回
    time_list = []
    intercept_list = []
    
    #等间隔改变”时间-角度”，从而改变斜率
    for i in t:
        #在特定”时间-角度-斜率“情况下画出各种截距的线簇
        for j in b:
            #在特定斜率，特定截距的确定直线下，寻找与牙弓曲线的交点
            for k in x:
                y1 = lines_m(theta_m(i),j,k) - dental(k)
                #满足判定条件，即可认为是交点。判定条件精度可改变，下同。
                if math.fabs(y1) < 0.1:
                    
                    print(k,dental(k),j)
                    #计算交点和截距点的距离
                    atd = cal_distance((k,dental(k)),(0,j))
                    #记录所有信息（全部信息列表）
                    intersect_and.append((i,theta_m(i),j,k,dental(k),atd))
                    m = m + 1 
                    
            #如果列表的长度比上次增加1，表示有新的交点，可进一步计算
            if len(intersect_and) - ctr:
                ctr = ctr + 1
                y2 = intersect_and[m][5]-ATD_aim
                #满足判定条件，即可认为该截距条件下的特定直线，满足等距要求。
                if math.fabs(y2) < 0.1:
                    #记录此时的时间，和截距位置，用于后续拟合直行电机运动轨迹
                    time_list.append(intersect_and[m][0])
                    intercept_list.append(intersect_and[m][2])
                    print("Found a line!")
                    
            else:
                print("No intersection")
        
            
    return time_list, intercept_list

def Normal(t,b,x,dental):
    '''
    计算法线情况下的数值解,其中:
    t为时间区间（array），
    b为截距区间（array），
    x为定义域区间（array）
    返回 时间-电机位移 两个对应的列表
    '''
    
    #用于统计的”全部信息列表“
    intersect_and = []
    #m用于统计“全部信息列表”的数据点index
    m = -1
    #ctr 即counter，用于判断『全部信息列表』是否已被检查过
    ctr = 0
    #求出的时间和截距的列表，用于函数返回
    time_list = []
    intercept_list = []
    
    
    #等间隔改变”时间-角度”，从而改变斜率
    for i in t:
        #在特定”时间-角度-斜率“情况下画出各种截距的线簇
        for j in b:
            #在特定斜率，特定截距的确定直线下，寻找与牙弓曲线的交点
            for k in x:
                y1 = lines_m(theta_m(i),j,k) - dental(k)
                #满足判定条件，即可认为是交点。判定条件精度可改变，下同。
                if math.fabs(y1) < 0.1:
                    
                    print(k,dental(k),j)
                    #计算交点和截距点的距离
                    atd = cal_distance((k,dental(k)),(0,j))
                    #记录所有信息（全部信息列表）
                    intersect_and.append((i,theta_m(i),j,k,dental(k),atd))
                    m = m + 1 
            
            #如果列表的长度比上次增加1，表示有新的交点，可进一步计算
            if len(intersect_and) - ctr:
                ctr = ctr + 1
                #利用 np.polyder 求牙弓曲线的导数k1，得出交点处的牙弓曲线的切线斜率
                k1 = np.polyder(dental,1)(intersect_and[m][3])  
                #直线的斜率
                k2 = 1/(math.tan(intersect_and[m][1]))
                #若两线垂直，则斜率相乘为-1，再+1 即为0
                y2 = k1*k2 + 1
                #满足判定条件，即可认为该截距条件下的特定直线，满足等距要求。
                if math.fabs(y2) < 0.015:
                    #记录此时的时间，和截距位置，用于后续拟合直行电机运动轨迹
                    time_list.append(intersect_and[m][0])
                    intercept_list.append(intersect_and[m][2])
                    print("Found a line!")
                    
            else:
                print("No intersection")
                
    return time_list, intercept_list
        

                   
#----------------------------对 时间 - 位移 散点进行拟合 -------------------
def time_displacement_fit(t_list,x_list,degree):
    '''
    Parameters
    ----------
    t_list : LIST
        时间点的列表.
    x_list : LIST
        位移点的列表.
    degree : int
        拟合目标的幂函数的最高次
    Returns  一个拟合的曲线的函数.
    -------
    一个用幂函数拟合曲线的函数
    '''
    poly = np.polyfit(t_list, x_list, deg = degree)#高次系数在前
    fitting_func = np.poly1d(poly)#高次系数须在后
    return fitting_func


def time_displacement_pwfit(t_list,x_list,degree,t_break):
    '''
    Parameters
    ----------
    t_list : List
        拟合点的横坐标，时间.
    x_list : List
        拟合点的纵坐标，截距.
    degree : int
        拟合函数的次数.
    t_break : List
        分段函数的分段点，含起讫点
        如t_break = np.array([min(time_list), 3, 4, max(time_list)]).

    Returns 一个拟合的分段函数
    -------
    一个用分段函数拟合曲线的函数
    '''
    displacement_pwlf = pwlf.PiecewiseLinFit(t_list, x_list, degree = degree)
    displacement_pwlf.fit_with_breaks(t_break)
    #t_hat = np.linspace([min(t_list), max(t_list), 5000])
    return displacement_pwlf

  





                         
# ---------------------------- 主函数 --------------------------------------       
def main():
    
    #换不同函数，选择两种情形计算时间-截距的关系，返回两个列表
    time_list, intercept_list = Normal(t,b,x,dental_jawbone_4)

   
    #Print something
    print('time list is:',time_list)
    print ('intercept list is:', intercept_list)

    
    #分段函数分段点。需根据具体情况手动调整
    t_break = np.array([min(time_list), 2.7, 3, 4, max(time_list)])    
    
    
    #是否使用多项式拟合。否则，使用分段函数拟合
    use_poly = True 
    #拟合
    if use_poly:
        
        fitting_func = time_displacement_fit(time_list, intercept_list, 6)
        
        correlation = np.corrcoef(intercept_list, fitting_func(time_list))[0,1]  #相关系数
        R_sq = correlation**2   #R方（决定系数（英语：coefficient of determination，记为R2或r2））
        print('The fitting functiong of pano motor t-x curve is:', fitting_func)
        velocity = np.polyder(fitting_func,1)
        print ('The velocity is:',velocity)
        acceleration = np.polyder(fitting_func,2)
        print('The acceleration is', acceleration)
        #TODO 上述信息保存为文本输出
    else:  

        fitting_func = time_displacement_pwfit(
            time_list, intercept_list, 1, t_break)
        R_sq = fitting_func.r_squared() #计算决定系数
        fitting_eqn, fitting_list = get_pw_func_eqn(fitting_func) #返回分段函数表达式
        #TODO 把求导的速度整出来
        slopes = fitting_func.calc_slopes() #求出斜率
        velocity = unif_v(slopes, t_break, time_list) #速度分段函数
        
        
        
    #Plot figures
    #figsize 参数用于调整 width 和 height。默认为1：1
    #figsize 参数用于调整 width 和 height。默认为1：1
    fig, ax = plt.subplots(2,figsize=(7,10))
    plt.subplots_adjust(left=None, bottom=None, right=None, top=None, wspace=None, hspace=0.3)
    fig.suptitle('Everything about pano motor movement')
    #plt.scatter(time_list,intercept_list)
    ax[0].plot(time_list, intercept_list, 'o', label='orignal displacement')
    
    if use_poly:
        ax[0].plot(time_list,fitting_func(time_list), label='displacement(fitting)')
        ax[0].text(3.5, 50, fitting_func, wrap=True)#在图中打印字符串，前两个参数为起点坐标，下同
    else: #由于分段函数的fitting_func 无法调用，无法打印，因此分成两种情况
        ax[0].plot(time_list,fitting_func.predict(time_list), label='displacement(fitting)')
        ax[0].text(3.5, 50, fitting_eqn, wrap=True)
        
    ax[0].text(3, 45, 'R square is %f'%R_sq)
    ax[0].set_xlabel('time (unit: s)')  # Add an x-label to the axes.
    ax[0].set_ylabel('displacement (unit: mm)')  # Add a y-label to the axes.
    ax[0].set_title("'t-x' curve of pano motor")  # Add a title to the axes.
    ax[0].legend()  # Add a legend.
    
    
    if use_poly:
        ax[1].plot(time_list, velocity(time_list), label='velocity')
        ax[1].text(3, -40, velocity, wrap=True)
    else:
        ax[1].plot(time_list, velocity, label='velocity') #此时的velocity 是一个列表，无法带（time_list）
        ax[1].text(3, -40, slopes, wrap=True)#此时的velocity也不便全部打印出来
    #ax[1].plot(time_list, acceleration(time_list), label='acceleration')
    ax[1].set_xlabel('time (unit: s)')  # Add an x-label to the axes.
    ax[1].set_ylabel('v (unit: mm/s)')  # Add a y-label to the axes.
    ax[1].axhline(y=0, color="black", linestyle="--")  # reference line 
    ax[1].set_title("'t-v' curve of pano motor")  # Add a title to the axes.
    ax[1].legend()  # Add a legend.
    #子图自动布局，不至于文字坐标重叠
    #plt.tight_layout()
    #以下存储目录因人而异
    plt.savefig('./tryhd-NEW.png', dpi=300)
    #TODO 增加预估时间或者进度条。可从for循环的次数预估。
    

if __name__ == "__main__":
    main()        
        
