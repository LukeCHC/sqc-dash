# -*- coding: utf-8 -*-
"""
Created on Fri Aug 19 16:03:34 2022

@author: chcuk
"""
#import pandas as pd
from array import array
import GNSS
#from GNSS import GPS, GLO, GAL, BDS, Dummy 
import numpy as np
import gc
#from TimeTrans import str2dt, dt2float
#from datetime import datetime, timedelta

#=== ephsort is different brdcread
#    includes brdcread, also includes sorting out data based on GNSS library
#    brdcread needs not GNSS lib
#    here we call GNSS lib to sort out data needed by xyz calculation
class ephsort():
    def __init__(self, inPath):
        """
        Parameters
        ----------
        config : dict
            variable of read ini file.
        """
        self.inPath = inPath

    def brdc2para(self):
        path = self.inPath
        # BRDC file
        BRDC_list = []
        with open(path, 'r') as f:
            for l in f:
                BRDC_list.append(l)
        # BRDC header
        headerEndIndex = [i for i in range(len(BRDC_list)) if 'END OF HEADER' 
                          in BRDC_list[i]]
        header = BRDC_list[:(headerEndIndex[0]+1)]
        
        for l in range(len(header)-1,-1,-1):
            if 'CORR' not in header[l]:
                del header[l]
        #dfHead = pd.DataFrame(header)
        #dfHead[["Station","1","2"]] = dfHead[0].str.split("",1,expand = True)
        
        # BRDC data
        #data_list = [x.strip('\n') for x in BRDC_list[headerEndIndex[-1]+1:]]
        BRDCData = [x.strip('\n') for x in BRDC_list[headerEndIndex[-1]+1:]]
        #for l in data_list[:]:
        for l in BRDCData[:]:
            if not l:
                del l
                
        #return header_list, data_list
        BRDCSV   = list(set([x[:3] for x in BRDCData if x[:3]!=' '*3]))
        BRDCSYS  = list(set([x[0] for x in BRDCSV]))
        BRDCSV.sort()
        BRDCSYS.sort()
# =============================================================================
#         for x in sys:
#             if x not in BRDCSYS:
#                 raise ValueError('{}{}{}{}'.format(
#                     'Selected Satellite System ', x, ' cannot be found ',
#                     'in the ephemeris file.'))
# =============================================================================
        gBuf = array('d')
        rBuf = array('d')
        cBuf = array('d')
        eBuf = array('d')
        for i in range(len(BRDCData)):
            if BRDCData[i][0]=='G':
                gBuf.extend(GNSS.GPSEphParam(BRDCData, i).res())
            if BRDCData[i][0]=='R':
                rBuf.extend(GNSS.GLOEphParam(BRDCData, i).res())
            if BRDCData[i][0]=='C':
                cBuf.extend(GNSS.BDSEphParam(BRDCData, i).res())
            if BRDCData[i][0]=='E':
                eBuf.extend(GNSS.GALEphParam(BRDCData, i).res())
        gDataArr = np.frombuffer(gBuf, dtype=np.float64).reshape(-1,33)
        rDataArr = np.frombuffer(rBuf, dtype=np.float64).reshape(-1,18)
        cDataArr = np.frombuffer(cBuf, dtype=np.float64).reshape(-1,30)
        eDataArr = np.frombuffer(eBuf, dtype=np.float64).reshape(-1,30)
        del gBuf, rBuf, cBuf, eBuf
        gc.collect()
        hArr = np.full((4,6), np.nan, dtype=object)
        hArr[:,0] = np.float(str(gDataArr[0,0])[:8] + '000000')
        hArr[:,1] = np.array(['BDUT','GAGP','GAUT','GPUT'])
        for x in header:
            if x[:4]=='BDUT':
                hArr[0,2] = np.float(x[5:22].replace('D','E'))
                hArr[0,3] = np.float(x[22:38].replace('D','E'))
                hArr[0,4] = np.float(x[39:45].replace('D','E'))
                hArr[0,5] = np.float(x[46:50].replace('D','E'))
            if x[:4]=='GAGP':
                hArr[1,2] = np.float(x[5:22].replace('D','E'))
                hArr[1,3] = np.float(x[22:38].replace('D','E'))
                hArr[1,4] = np.float(x[39:45].replace('D','E'))
                hArr[1,5] = np.float(x[46:50].replace('D','E'))
            if x[:4]=='GAUT':
                hArr[2,2] = np.float(x[5:22].replace('D','E'))
                hArr[2,3] = np.float(x[22:38].replace('D','E'))
                hArr[2,4] = np.float(x[39:45].replace('D','E'))
                hArr[2,5] = np.float(x[46:50].replace('D','E'))
            if x[:4]=='GPUT':
                hArr[3,2] = np.float(x[5:22].replace('D','E'))
                hArr[3,3] = np.float(x[22:38].replace('D','E'))
                hArr[3,4] = np.float(x[39:45].replace('D','E'))
                hArr[3,5] = np.float(x[46:50].replace('D','E'))
        return gDataArr, rDataArr, cDataArr, eDataArr, hArr
        
    
# =============================================================================
#     def splitSys(self, arrEPH, sys: str):
#         itl = self.intvalEPH
#         if sys == "G":
#             svnum = GPS.MaxNoSV
#             dummy = Dummy.sys["G"]
#         elif sys == "R":
#             svnum = GLO.MaxNoSV
#             dummy = Dummy.sys["R"]
#         elif sys == "C":
#             svnum = BDS.MaxNoSV
#             dummy = Dummy.sys["C"]
#         elif sys == "E":
#             svnum = GAL.MaxNoSV
#             dummy = Dummy.sys["E"]
#         rowPerSV = int(60 / itl * 60 * 24)
#         row = int(60 / itl * 60 * 24 * svnum)
#         #=== columns in dfeph
#         col = ["time", "sys", "PRN", "x", "y", "z"]
#         date = self.mkTimeCol(arrEPH, itl, svnum)
#         arr = np.full((row, len(col)), np.nan)
#         arr[:, 0] = date
#         arr[:, 1] = dummy
#         arr[:, 2] = np.tile(np.arange(1, svnum + 1), rowPerSV)
#         ephIdx = self.mkIdxCol(arrEPH)
#         dfeph = pd.DataFrame(arrEPH, index=ephIdx)
#         dfeph = dfeph.reset_index(drop=True)
#         dfeph.columns = col
#         dfeph["time"] = list(map(str2dt, dfeph["time"].values))
#         return dfeph
#     
#     def mkTimeCol(self, arr2D, itl, svnum):
#         dateS = datetime.strptime(str(int(arr2D[0, 0]))[:8], "%Y%m%d")
#         dateE = dateS + timedelta(hours=23, minutes=59, seconds=55)
#         tTag = pd.date_range(start=dateS, end=dateE, freq=str(itl) + "s").map(
#             lambda x: x.strftime("%Y%m%d%H%M%S.0")
#         )
#         tTagL = tTag.tolist() * svnum
#         tTagL.sort()
#         tTagA = np.array(tTagL)
#         tTagF = tTagA.astype(float)
#         return tTagF
# 
#     def mkIdxCol(self, arr2D):
#         strTime = np.char.mod("%14d", arr2D[:, 0])
#         strSys = np.char.mod("%02d", arr2D[:, 1])
#         strPrn = np.char.mod("%02d", arr2D[:, 2])
#         strIdx = np.char.add(np.char.add(strTime, strSys), strPrn)
#         return strIdx    
#     
#     def eph2npy(self, oPath):
#         """ Saves eph to .npy"""
#         fPath = self.inPath
#         read = self.read(fPath)
#         dfG = read[0]
#         dfG["time"] = list(map(dt2float, dfG["time"]))
#         np.save(np.array(dfG), "{}/{}".format(oPath, "eph_G.npy"))
#         del dfG
#         dfR = read[1]
#         dfR["time"] = list(map(dt2float, dfR["time"]))
#         np.save(np.array(dfR), "{}/{}".format(oPath, "eph_R.npy"))
#         del dfR
#         dfC = read[2]
#         dfC["time"] = list(map(dt2float, dfC["time"]))
#         np.save(np.array(dfC), "{}/{}".format(oPath, "eph_C.npy"))
#         del dfC
#         dfE = read[3]
#         dfE["time"] = list(map(dt2float, dfE["time"]))
#         np.save(np.array(dfE), "{}/{}".format(oPath, "eph_E.npy"))
#         del dfE
#         return True 
# =============================================================================
    
#test = readBRDC(r"C:\Users\chcuk\OneDrive\Desktop\IIG\in\rapid\BRDC00IGS_R_20222220000_01D_MN.rnx").read()