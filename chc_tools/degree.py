# -*- coding: utf-8 -*-
"""
Created on Wed Nov 23 14:27:46 2022

@author: Zoe Chen
"""
import numpy as np

R2D = 180/np.pi
def FromRadians(rad):
    deg = rad * R2D
    return deg

def Constrain360(deg):
    deg360 = deg % 360
    return deg360

def Constrain180(deg):
    val = deg % 360 
    if val > 180:
        deg180 = val - 360 
    else:
        deg180 = val
    return deg180

def Constrain90(deg):
    if deg > 90:
        deg90 = 90
    elif deg < -90:
        deg90 = -90
    else:
        deg90 = deg
    return deg90


    