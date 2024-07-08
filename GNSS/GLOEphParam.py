# -*- coding: utf-8 -*-
"""
GLONASS Ephemeris Parameter
Created on Thu May 10 2021
@author: Dr Hui Zhi
"""

# import GNSS
from GNSS import Dummy
import numpy as np
from datetime import datetime, timedelta


class GLOEphParam:
    dType_o = np.dtype(
        [
            ("time", np.float64),
            ("sys", np.float64),
            ("PRN", np.float64),
            ("description", np.float64),
        ]
    )

    def __init__(self, blockData, num):
        self.blockData = blockData
        self.num = num

        # SV/EPOCH/SV CLK
        self.sat_sys = self.blockData[self.num][0]
        self.prn = int(self.blockData[self.num][1:3])
        self.toc = self.blockData[self.num][4:8]
        self.obs_t = self.blockData[self.num][4:23]
        self.bias = float(self.blockData[self.num][23:42])
        self.rel_bias = float(self.blockData[self.num][42:61])
        self.mftime = float(self.blockData[self.num][61:80])

        # Broadcast orbit - 1
        self.posX = float(self.blockData[self.num + 1][4:23])
        self.velX = float(self.blockData[self.num + 1][23:42])
        self.accX = float(self.blockData[self.num + 1][42:61])
        self.heathX = float(self.blockData[self.num + 1][61:80])

        # Broadcast orbit - 2
        self.posY = float(self.blockData[self.num + 2][4:23])
        self.velY = float(self.blockData[self.num + 2][23:42])
        self.accY = float(self.blockData[self.num + 2][42:61])
        self.freq = float(self.blockData[self.num + 2][61:80])

        # Broadcast orbit - 3
        self.posZ = float(self.blockData[self.num + 3][4:23])
        self.velZ = float(self.blockData[self.num + 3][23:42])
        self.accZ = float(self.blockData[self.num + 3][42:61])
        self.age = float(self.blockData[self.num + 3][61:80])

        gpsUTC = datetime(1980, 1, 6, 0, 0, 0)
        tMoscow = datetime.strptime(self.obs_t,'%Y %m %d %H %M %S') - gpsUTC + timedelta(seconds=3 * 3600)
        # tMoscow = self.toc - gpsUTC + timedelta(seconds=3 * 3600)
        self.iode = int(tMoscow.seconds / 900)

    def res(self):
        # Obs time
        obs_tM = int(
            "{}{}{}{}{}{}".format(
                self.blockData[self.num][4:8],
                self.blockData[self.num][9:11],
                self.blockData[self.num][12:14],
                self.blockData[self.num][15:17],
                self.blockData[self.num][18:20],
                self.blockData[self.num][21:23],
            )
        )
        resList = [
            obs_tM,
            Dummy.sys[self.sat_sys],
            self.prn,
            self.bias,
            self.rel_bias,
            self.mftime,
            self.posX,
            self.velX,
            self.accX,
            self.heathX,
            self.posY,
            self.velY,
            self.accY,
            self.freq,
            self.posZ,
            self.velZ,
            self.accZ,
            self.age,
        ]
        return resList
