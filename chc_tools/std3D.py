#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
3d std calculation
Created on Mon May 24 15:00:29 2021
@author: Dr Hui Zhi
"""

import numpy as np

def std3D(array3D):
    res = np.full((array3D.shape[0], array3D.shape[1], 1) ,np.nan)
    for i in range(array3D.shape[0]):
        res[i,:,0] = np.sqrt(
            (np.square(array3D[i,:,0]) + np.square(array3D[i,:,1]) 
             + np.square(array3D[i,:,2])) / array3D.shape[2])
    return res
