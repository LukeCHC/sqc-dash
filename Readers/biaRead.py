# -*- coding: utf-8 -*-
"""
Created on Thu Feb 16 14:34:34 2023

@author: chcuk
"""

from array import array
from GNSS import Dummy
import numpy as np
import gc
class readBia:
    def __init__(self, inPath):
        self.inPath = inPath
        
    def read(self):
        
        # file = open(self.inPath, "r")
        file = open(r"\\meetingroom\Integrity\GXCO\cgu2022270.bia", "r")
        buf  = array('d')
        flag = 1
        while flag:
            l = file.readline().strip('\n').split()
            if not l:
                file.close()
                flag = 0
            elif l[0]=='OSB':
                
                sys = Dummy.sys[l[1][0]]
                prn = int(l[1][1:])
                # freq = l[2]

                year = int(l[3][:4])
                doy = int(l[3][5:8])
                sod = int(l[3][9:14]) # second of day
                
                time  = int('{}{}{}'.format(
                    year, doy, sod))
                
                bias = float(l[6]) # nanoseconds
                buf.extend([time, sys, prn, bias])
                buf.extend([time, sys, prn, bias])
        biaArr = np.frombuffer(buf, dtype=np.float64).reshape(-1,4)
        del buf
        gc.collect()
        biaArrG = biaArr[np.where(biaArr[:,1]==Dummy.sys['G'])]
        biaArrR = biaArr[np.where(biaArr[:,1]==Dummy.sys['R'])]
        biaArrC = biaArr[np.where(biaArr[:,1]==Dummy.sys['C'])]
        biaArrE = biaArr[np.where(biaArr[:,1]==Dummy.sys['E'])]
                # output = []
                # if len(clkArrG):
                #     output.append(self.splitSys(clkArrG, "G"))
                # else: 
                #     output.append([])
                # if len(clkArrR):
                #     output.append(self.splitSys(clkArrR, "R"))
                # else: 
                #     output.append([])
                # if len(clkArrC):
                #     output.append(self.splitSys(clkArrC, "C"))
                # else: 
                #     output.append([])
                # if len(clkArrE):
                #     output.append(self.splitSys(clkArrE, "E"))
                # else: 
                #     output.append([])
        return [biaArrG, biaArrR, biaArrC, biaArrE]