# -*- coding: utf-8 -*-
"""
Created on Mon Feb 20 15:05:33 2023

@author: chcuk
"""

import numpy as np
from datetime import datetime, timedelta
from GNSS import GPS, GLO, GAL, BDS, Dummy
from array import array
import pandas as pd
import gc
from TimeTrans import str2dt, dt2float


class readATX:
    def __init__(self, inPath,):
        self.inPath = inPath
        
    def read(self):
        with open(self.inPath, 'r') as handle:
            lines = handle.readlines()
            
        for i in range(len(lines)):
            if 'START OF ANTENNA' in lines[i]:
                if 'VALID UNTIL' not in lines[i+7]: 
                    j=0
                    while 'END OF ANTENNA' not in lines[i+j]:
                        j+=1
                        data.append(lines[i+j])
        g_data = []
        for i in range(len(data)):
            if 'BLOCK' in data[i]:
                    j=0
                    while 'END OF ANTENNA' not in data[i+j]:
                        g_data.append(data[i+j])    
                        j+=1
        g_block = [[] for i in range(GPS.MaxNoSV)]               

        antenna_count = []
        for i in range(len(g_data)):
            if g_data[i][:5]=='BLOCK':
                antenna_count.append(i)
        antenna_count.append(len(g_data))
        for i in range(len(g_block)):
               g_block[i] = g_data[antenna_count[i]:antenna_count[i+1]]
        