# -*- coding: utf-8 -*-
"""
Created on Sat Apr  9 17:39:19 2022

@author: Zoe Chen
"""
from GNSS.GPS import GPS
from GNSS.GLO import GLO
from GNSS.GAL import GAL
from GNSS.BDS import BDS

def get_svnum(sys):
    if sys=='G':
        svnum = GPS.MaxNoSV
    if sys=='R':
        svnum = GLO.MaxNoSV
    if sys=='C':
        svnum = BDS.MaxNoSV
    if sys=='E':
        svnum = GAL.MaxNoSV
    return svnum