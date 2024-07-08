#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Match EPH
Created on Tue May 10 2022
@author: Stringmaster, Bestie, Boss and some other guy
"""

import numpy as np
from GNSS import SysNames, GPS, GLO, GAL, BDS
from datetime import datetime as dt
from datetime import timedelta
from time_transform import dt2float


class matchEPH:
    def __init__(self, arrBRDC):
        """
        Input:
        
        arrBRDC: eph list each element is the full brdc array
        [tTag, sys, prn, variables....]
        arrBRDC and arrCor must be from the same system
        the inputs brdc should be tailored to contain only 
        the desired system information, no system match is done here
        
        Output:
        first layer in the output list is multiple epochs
        second layer is multiple SVs 
        each output EPH is a row in arrBRDC
        
        perEpoch = allEpoch[calcT.index(timeOfInterest)]
        eph      = perEpoch[prnList.index(prnOfInterest)]
        """

        self.arrBRDC = arrBRDC
        self.ttIdx = 0
        self.sysIdx = 1
        self.prnIdx = 2
        self.iodeIdx = 6

    def timeMatch(self, ephSys, prnList, calcT):
        # input arguments: eph parameters (list)
        # single system only
        parsedEphSys = SysNames(ephSys)

        arrBRDC = self.arrBRDC

        if parsedEphSys.Sys == "G":
            interval = GPS.ephInterval
            delay = GPS.ephDelay
            flag = GPS.ephFlag

        elif parsedEphSys.Sys == "R":
            interval = GLO.ephInterval
            delay = GLO.ephDelay
            flag = GLO.ephFlag

        elif parsedEphSys.Sys == "C":
            interval = BDS.ephInterval
            delay = BDS.ephDelay
            flag = BDS.ephFlag

        elif parsedEphSys.Sys == "E":
            interval = GAL.ephInterval
            delay = GAL.ephDelay
            flag = GAL.ephFlag

        allEpoch = []  # list of matched ephmeris

        for i in range(len(calcT)):
            tt_cor = calcT[i]
            dayRollover = 0
            tagGiven = tt_cor
            tagSecs = tagGiven - dt(
                tagGiven.year, tagGiven.month, tagGiven.day, 0, 0, 0
            )
            tagSecs = tagSecs.seconds

            tagL = tagSecs - (tagSecs % interval) + delay
            tagH = tagL + interval

            if tagH >= 86400:
                tagH = tagH % 86400
                dayRollover = 1

            if (tagSecs - delay) % interval > interval / 2:
                ephTag = tagH
            else:
                ephTag = tagL

            ephDT = dt(
                tagGiven.year, tagGiven.month, tagGiven.day, 0, 0, 0
            ) + timedelta(seconds=ephTag)

            if dayRollover == 1:
                ephDT = ephDT + timedelta(days=1)
            allPRNperEpoch = []
            for j in range(len(prnList)):
                prnMatch = arrBRDC[np.where(int(prnList[j][1:]) == arrBRDC[:, self.prnIdx])]

                timeMatch = prnMatch[
                    np.where(dt2float(ephDT) == prnMatch[:, self.ttIdx])
                ]

                if len(timeMatch) == 0: #checks for irregular eph epochs
                    ephDTlower = ephDT + timedelta(seconds=-interval / 2)
                    ephDThigher = ephDT + timedelta(seconds=interval / 2)
                    timeMatch = prnMatch[
                        np.where(
                            (dt2float(ephDTlower) <= prnMatch[:, 0])
                            & (dt2float(ephDThigher) > prnMatch[:, 0])
                        )
                    ]
                if len(timeMatch) > 1:
                    timeMatch = timeMatch[0]

                if flag == 4:
                    timeMatch = timeMatch[0]
                allPRNperEpoch.append(timeMatch)
            allEpoch.append(np.array(allPRNperEpoch).reshape(-1,33))

        return allEpoch

    def iodeMatch(self, arrCor):
        # single system only
        # arrCor = [tt, prn, iode]
        arrBRDC = self.arrBRDC
        a = []  # list of matched ephmeris
        for i in range(len(arrCor)):
            tt_cor, prn_cor, iode_cor = arrCor[i]
            prnMatch = arrBRDC[
                np.where(prn_cor == arrBRDC[:, self.prnIdx])
            ]  # sv column
            iodeMatch = prnMatch[
                np.where(iode_cor == prnMatch[:, self.iodeIdx])
            ]  # iode column
            if len(iodeMatch) == 1:
                # sometmes len > 1 -> duplicate IODEs need to fix
                pass

            a.append(iodeMatch)

        return a


# brdc = np.load(r"C:\Meeting Room Share\Stuff\Luke\data\BRDC_Original_G.npy")
# cor = np.load(r"C:\Meeting Room Share\Stuff\Luke\data\DLR_COR_G.npy")

# arrBRDC = brdc[:, [0, 2, 6]][350:850]
# arrCor = cor[0, :, [0, 2, 3]].T[0:32]
