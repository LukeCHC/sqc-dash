#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
GNSS Dummies
Created on Thu Mar 18 2021
@author: Dr Hui Zhi
"""

class Dummy():
    sys = {'G':1, 'R':2, 'C':3, 'E': 4, 'S':5, 'Q':6, 'J':7}
    oc  = {'ORBIT':1, 'CLOCK': 2}
    yycInterval = {
        '0':1, '1':2, '2':5, '3':10, '4':15, '5':30, '6':60, '7':120, '8':240,
        '9':300, '10':600, '11':900, '12':1800, '13':3600, '14':7200,
        '15':10800}
    sys_ = {'GPS':1, 'GLONASS':2, 'BDS':3, 'GALILEO': 4, 'SBAS':5, 'QZSS':6, 'J':7}
    