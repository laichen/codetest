# -*- coding: utf-8 -*-
"""
Created on Wed Apr 20 21:05:50 2022

@author: dx.lai
"""


# -*- coding: utf-8 -*-
"""
Created on Wed Apr 20 11:10:42 2022

@author: dx.lai

https://simpleitk.readthedocs.io/en/master/link_DicomSeriesFromArray_docs.html

"""


import SimpleITK as sitk

# import sys
import time
import os
import numpy as np

#注意：需要使用 / 号
mhd_path = "F:/vlt/wzbmm/reconImg-1024-1024-800.mhd"  # mhd文件需和同名raw文件放在同一个文件夹

out_directory = "F:/dcmtest/wzbmmdcm"  #同上，输出的目录

pixel_dtypes = {"int16": np.int16, "float32":np.float32, "float64": np.float64} #输入的数据类型池

pixel_dtype = pixel_dtypes["float64"] # 确定输入图像数据类型




#定义一个读取并处理单帧图像的函数
def writeSlices(series_tag_values, new_img, out_dir, i):
    '''
    

    Parameters
    ----------
    series_tag_values : TYPE
        Tag 的列表.
    new_img : TYPE
        Array 图像.
    out_dir : TYPE
        输出目录.
    i : TYPE
        Index.

    Returns
    -------
    .dcm 文件.

    '''
    image_slice = new_img[:, :, i] #对z方向进行切片

    # Tags shared by the series.
    list(map(lambda tag_value: image_slice.SetMetaData(tag_value[0],
                                                       tag_value[1]),
             series_tag_values))


    #   切片特有的Tag
    #关于Dicom tag，参考 https://dicom.innolitics.com/ciods/cr-image/patient/00100020
    
    image_slice.SetMetaData("0008|0012", time.strftime("%Y%m%d")) #Instance Creation Date
    image_slice.SetMetaData("0008|0013", time.strftime("%H%M%S")) #Instance Creation Time

    # Setting the type to CT so that the slice location is preserved and
    # the thickness is carried over.
    #https://dicom.innolitics.com/ciods/mr-image/general-series/00080060
    #Modality 下定义的条目中没有CBCT条目
    image_slice.SetMetaData("0008|0060", "CT") 

    # (0020, 0032) image position patient determines the 3D spacing between
    # slices.
    #   Image Position (Patient)
    image_slice.SetMetaData("0020|0032", '\\'.join(
        map(str, new_img.TransformIndexToPhysicalPoint((0, 0, i)))))
    
    #   Instance Number
    image_slice.SetMetaData("0020,0013", str(i))

    # Write to the output directory and add the extension dcm, to force
    # writing in DICOM format.
    writer.SetFileName(os.path.join(out_dir, str(i) + '.dcm'))
    writer.Execute(image_slice)



#读取mhd中指向的raw文件
data = sitk.ReadImage(mhd_path)  # 读取mhd文件
spacing = data.GetSpacing()  # 获得spacing大小
direction = data.GetDirection() #获取方向，对应TransformMatrix
img_data = sitk.GetArrayFromImage(data)  # 获得图像矩阵
new_img = sitk.GetImageFromArray(img_data)
new_img.SetSpacing(spacing) #设置spacing 
new_img.SetDirection(direction) #设置direction




writer = sitk.ImageFileWriter()
# Use the study/series/frame of reference information given in the meta-data
# dictionary and not the automatically generated information from the file IO
writer.KeepOriginalImageUIDOn()

modification_time = time.strftime("%H%M%S")
modification_date = time.strftime("%Y%m%d")

# Copy some of the tags and add the relevant tags indicating the change.
# For the series instance UID (0020|000e), each of the components is a number,
# cannot start with zero, and separated by a '.' We create a unique series ID
# using the date and time. Tags of interest:

series_tag_values = [
    ("0008|0031", modification_time),  # Series Time
    ("0008|0021", modification_date),  # Series Date
    ("0008|0008", "DERIVED\\SECONDARY"),  # Image Type
    ("0020|000e", "1.2.826.0.1.3680043.2.1125."
     + modification_date + ".1" + modification_time),  # Series Instance UID
    ("0020|0037", '\\'.join(map(str, (direction[0], direction[3], direction[6],
                                      direction[1], direction[4],
                                      direction[7])))),  # Image Orientation
    # Patient
    ("0008|103e", "Created-SimpleITK-Laidx"), # Series Description
    ("0010|0010","Female volunteer"), #Patient's Name
    ("0010|0040","F"),  #Patient's Sex
    ("0018|0015","JAW"), #Body Part Examined 
    #https://dicom.nema.org/medical/dicom/current/output/chtml/part16/chapter_L.html#chapter_L
    
    # CT Image
    ("0018|1110","600"), #SID mm
    ("0018|1111","400"), #SAD mm
    ("0018|1150","1800"), #Exposure Time ms 
    ("0018|0060","90"), #kVp 
    ("0018|1151","5"), #X-Ray Tube Current   mA
    ("0018|1190","0.5"), #Focal spot  mm
]

if pixel_dtype == np.float64:
    # If we want to write floating point values, we need to use the rescale
    # slope, "0028|1053", to select the number of digits we want to keep. We
    # also need to specify additional pixel storage and representation
    # information.
    rescale_slope = 0.001  # keep three digits after the decimal point
    series_tag_values = series_tag_values + [
        ('0028|1053', str(rescale_slope)),  # rescale slope
        ('0028|1052', '0'),  # rescale intercept
        ('0028|0100', '16'),  # bits allocated
        ('0028|0101', '16'),  # bits stored
        ('0028|0102', '15'),  # high bit
        ('0028|0103', '1')]  # pixel representation



if pixel_dtype == np.float32:
    # If we want to write floating point values, we need to use the rescale
    # slope, "0028|1053", to select the number of digits we want to keep. We
    # also need to specify additional pixel storage and representation
    # information.
    rescale_slope = 0.01  # keep three digits after the decimal point
    series_tag_values = series_tag_values + [
        ('0028|1053', str(rescale_slope)),  # rescale slope
        ('0028|1052', '0'),  # rescale intercept
        ('0028|0100', '16'),  # bits allocated
        ('0028|0101', '16'),  # bits stored
        ('0028|0102', '15'),  # high bit
        ('0028|0103', '1')]  # pixel representation


# Write slices to output directory
list(map(lambda i: writeSlices(series_tag_values, new_img, out_directory, i),
         range(new_img.GetDepth())))


# # Re-read the series
# # Read the original series. First obtain the series file names using the
# # image series reader.
# data_directory = out_directory
# series_IDs = sitk.ImageSeriesReader.GetGDCMSeriesIDs(data_directory)
# if not series_IDs:
#     print("ERROR: given directory \"" + data_directory +
#           "\" does not contain a DICOM series.")
#     sys.exit(1)
# series_file_names = sitk.ImageSeriesReader.GetGDCMSeriesFileNames(
#     data_directory, series_IDs[0])

# series_reader = sitk.ImageSeriesReader()
# series_reader.SetFileNames(series_file_names)

# # Configure the reader to load all of the DICOM tags (public+private):
# # By default tags are not loaded (saves time).
# # By default if tags are loaded, the private tags are not loaded.
# # We explicitly configure the reader to load tags, including the
# # private ones.
# series_reader.LoadPrivateTagsOn()
# image3D = series_reader.Execute()
# print(image3D.GetSpacing(), 'vs', new_img.GetSpacing())
# sys.exit(0)