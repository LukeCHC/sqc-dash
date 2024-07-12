# -*- coding: utf-8 -*-
"""
Created on Wed Jun 15 10:46:24 2022

@author: Zoe Chen
"""

def id2num(staid):
    stanum = int(staid[1:3])
    return stanum

def num2id(sys,satnum):
    if len(satnum) < 2:
        satid = sys +'0'+ satnum
    else:
        satid = sys + satnum
    return satid