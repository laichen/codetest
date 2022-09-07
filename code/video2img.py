# -*- coding: utf-8 -*-
"""
Spyder Editor

This is a temporary script file.
"""
import cv2


videoinpath  = './redpoint.mp4'  
imgoutpath = './imgs'

def save_img():
    
    capture = cv2.VideoCapture(videoinpath)
    #fps = capture.get(cv2.CAP_PROP_FPS)
    #frameCount = capture.get(cv2.CAP_PROP_FRAME_COUNT)
    #size = (int(capture.get(cv2.CAP_PROP_FRAME_WIDTH)), int(capture.get(cv2.CAP_PROP_FRAME_HEIGHT)))
    if capture.isOpened():
        c = 0
        while True:
            success,frame =capture.read()

            if success:
                cv2.imwrite(imgoutpath + str(c) + '.png', frame)
                cv2.waitKey(1)
                c = c + 1
            else:
                break
    else:
        print('视频打开失败！')
        
        capture.release()
        print('save_success')
        print(imgoutpath)


save_img()
