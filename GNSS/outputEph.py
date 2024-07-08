# -*- coding: utf-8 -*-
"""
Select and output ephemeris original data
Created on Wed Aug 12 2020
@author: Dr Hui Zhi
"""

from GNSS import readEph,GPSEphParam
from GNSS import GLOEphParam,BDSEphParam,GALEphParam 

import weakref
import gc
from array import array
import numpy as np

class outputEph():    
    def __init__(self, config):
        self.config = config
    
    def select(self, num):
        sys      = [x.strip() for x in self.config['SYS'].split(',')]
        r        = readEph.readEph(self.config)
        header   = weakref.ref(r)().read(num)[0]
        BRDCData = weakref.ref(r)().read(num)[1]
        BRDCSV   = list(set([x[:3] for x in BRDCData if x[:3]!=' '*3]))
        BRDCSYS  = list(set([x[0] for x in BRDCSV]))
        BRDCSV.sort()
        BRDCSYS.sort()
        for x in sys:
            if x not in BRDCSYS:
                raise ValueError('{}{}{}{}'.format(
                    'Selected Satellite System ', x, ' cannot be found ',
                    'in the ephemeris file.'))
        gBuf = array('d')
        rBuf = array('d')
        cBuf = array('d')
        eBuf = array('d')
        for i in range(len(BRDCData)):
            if BRDCData[i][0]=='G':
                gBuf.extend(GPSEphParam.GPSEphParam(BRDCData, i).res())
            if BRDCData[i][0]=='R':
                rBuf.extend(GLOEphParam.GLOEphParam(BRDCData, i).res())
            if BRDCData[i][0]=='C':
                cBuf.extend(BDSEphParam.BDSEphParam(BRDCData, i).res())
            if BRDCData[i][0]=='E':
                eBuf.extend(GALEphParam.GALEphParam(BRDCData, i).res())
        gDataArr = np.frombuffer(gBuf, dtype=np.float64).reshape(-1,33)
        rDataArr = np.frombuffer(rBuf, dtype=np.float64).reshape(-1,18)
        cDataArr = np.frombuffer(cBuf, dtype=np.float64).reshape(-1,30)
        eDataArr = np.frombuffer(eBuf, dtype=np.float64).reshape(-1,30)
        del r, gBuf, rBuf, cBuf, eBuf
        gc.collect()
        hArr = np.full((4,6), np.nan, dtype=object)
        hArr[:,0] = np.float(str(gDataArr[0,0])[:8] + '000000')
        hArr[:,1] = np.array(['BDUT','GAGP','GAUT','GPUT'])
        for x in header:
            if x[:4]=='BDUT':
                hArr[0,2] = np.float(x[5:22])
                hArr[0,3] = np.float(x[22:38])
                hArr[0,4] = np.float(x[39:45])
                hArr[0,5] = np.float(x[46:50])
            if x[:4]=='GAGP':
                hArr[1,2] = np.float(x[5:22])
                hArr[1,3] = np.float(x[22:38])
                hArr[1,4] = np.float(x[39:45])
                hArr[1,5] = np.float(x[46:50])
            if x[:4]=='GAUT':
                hArr[2,2] = np.float(x[5:22])
                hArr[2,3] = np.float(x[22:38])
                hArr[2,4] = np.float(x[39:45])
                hArr[2,5] = np.float(x[46:50])
            if x[:4]=='GPUT':
                hArr[3,2] = np.float(x[5:22])
                hArr[3,3] = np.float(x[22:38])
                hArr[3,4] = np.float(x[39:45])
                hArr[3,5] = np.float(x[46:50])
        return gDataArr, rDataArr, cDataArr, eDataArr, hArr
    
    def output(self):
        fileNum   = len(readEph.readEph(self.config).path()[0])
        sel       = [self.select(i) for i in range(fileNum)]
        gBRDCArr  = np.vstack([sel[i][0] for i in range(fileNum)])
        rBRDCArr  = np.vstack([sel[i][1] for i in range(fileNum)])
        cBRDCArr  = np.vstack([sel[i][2] for i in range(fileNum)])
        eBRDCArrR = np.vstack([sel[i][3] for i in range(fileNum)])
        del sel
        gc.collect()
        col0 = np.char.mod('%14d', eBRDCArrR[:,0])
        col1 = np.char.mod('%1d', eBRDCArrR[:,1])
        col2 = np.char.mod('%02d', eBRDCArrR[:,2])
        eBRDCstr = np.char.add(np.char.add(col0, col1), col2)
        vals, idx_st, count = np.unique(
            eBRDCstr, return_index=True, return_counts=True)
        eBRDCArr = eBRDCArrR[idx_st,:]
        name = '{}{}'.format(
            self.config['OFP'], '/Data/BRDC_Original_G.npy')
        np.save(name, gBRDCArr)
        name = '{}{}'.format(
            self.config['OFP'], '/Data/BRDC_Original_R.npy')
        np.save(name, rBRDCArr)
        name = '{}{}'.format(
            self.config['OFP'], '/Data/BRDC_Original_C.npy')
        np.save(name, cBRDCArr)
        name = '{}{}'.format(
            self.config['OFP'], '/Data/BRDC_Original_E.npy')
        np.save(name, eBRDCArr)
        # headArr = np.array([sel[i][4] for i in range(1, fileNum-1)])
        # name    = '{}{}'.format(
        #         self.config['OFP'], '/Data/BRDC_TCOR.npy')
        # np.save(name, headArr)
    