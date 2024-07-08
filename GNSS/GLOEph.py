# -*- coding: utf-8 -*-
"""
Calculate Ephemeris XYZT
Created on Mon May 10 2021
@author: Dr Hui Zhi
"""

# from GNSS import GLO,matchIODE,GLOXYZT
# from Core import gpst2gpsw
import numpy as np

class GLOEph():
    def __init__(self, config, arr3D, arrBRDC, statName):
        """
        Parameters
        ----------
        arr3D : 3D array
            correction array.
        arrBRDC : 2D array
            eph array.
        statName : str
            correction source name.
        """
        self.config   = config
        self.arr3D    = arr3D
        self.arrBRDC  = arrBRDC
        self.statName = statName
        
    def xyzt(self):
        rsvnum = GLO.GLONASS.MaxNoSV
        fun    = matchIODE.matchIODE(self.arr3D, self.arrBRDC, rsvnum).outputGLO()
        sysArrBRDC = fun[0]
        dateCor    = fun[1]
        brdc       = sysArrBRDC.copy()
        tTagArr = [np.array([gpst2gpsw.gpst2gpsw(x).inDT()[2] for x in dateCor[i]]) 
                   for i in range(self.arr3D.shape[0])]
        res    = [GLOXYZT.GLOXYZT(brdc[i],tTagArr[i]).res()
                  for i in range(self.arr3D.shape[0])]
        resArr = np.array(res)
        XYZT   = np.c_[self.arr3D[:,:,:3], resArr]
        name   = '{}{}{}{}'.format(
            self.config['OFP'], '/Data/', self.statName, '_EPH_R.npy')
        np.save(name, XYZT)
        return XYZT
    