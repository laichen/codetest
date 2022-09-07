# -*- coding: utf-8 -*-
"""
Created on Thu Apr 21 15:08:55 2022

@author: dx.lai
"""

import SimpleITK as sitk

image = sitk.ReadImage("F:/dcmtest/jjw/jjw.tif", imageIO="TIFFImageIO")