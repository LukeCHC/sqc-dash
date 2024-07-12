# -*- coding: utf-8 -*-
"""
Created on Wed Nov 23 11:48:33 2022

@author: Zoe Chen
"""

from TimeTrans.timeTools import doy2ymd
from Downloading.downloading_sp3 import downloading_sp3
from Downloading.downloading_clk import downloading_clk
import os
from datetime import datetime as dt

def check_sp3f(IFP,dates):
    #= check if sp3 files exist for the dates 
    #= if not, download it
    filein = get_files(IFP,'sp3')
    nfile = len(filein)
    dates0 = []
    if(nfile >0):
        for i in range(nfile):
            filename = os.path.basename(filein[i])
            #= the length of fullname of GBM/ESA*.SP3 is 38
            #if(filename[0:3] == 'GBM'):
            if(len(filename) == 38):
                year = int(filename[11:15])
                doy = int(filename[15:18])
                date = doy2ymd(year,doy)
                dates0.append(date)
    
    for i in range(len(dates)):
        if(dates[i] not in dates0):
            downloading_sp3(IFP,dates[i]).sp3F()
            #downloading_sp3(IFP,dates[i]).sp3R()
    return

def check_clkf(IFP,dates):
    #= check if clk files exist for the dates 
    #= if not, download it
    filein = get_files(IFP,'clk')
    nfile = len(filein)
    dates0 = []
    if(nfile >0):
        for i in range(nfile):
            filename = os.path.basename(filein[i])
            #if(filename[0:3] == 'GBM'):
            #= the length of fullname of GBM/ESA*.SP3 is 38
            if(len(filename) == 38):
                year = int(filename[11:15])
                doy = int(filename[15:18])
                date = doy2ymd(year,doy)
                dates0.append(date)
    
    ddates = []
    if (type(dates) == dt):
        ddates.append(dates)
    else:   
        ddates = dates
        
    for i in range(len(ddates)):
        if(ddates[i] not in dates0):
            downloading_clk(IFP,ddates[i]).clkF()
            #downloading_clk(IFP,ddates[i]).clkR()
    return


def get_files(IFP,types):
    #=In: IFP: Input folder path
    #=    types: *.sp3,*.yyO
    #=Out: the path of types (all files)
    filepath   = []      # file path
    for (root, dirs, files) in os.walk(IFP, topdown=False):
        for name in files:
            filename = os.path.basename(name)
            if(types.lower() in filename.lower()):
                filepath.append(os.path.join(root,name))
    return filepath

def get_tfiles(IFP,types,dates):
    #=In: IFP: Input folder path
    #=    types: *.sp3,*.clk
    #=Out: the path of types for the dates
    ddates = []
    if(type(dates) == dt):
        ddates.append(dates)
    else:
        ddates = dates
    filepath   = []      # file path
    files = get_files(IFP,types)
    nfile = len(files)
    for i in range(nfile):
        filename = os.path.basename(files[i])
        #if(filename[0:3] == 'GBM'):
        #= the length of fullname of GBM/ESA*.SP3/CLK is 38
        #= not suitable for *.yyo
        if(len(filename) == 38):
            year = int(filename[11:15])
            doy = int(filename[15:18])
            date = doy2ymd(year,doy)
            if (date in ddates):
                filepath.append(files[i])
    return filepath