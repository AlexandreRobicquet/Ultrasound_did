#!/usr/bin/python
# -*- coding: utf-8 -*-

"""

All rights reserved.
Written by Alexandre Robicquet <robicquet.alexandre@gmail.com>, 2017

"""


import sys
reload(sys)
sys.setdefaultencoding('utf-8')
import dicom
import cv2
import numpy as np
import os
import json
import pylab
from PIL import Image, ImageFilter
import pytesseract
import random
import time


def jpg_image_to_array(image_path):
  """
  Loads JPEG image into 3D Numpy array of shape
  (width, height, channels)
  """
  with Image.open(image_path) as image:
    im_arr = np.fromstring(image.tobytes(), dtype=np.uint8)
    im_arr = im_arr.reshape((image.size[1], image.size[0], 3))
  return im_arr



def strTimeProp(start, end, format, prop):
    """Get a time at a proportion of a range of two formatted times.

    start and end should be strings specifying times formated in the
    given format (strftime-style), giving an interval [start, end].
    prop specifies how a proportion of the interval to be taken after
    start.  The returned time will be in the specified format.
    """

    stime = time.mktime(time.strptime(start, format))
    etime = time.mktime(time.strptime(end, format))

    ptime = stime + prop * (etime - stime)

    return time.strftime(format, time.localtime(ptime))



def dicom_crop(dicom_name, output_path=''):
    """
    INPUT:
        - dicome_name  (str) is the path + name of the dicom to Study
        (ds is the dicom file reade)
        - output_path (str): path where to save the cropped images


    f the file is not properly decompressed, you will receive as an error"""

    ds = dicom.read_file(dicom_name)

    xM = ds.SequenceOfUltrasoundRegions[0].RegionLocationMaxX1
    yM = ds.SequenceOfUltrasoundRegions[0].RegionLocationMaxY1
    xm = ds.SequenceOfUltrasoundRegions[0].RegionLocationMinX0
    ym = ds.SequenceOfUltrasoundRegions[0].RegionLocationMinY0

    im = Image.fromarray(ds.pixel_array)

    # cropping
    img = im.crop((xm, ym, xM, yM))

    # resizing
    X = ds.SequenceOfUltrasoundRegions[0].PhysicalDeltaX*100
    Y = ds.SequenceOfUltrasoundRegions[0].PhysicalDeltaY*100
    W, H = img.size

    img = img.resize((int(round(X*W)), int(round(Y*H))), Image.ANTIALIAS)

    if pytesseract.image_to_string(img).find('Admission')==-1:
        name  = dicom_name[:-4]+'.jpg'
        if name.rfind('/')!=-1:
          name = name[name.rfind('/')+1:]
        print(name)
        img.save(output_path+name)
        ds.pixel_array = np.fromstring(im.tobytes(), dtype=np.uint8)
    else:
        ds.pixel_array = '?'




def deindentify_image(dicom_name):

    ds = dicom.read_file(dicom_name)
    im = Image.fromarray(ds.pixel_array)

    xM = ds.SequenceOfUltrasoundRegions[0].RegionLocationMaxX1
    yM = ds.SequenceOfUltrasoundRegions[0].RegionLocationMaxY1
    xm = ds.SequenceOfUltrasoundRegions[0].RegionLocationMinX0
    ym = ds.SequenceOfUltrasoundRegions[0].RegionLocationMinY0

    positions =  (0,0,im.size[0],ym)

    # blur parts of the image
    image_crop_part = im.crop(positions)
    for i in range(100):  # You can blur many times
    	image_crop_part = image_crop_part.filter(ImageFilter.BLUR)

    im.paste(image_crop_part, positions)

    im_arr = np.fromstring(im.tobytes(), dtype=np.uint8)

    ds.pixel_array = im_arr

    return ds






def deindentify(dcm, input_path='', output_path='',anon_tags=None, delete = False):

    """ deindentify is a function use to return a deintify version of the inputed dicom.

    Input:
        dcm (str / dcm): name of the dicom: '*.dcm'     [dicom to deindentify]
        intput_path (str): localization of the dicom file
        output_path (str): where the deinditenfied dicom needs to be saved_cs_client
        anon_tag (list of str): List of the tags (label) of the dicom that need to be deindentidied - if none, default list of anon tag used
        delete:
            True =  remove fully the element listed in anon_tag -> change the structure of the dicom
            False = replace the anon_tags value by the string '?'

    Ouput:
        Deidentified dicom (dcm)

    """


    if anon_tags is None:
        anon_tags = ['StudyID', 'StudyDate', 'SeriesDate', 'StudyTime', 'SeriesTime',
            'InstanceCreationDate', 'InstanceCreationTime', 'PatientID', 'AcquisitionDate',
            'AcquisitionTime', 'PerformedProcedureStepStartDate', 'PerformedProcedureStepStartTime',
            'PerformedProcedureStepID', 'PatientName.FamilyName', 'PatientName.GivenName', 'PatientName.MiddleName','PatientName.NameSuffix',
            'Header.RequestAttributesSequenceIm.Item_1.ScheduledProcedureID','FillerOrderNumberOfImagingServiceRequest' ,'Header.ReferringPhysicianName.FamilyName',
            'Header.ReferringPhysicianName.GivenName','Header.OperatorName.FamilyName', 'Header.OperatorName.GivenName', 'Header.PatientBirthTime','PatientBirthTime',
            'ReferringPhysicianName','InstitutionName','OperatorsName','IssuerOfPatientID','PerformedProtocolCodeSequence','PatientAddress',
            'PatientName','PerformingPhysicianName','PrivateCreator','InstitutionalDepartmentName','SecondaryCaptureDeviceID','StationName']

    d = dicom.read_file(input_path+dcm)

    for tag in anon_tags:
        missed = []
        #try:
        if delete:
            t = d.data_element(tag).tag
            del d[t]
        else:
            try:
                #print(d.data_element(tag).value)
                d.data_element(tag).value = '?'
                print(d.data_element(tag).value)
            except:
                missed.append(tag)

    #except:
    d.AccessionNumber = '00'+str(int(d.data_element('AccessionNumber').value[2:-1])*4)
    try:
        d.RequestAttributesSequence[0].ScheduledProcedureStepID='?'
        d.RequestAttributesSequence[0].RequestedProcedureID='?'
    except:
        pass

    #d.PatientBirthDate =  strTimeProp(str(int(d.PatientBirthDate)), str(int(d.PatientBirthDate)+1010000), '%m%d%Y', np.random.random())
    #d.ContentDate = strTimeProp(str(int(d.PatientBirthDate)), str(int(d.PatientBirthDate)+5000000), '%m%d%Y', np.random.random())
    
    if dcm.rfind('/')!=-1:
          name = dcm[dcm.rfind('/')+1:]
    d.save_as(output_path+name)
    return d

