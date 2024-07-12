# -*- coding: utf-8 -*-
"""
Created on Tue Aug 23 09:53:47 2022

@author: chcuk
"""
import pandas as pd
import numpy as np

class ocCompare:
    def __init__(self, f1, f2, stEpoch, endEpoch, interval):
        self.f1 = f1
        self.f2 = f2
        self.stEpoch = stEpoch
        self.endEpoch = endEpoch
        self.interval = interval
        
        """
        f1,f1 should be numpy array shape (:,8)
        
        columns = tt, sys, prn, iode, x , y, z, clk    
        
        interval unit = seconds
        """
        
        
    def run(self):
        tRange = pd.date_range(self.stEpoch, self.endEpoch,freq=f'{self.interval}s')

        lst = []
        for i in range(len(tRange)):
            diff =  self.f1[np.where(self.f1[:,0] == tRange[i])] - self.f2[np.where(self.f2[:,0] == tRange[i])]
            cols = diff[:,-4:]
            lst.append(cols)
            
        vals = np.array(lst).reshape(-1,4)
        
        if len(vals) == len(self.f1):
            vals = np.concatenate((self.f1[:,:4], vals), axis = 1)
        elif len(vals) == len(self.f2):
            vals = np.concatenate((self.f2[:,:4], vals), axis = 1)
        else: print("Couldn't combine timetags and diff values")
        return vals
    
from Readers import sp3Read
    
rapFile = r"C:\Users\chcuk\OneDrive\Desktop\ShaoCompare\GFZ0MGXRAP_20222040000_01D_05M_ORB.SP3"
finFile = r"C:\Users\chcuk\OneDrive\Desktop\ShaoCompare\GRG0MGXFIN_20222040000_01D_05M_ORB.SP3"

rap = np.array(sp3Read.readSP3(rapFile, 900).read()[0])
rap = np.insert(rap, 3,  0,1 )
fin = np.array(sp3Read.readSP3(finFile, 300).read()[0])
fin = np.insert(fin, 3,  0,1 )
start = rap[0,0]
end = rap[-1,0]

# test = ocCompare(rap,fin,start,end, 900).run()
# test2 = ocCompare(fin,rap,start,end, 900).run()