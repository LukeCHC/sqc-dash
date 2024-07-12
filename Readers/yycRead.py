# -*- coding: utf-8 -*-
"""
Created on Fri Aug 19 14:25:00 2022

@author: chcuk
"""

# -*- coding: utf-8 -*-
"""
Read Correction
Created on Fri Sep 24 2020
@author: Dr Hui Zhi
"""

from GNSS import Dummy
import gc
import numpy as np
from array import array
import pandas as pd
from time_transform import str2dt


class readYYC:
    def __init__(self, inPath):
        """
        Parameters
        ----------
        config : dict
        """
        self.inPath = inPath

    def read(self):
        path = self.inPath
        oBuf = array("d")
        cBuf = array("d")
        file = open(path, "r")
        flag = 1
        while flag:
            l = file.readline().strip("\n").split()
            if not l:
                file.close()
                flag = 0
            elif l[0] == ">":
                oc = l[1]
                if oc == "ORBIT":
                    time = int(
                        "{}{}{}{}{}{}".format(l[2], l[3], l[4], l[5], l[6], l[7][:2])
                    )
                    interval = l[8]
                    msgNum = int(l[9])
                    msgL = 0
                    while msgL < msgNum:
                        ln = file.readline().strip("\n").split()
                        oBuf.extend(
                            [
                                Dummy.oc[oc],
                                Dummy.yycInterval[interval],
                                time,
                                Dummy.sys[ln[0][0]],
                                float(ln[0][1:]),
                                float(ln[1]),
                                float(ln[2]),
                                float(ln[3]),
                                float(ln[4]),
                                float(ln[5]),
                                float(ln[6]),
                                float(ln[7]),
                            ]
                        )
                        msgL += 1
                elif oc == "CLOCK":
                    time = int(
                        "{}{}{}{}{}{}".format(l[2], l[3], l[4], l[5], l[6], l[7][:2])
                    )
                    interval = l[8]
                    msgNum = int(l[9])
                    msgL = 0
                    while msgL < msgNum:
                        ln = file.readline().strip("\n").split()
                        cBuf.extend(
                            [
                                Dummy.oc[oc],
                                Dummy.yycInterval[interval],
                                time,
                                Dummy.sys[ln[0][0]],
                                float(ln[0][1:]),
                                float(ln[1]),
                                float(ln[2]),
                                float(ln[3]),
                                float(ln[4]),
                            ]
                        )
                        msgL += 1
        # orbit col: orbit, interval, time, sys, prn, IODE, r, a, c, rV, aV, cV
        dfO = pd.DataFrame(np.frombuffer(oBuf, dtype=np.float64).reshape(-1, 12)[:, 2:])
        dfO.columns = ["time", "system", "prn", "IODE", "r", "a", "c", "rV", "aV", "cV"]
        dfO["time"] = pd.Series(map(str2dt, dfO["time"]))
        # clock col: clock, interval, time, sys, prn, IODE, c0, c1, c2
        dfC = pd.DataFrame(np.frombuffer(cBuf, dtype=np.float64).reshape(-1, 9)[:, 2:])
        dfC.columns = ["time", "system", "prn", "IODE", "c0", "c1", "c2"]
        dfC["time"] = pd.Series(map(str2dt, dfC["time"]))
        del oBuf, cBuf
        gc.collect()

        return dfO, dfC


# test = readYYC(
#     r"C:\Users\chcuk\OneDrive\Desktop\IIG\in\rapid\SSRA0CHCSH2230.22C"
# ).read()
