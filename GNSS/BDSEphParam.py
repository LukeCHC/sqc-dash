# -*- coding: utf-8 -*-
"""
BDS Ephemeris Parameter
Created on Tue Aug 25 2020
@author: Dr Hui Zhi
"""

#import GNSS
from GNSS import Dummy
import numpy as np

class BDSEphParam():
    dType_o = np.dtype([
        ('time', np.float64), ('sys', np.float64), ('PRN', np.float64), 
        ('description', np.float64)])
    
    def __init__(self, blockData, num):
        self.blockData = blockData
        self.num       = num
                   
        # SV/EPOCH/SV CLK
        self.sat_sys = self.blockData[self.num][0]
        self.prn     = int(self.blockData[self.num][1:3])
        self.toc     = self.blockData[self.num][4:8]
        self.obs_t   = self.blockData[self.num][4:23]
        self.bias    = float(self.blockData[self.num][23:42])
        self.drift   = float(self.blockData[self.num][42:61])
        self.driftRate = float(self.blockData[self.num][61:80])
        
        # Broadcast orbit - 1
        self.IODE   = int(float(self.blockData[self.num+3][4:23]) / 720 % 240)
        self.Crs    = float(self.blockData[self.num+1][23:42])
        self.Deltan = float(self.blockData[self.num+1][42:61])
        self.M0     = float(self.blockData[self.num+1][61:80])
        
        # Broadcast orbit - 2
        self.Cuc   = float(self.blockData[self.num+2][4:23])
        self.e     = float(self.blockData[self.num+2][23:42])
        self.Cus   = float(self.blockData[self.num+2][42:61])
        self.sqrtA = float(self.blockData[self.num+2][61:80])
        
        # Broadcast orbit - 3
        self.Toe_SOW = float(self.blockData[self.num+3][4:23])
        self.Cic     = float(self.blockData[self.num+3][23:42])
        self.omega0  = float(self.blockData[self.num+3][42:61])
        self.Cis     = float(self.blockData[self.num+3][61:80])
        
        # Broadcast orbit - 4
        self.i0       = float(self.blockData[self.num+4][4:23])
        self.Crc      = float(self.blockData[self.num+4][23:42])
        self.omega    = float(self.blockData[self.num+4][42:61])
        self.omegaDOT = float(self.blockData[self.num+4][61:80])
        
        # Broadcast orbit - 5
        self.IDOT        = float(self.blockData[self.num+5][4:23])
        # self.spare1      = float(self.blockData[self.num+5][23:42])
        self.Toe_BDSWeek = float(self.blockData[self.num+5][42:61])
        # self.spare2      = float(self.blockData[self.num+5][61:80])
        
        # Broadcast orbit - 6
        self.SVaccuracy = float(self.blockData[self.num+6][4:23])
        self.SVhealth   = float(self.blockData[self.num+6][23:42])
        self.TGD1       = float(self.blockData[self.num+6][42:61])
        self.TGD2       = float(self.blockData[self.num+6][61:80])

        # Broadcast orbit - 7
        self.TransmissionTime = float(self.blockData[self.num+7][4:23])
        self.AODC             = float(self.blockData[self.num+7][23:42])
        # self.spare3         = float(self.blockData[self.num+7][42:61])
        # self.spare4         = float(self.blockData[self.num+7][61:80])
        
    def res(self):
        # Obs time
        obs_tM  = int('{}{}{}{}{}{}'.format(
            self.blockData[self.num][4:8], self.blockData[self.num][9:11], 
            self.blockData[self.num][12:14], self.blockData[self.num][15:17], 
            self.blockData[self.num][18:20], self.blockData[self.num][21:23]))
        resList = [
            obs_tM, Dummy.sys[self.sat_sys], self.prn,
            self.bias, self.drift, self.driftRate, self.IODE, self.Crs, 
            self.Deltan, self.M0, self.Cuc, self.e, self.Cus, self.sqrtA, 
            self.Toe_SOW, self.Cic, self.omega0, self.Cis, self.i0, self.Crc, 
            self.omega, self.omegaDOT, self.IDOT, self.Toe_BDSWeek, 
            self.SVaccuracy, self.SVhealth, self.TGD1, self.TGD2, 
            self.TransmissionTime, self.AODC]
        return resList
