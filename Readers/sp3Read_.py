# -*- coding: utf-8 -*-
"""
Created on Wed Aug 17 15:18:16 2022

@author: chcuk
"""
import numpy as np
from datetime import datetime, timedelta
from GNSS import GPS, GLO, GAL, BDS, Dummy
from array import array
import pandas as pd
import gc
from TimeTrans import str2dt, dt2float


class readSP3:
    def __init__(self, inPath, intvalSP3: int):
        self.intvalSP3 = intvalSP3
        self.inPath = inPath

    def read(self):
        file = open(self.inPath, "r")
        buf = array("d")
        flag = 1
        while flag:
            l = file.readline().strip("\n").split()
            if not l:
                file.close()
                flag = 0
            elif l[0] == "*":
                timetag = int(
                    "{}{}{}{}{}{}".format(
                        "%04d" % int(l[1]),
                        "%02d" % int(l[2]),
                        "%02d" % int(l[3]),
                        "%02d" % int(l[4]),
                        "%02d" % int(l[5]),
                        "%02d" % float(l[6]),
                    )
                )
                flagB = 1
                while flagB:
                    t = file.tell()
                    l = file.readline().strip("\n").split()
                    if l[0] == "*" or "EOF" in l:
                        file.seek(t)
                        flagB = 0
                    elif l[0][0] == "P":
                        sys = Dummy.sys[l[0][1]]
                        prn = int(l[0][2:])
                        x = float(l[1])
                        y = float(l[2])
                        z = float(l[3])
                        clk = float(l[4])
                        buf.extend([timetag, sys, prn, x, y, z, clk])
        arr0 = np.frombuffer(buf, dtype=np.float64).reshape(-1, 7)
        del buf
        gc.collect()
        arrSP3 = np.c_[arr0[:, :3], arr0[:, 3:6] * 1e3, arr0[:, 6, None] / 1e-6]
        sp3ArrG = arrSP3[np.where(arrSP3[:, 1] == Dummy.sys["G"])]
        sp3ArrR = arrSP3[np.where(arrSP3[:, 1] == Dummy.sys["R"])]
        sp3ArrC = arrSP3[np.where(arrSP3[:, 1] == Dummy.sys["C"])]
        sp3ArrE = arrSP3[np.where(arrSP3[:, 1] == Dummy.sys["E"])]
        output = []
        if len(sp3ArrG):
            output.append(self.splitSys(sp3ArrG, "G"))
        else: 
            output.append([])
        if len(sp3ArrR):
            output.append(self.splitSys(sp3ArrR, "R"))
        else: 
            output.append([])
        if len(sp3ArrC):
            output.append(self.splitSys(sp3ArrC, "C"))
        else: 
            output.append([])
        if len(sp3ArrE):
            output.append(self.splitSys(sp3ArrE, "E"))
        else: 
            output.append([])
        return output
    
    def readMulti(self, pathList):
        """list of file paths, must be in order of date"""
        days = []
        for i in range(len(pathList)):
            self.inPath = pathList[i]
            days.append(self.read())
            
        output = []
        try:
            output.append(pd.concat([x[0] for x in days]))
        except:
            output.append([])
        try:
            output.append(pd.concat([x[1] for x in days]))
        except:
            output.append([])
        try:
            output.append(pd.concat([x[2] for x in days]))
        except:
            output.append([])
        try:
            output.append(pd.concat([x[3] for x in days]))
        except:
            output.append([])
        return output

    def sp32npy(self, oPath):
        """ Saves sp3 to .npy"""
        fPath = self.inPath
        read = self.read(fPath)
        dfG = read[0]
        dfG["time"] = list(map(dt2float, dfG["time"]))
        np.save(np.array(dfG), "{}/{}".format(oPath, "sp3_G.npy"))
        del dfG
        dfR = read[1]
        dfR["time"] = list(map(dt2float, dfR["time"]))
        np.save(np.array(dfR), "{}/{}".format(oPath, "sp3_R.npy"))
        del dfR
        dfC = read[2]
        dfC["time"] = list(map(dt2float, dfC["time"]))
        np.save(np.array(dfC), "{}/{}".format(oPath, "sp3_C.npy"))
        del dfC
        dfE = read[3]
        dfE["time"] = list(map(dt2float, dfE["time"]))
        np.save(np.array(dfE), "{}/{}".format(oPath, "sp3_E.npy"))
        del dfE
        return True

    def mkTimeCol(self, arr2D, itl: int, svnum):
        dateS = datetime.strptime(str(int(arr2D[0, 0]))[:8], "%Y%m%d")
        dateE = dateS + timedelta(hours=23, minutes=59, seconds=55)
        tTag = pd.date_range(start=dateS, end=dateE, freq=str(itl) + "s").map(
            lambda x: x.strftime("%Y%m%d%H%M%S.0")
        )
        tTagL = tTag.tolist() * svnum
        tTagL.sort()
        tTagA = np.array(tTagL)
        tTagF = tTagA.astype(float)
        return tTagF

    def mkIdxCol(self, arr2D):
        strTime = np.char.mod("%14d", arr2D[:, 0])
        strSys = np.char.mod("%02d", arr2D[:, 1])
        strPrn = np.char.mod("%02d", arr2D[:, 2])
        strIdx = np.char.add(np.char.add(strTime, strSys), strPrn)
        return strIdx

    def splitSys(self, arrSP3, sys: str):
        itl = self.intvalSP3
        if sys == "G":
            svnum = GPS.MaxNoSV
            dummy = Dummy.sys["G"]
        elif sys == "R":
            svnum = GLO.MaxNoSV
            dummy = Dummy.sys["R"]
        elif sys == "C":
            svnum = BDS.MaxNoSV
            dummy = Dummy.sys["C"]
        elif sys == "E":
            svnum = GAL.MaxNoSV
            dummy = Dummy.sys["E"]
        rowPerSV = int(60 / itl * 60 * 24)
        row = int(60 / itl * 60 * 24 * svnum)
        col = ["time", "sys", "prn", "x", "y", "z", "clock"]
        date = self.mkTimeCol(arrSP3, itl, svnum)
        arr = np.full((row, len(col)), np.nan)
        arr[:, 0] = date
        arr[:, 1] = dummy
        arr[:, 2] = np.tile(np.arange(1, svnum + 1), rowPerSV)
        sp3Idx = self.mkIdxCol(arrSP3)
        dfsp3 = pd.DataFrame(arrSP3, index=sp3Idx)
        dfsp3 = dfsp3.reset_index(drop=True)
        dfsp3.columns = col
        dfsp3["time"] = list(map(str2dt, dfsp3["time"].values))
        return dfsp3

# day0 = r"C:\Users\chcuk\OneDrive\Desktop\IIG\in\rapid\GFZ0MGXRAP_20222220000_01D_05M_ORB.SP3"
# day1 = r"C:\Users\chcuk\OneDrive\Desktop\IIG\in\rapid\GFZ0MGXRAP_20222230000_01D_05M_ORB.SP3"
# day2 = r"C:\Users\chcuk\OneDrive\Desktop\IIG\in\rapid\GFZ0MGXRAP_20222240000_01D_05M_ORB.SP3"

# days = [day0,day1,day2]
# test = readSP3('', 900).readMulti(days)