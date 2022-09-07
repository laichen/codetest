# -*- coding: utf-8 -*-
"""
Created on Wed Apr 20 11:10:42 2022

@author: dx.lai

https://simpleitk.readthedocs.io/en/master/link_DicomSeriesFromArray_docs.html

Dicom Series From Array

This example illustrates how to write a DICOM series from a numeric array and 
create appropriate meta-data so it can be read by DICOM viewers.

Generating an array is done using a simple random number generator for this 
case but can come from other sources.

Writing the 3D image as a DICOM series is done by configuring the meta-data 
dictionary for each of the slices and then writing it in DICOM format. 
In our case we generate all of the meta-data to indicate that this series is 
derived. If the new image has float values we need to encode this via the 
rescale slope (0028|1053), rescale intercept (0028|1052), and several additional 
meta-data dictionary values specifying how the values are stored.

"""


import SimpleITK as sitk

import sys
import time
import os
import numpy as np

#注意：需要使用 / 号
mhd_path = "F:/dcmtest/reconXiaoXJ-1024-1024-800/reconhalf.mhd"  # mhd文件需和同名raw文件放在同一个文件夹
data = sitk.ReadImage(mhd_path)  # 读取mhd文件

pixel_dtypes = {"int16": np.int16,"float64": np.float64}


def writeSlices(series_tag_values, new_img, out_dir, i):
    image_slice = new_img[:, :, i]

    # Tags shared by the series.
    list(map(lambda tag_value: image_slice.SetMetaData(tag_value[0],
                                                       tag_value[1]),
             series_tag_values))


    # Slice specific tags.
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


#如果传入参数不足，则提示
if len(sys.argv) < 3:
    print("Usage: python " + __file__ + " <output_directory> [" + ", "
          .join(pixel_dtypes) + "]")
    sys.exit(1)

# Create a new series from a numpy array
try:
    pixel_dtype = pixel_dtypes[sys.argv[2]]
except KeyError:
    pixel_dtype = pixel_dtypes["int16"]


#生成4x5 层厚为3的随机图像。此处可以直接替换为别的来源，如下一段。
# new_arr = np.random.uniform(-10, 10, size=(3, 4, 5)).astype(pixel_dtype)
# new_img = sitk.GetImageFromArray(new_arr)
# new_img.SetSpacing([2.5, 3.5, 4.5])

#读取mhd中指向的raw文件
spacing = data.GetSpacing()  # 获得spacing大小
direction = data.GetDirection() #获取方向，对应TransformMatrix
img_data = sitk.GetArrayFromImage(data)  # 获得图像矩阵
new_img = sitk.GetImageFromArray(img_data)
new_img.SetSpacing(spacing)
new_img.SetDirection(direction)




# Write the 3D image as a series
# IMPORTANT: There are many DICOM tags that need to be updated when you modify
#            an original image. This is a delicate opration and requires
#            knowledge of the DICOM standard. This example only modifies some.
#            For a more complete list of tags that need to be modified see:
#                  http://gdcm.sourceforge.net/wiki/index.php/Writing_DICOM
#            If it is critical for your work to generate valid DICOM files,
#            It is recommended to use David Clunie's Dicom3tools to validate
#            the files:
#                  http://www.dclunie.com/dicom3tools.html

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
    # (Patient)
    ("0008|103e", "Created-SimpleITK-Laidx")  # Series Description
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

# Write slices to output directory
list(map(lambda i: writeSlices(series_tag_values, new_img, sys.argv[1], i),
         range(new_img.GetDepth())))

# Re-read the series
# Read the original series. First obtain the series file names using the
# image series reader.
data_directory = sys.argv[1]
series_IDs = sitk.ImageSeriesReader.GetGDCMSeriesIDs(data_directory)
if not series_IDs:
    print("ERROR: given directory \"" + data_directory +
          "\" does not contain a DICOM series.")
    sys.exit(1)
series_file_names = sitk.ImageSeriesReader.GetGDCMSeriesFileNames(
    data_directory, series_IDs[0])

series_reader = sitk.ImageSeriesReader()
series_reader.SetFileNames(series_file_names)

# Configure the reader to load all of the DICOM tags (public+private):
# By default tags are not loaded (saves time).
# By default if tags are loaded, the private tags are not loaded.
# We explicitly configure the reader to load tags, including the
# private ones.
series_reader.LoadPrivateTagsOn()
image3D = series_reader.Execute()
print(image3D.GetSpacing(), 'vs', new_img.GetSpacing())
sys.exit(0)