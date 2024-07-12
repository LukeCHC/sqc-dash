#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Reverse Order for numpy as last column
Created on Thu May 27 14:48:15 2021
@author: Dr Hui Zhi
"""

import numpy as np

def reverseOrder(array2D):
    return array2D[np.lexsort(-array2D.T)]
