# -*- coding: utf-8 -*-
"""
Created on Thu May 26 14:17:51 2022

@author: Zoe Chen
"""

import bitstruct

def getbitu(msg,i,fmt):
    # msg,i,fmt # msg,pos,fmt(len)
    if(type(fmt) == str):
        assert i>=0
        unpack = bitstruct.unpack_from(fmt, msg,i)[0]
    else:
        unpack = None
    return unpack