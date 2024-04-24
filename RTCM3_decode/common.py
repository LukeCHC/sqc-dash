# -*- coding: utf-8 -*-
"""
Created on Wed Mar 20 09:38:06 2024

@author: CHCUK-11
"""

SYS_GPS = 'G';SYS_GLO = 'R';SYS_GAL = 'E';SYS_BDS = 'C';SYS_QZS = 'J'

MAX_GPS_SAT = 32; MAX_GLO_SAT = 28; MAX_GAL_SAT = 36; MAX_BDS_SAT = 64; MAX_QZS_SAT = 7; MAX_SBS_SAT = 19
MAX_SAT = MAX_GPS_SAT + MAX_GLO_SAT + MAX_GAL_SAT + MAX_BDS_SAT + MAX_QZS_SAT + MAX_SBS_SAT

def prn2sysNum(prn,gpsst=None,glost=None,galst=None,qzsst=None,bdsst=None):
     # gps:1, glo:2, gal:3, qzss:4, bds:5
    if gpsst == None:
        gpsst = 32
    if glost == None:
        glost = 27
    if galst == None:
        galst = 36
    if qzsst == None:
        qzsst = 7
    if bdsst == None:
        bdsst = 64
    
    lst = [gpsst,glost,galst,qzsst,bdsst]
    if prn <= 0:
        raise Exception("prn too low")
    if prn <= lst[0]:
        sys = 1
        num = prn
    elif prn <= lst[0] +lst[1]:
        sys = 2
        num = prn - lst[0] 
    elif prn <= lst[0] + lst[1] + lst[2]:
        sys = 3
        num = prn - lst[0] - lst[1]
    elif prn <= lst[0] + lst[1] + lst[2] + lst[3]:
        sys = 4
        num = prn - lst[0] - lst[1] - lst[2] 
    elif prn <= lst[0] + lst[1] + lst[2] + lst[3] +lst[4]:
        sys = 5
        num = prn - lst[0] - lst[1] - lst[2] - lst[3]
    elif prn > lst[0] + lst[1] + lst[2] + lst[3]:
        raise Exception("prn too high")
    return sys, num

# def Numsys2prn(num,sys):
    
    
#     return prn