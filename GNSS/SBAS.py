# -*- coding: utf-8 -*-
"""
SBAS Constant
Created on Tue Jul 14 2020
@author: Dr Hui Zhi
"""

import GNSS

class SBAS():
    SBASL1  = 1575.42E+06            # SBAS L1 Frequency (Hz)
    SBASL5  = 1176.45E+06            # SBAS L2 Frequency (Hz)
    
    SBASLambda_L1 = GNSS.GPS.c / SBASL1       # SBAS L1 Wavelenfth     (meter)
    SBASLambda_L5 = GNSS.GPS.c / SBASL5       # SBAS L2 Wavelenfth     (meter)
    SBASGamma15   = SBASL1**2 / SBASL5**2
    
    SBASSV = ['S' + '%02d'%x for x in range(1,40)]
    
    L1_code = ['C1C', 'L1C', 'D1C', 'S1C']
    
    L5_code = ['C5I', 'L5I', 'D5I', 'S5I',
               'C5Q', 'L5Q', 'D5Q', 'S5Q',
               'C5X', 'L5X', 'D5X', 'S5X']
    