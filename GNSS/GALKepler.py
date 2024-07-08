# -*- coding: utf-8 -*-
"""
GALILEO Kepler
Created on Wed Aug 12 2020
@author: Dr Hui Zhi
"""

#import Core
#import GNSS
# from Core import gst2gpsw
from GNSS import GAL,GPS
import numpy as np
from datetime import datetime as dt
from time_transform.time_format import GalTime

class GALKepler():
    def __init__(self, IODEarr, tTagArr):
        self.IODEarr = IODEarr
        #self.tTagArr = tTagArr
        if (type(tTagArr) == dt): # only one epoch
            self.tTagArr = [tTagArr]
            self.ntag = 1
        elif (type(tTagArr) == list): # multiple epochs
            self.tTagArr = tTagArr
            self.ntag = len(self.tTagArr)
            
    def res(self):
        selData   = self.IODEarr
        bias      = selData[:,0]
        drift     = selData[:,1]
        driftRate = selData[:,2]
        Crs       = selData[:,4]
        Deltan    = selData[:,5]
        M0        = selData[:,6]
        Cuc       = selData[:,7]
        e         = selData[:,8]
        Cus       = selData[:,9]
        sqrtA     = selData[:,10]
        Toe_SOW   = selData[:,11]
        Cic       = selData[:,12]
        omega0    = selData[:,13]
        Cis       = selData[:,14]
        i0        = selData[:,15]
        Crc       = selData[:,16]
        omega     = selData[:,17]
        omegaDOT  = selData[:,18]
        IDOT      = selData[:,19]
        Toe_Week  = selData[:,21]
        # FitInterval = selData[:,28]
        miu       = GAL.miu
        pi        = GPS.Pi
        # F         = GNSS.GPS.F
        rad       = GPS.rad

        A  = sqrtA**2                     # Semi-major axis
        n0 = np.sqrt(miu / A**3)        # Computed mean motion - rad/sec

        #toeweek_rec = gpsv2gpst(tpL_str[k])[0]
        #t = self.tTagArr
        #tk = t - gst2gpsw.gst2gpsw(Toe_Week,Toe_SOW)[1]                  # Time from ephemeris reference epoch
        Rollover = GalTime().Rollover
        toc = [GalTime([Toe_Week[i],Toe_SOW[i],Rollover]).GAL2GPS().datetime 
                   for i in range(self.ntag)]
        tk = np.array([(self.tTagArr[i] - toc[i]).total_seconds()  
                       for i in range(self.ntag)]) 
# =============================================================================
#         ind1 = np.where(tk > 302400.0)
#         ind2 = np.where(tk < -302400.0)
#         ind3 = np.where((-302400.0 <= tk) & (tk <= 302400.0))
#         tk[ind1] = t[ind1] - gst2gpsw.gst2gpsw(Toe_Week,Toe_SOW)[1] [ind1] - 604800.0
#         tk[ind2] = t[ind2] - gst2gpsw.gst2gpsw(Toe_Week,Toe_SOW)[1] [ind2] + 604800.0
#         tk[ind3] = t[ind3] - gst2gpsw.gst2gpsw(Toe_Week,Toe_SOW)[1] [ind3]
# =============================================================================

        #if tk>302400.0:
        #    tk = t - Toe_SOW - 604800.0
        #elif tk<-302400.0:
        #    tk = t - Toe_SOW + 604800.0
        #else:
        #    tk = t - Toe_SOW

        n  = n0 + Deltan                  # Corrected mean motion
        Mk = M0 + n * tk                  # Mean anomaly
        # Mk = Ek - e*np.sin(Ek)        # Kepler's equation for eccentric anomaly (may be solved by iteration) - radians
        # if Mk<0:
        #     Mk = M0 + n*tk + 2*pi

        # Ek calculation                  # Eccentric anomaly
        Ek    = pi
        Mn    = Ek - e * np.sin(Ek)
        Ek    = Ek + (Mk - Mn) / (1 - e * np.cos(Ek))

        count = 1
        boolArrD = abs(Mk-Ek)>1.0E-15
        while boolArrD.any() and count<10:
            Mn[boolArrD] = Ek[boolArrD] - e[boolArrD] * np.sin(Ek[boolArrD])
            Ek[boolArrD] = (Ek[boolArrD] + (Mk[boolArrD] - Mn[boolArrD]) /
                            (1 - e[boolArrD] * np.cos(Ek[boolArrD])))
            boolArrD = abs(Mk-Ek)>1.0E-15
            count += 1

        # Clock and ClockRate
        clk  = bias + tk * (drift + tk * driftRate)
        # RelativeSeconds = F * e * sqrtA * np.sin(Ek)
        # clk  = (bias + FitInterval * (drift + FitInterval * driftRate) +
                # RelativeSeconds)
        rate = drift

        vk = np.arctan2((np.sqrt(1 - e**2) * np.sin(Ek)) /
                        (1 - e *  np.cos(Ek)),
                        (np.cos(Ek)-e)/(1-e*np.cos(Ek)))

        phiK = vk + omega                                            # Argument of latitude in radians

        # Second harmonic perturbations
        dUk = Cus * np.sin(phiK * 2) + Cuc * np.cos(phiK * 2)    # Argument of latitude correction
        dRk = Crs * np.sin(phiK * 2) + Crc * np.cos(phiK * 2)    # Radius correction
        dIk = Cis * np.sin(phiK * 2) + Cic * np.cos(phiK * 2)    # Correction to inclination

        uk = phiK + dUk		                                         # Corrected argument of latitude
        rk = A * (1 - e * np.cos(Ek)) + dRk                        # Corrected radius
        ik = i0 + dIk + IDOT * tk	                                 # Corrected inclination

        xkv = rk * np.cos(uk)	                                     # Positions in orbital plane
        ykv = rk * np.sin(uk)

        omegak = omega0 + (omegaDOT - rad) * tk - rad * Toe_SOW

        xk = xkv * np.cos(omegak) - ykv * np.cos(ik) * np.sin(omegak)
        yk = xkv * np.sin(omegak) + ykv * np.cos(ik) * np.cos(omegak)
        zk = ykv * np.sin(ik)

        # Derivatives
        Xkv  = (1.0 - e * np.cos(Ek))
        dEk  = n / Xkv
        dVk  = np.sqrt(1 - e**2) * n / (Xkv**2)

        Xkv  = dVk * 2
        dUkt = (Cus * np.cos(phiK * 2) - Cuc*np.sin(phiK * 2)) * Xkv
        dRkt = (Crs * np.cos(phiK * 2) - Crc*np.sin(phiK * 2)) * Xkv
        dIkt = (Cis * np.cos(phiK * 2) - Cic*np.sin(phiK * 2)) * Xkv

        Rdt  = dEk * (e * A * np.sin(Ek)) + dRkt

        dOk = omegaDOT - rad
        dIk = IDOT + dIkt
        dUk = dVk  + dUkt

        xkv = (Rdt * xk / rk) - dOk * yk + dIk * zk * np.sin(omegak)
        xkv = xkv - (dUk*rk*(np.sin(uk)*np.cos(omegak) +
                             np.cos(uk)*np.cos(ik)*np.sin(omegak)))

        ykv = (Rdt*yk/rk) + dOk*xk - dIk*zk*np.sin(omegak)
        ykv = ykv - (dUk*rk*(np.sin(uk)*np.sin(omegak) -
                             np.cos(uk)*np.cos(ik)*np.cos(omegak)))

        zkv = ((Rdt*zk/rk) + dIk*rk*np.sin(uk)*np.cos(ik) +
               dUk*rk*np.cos(uk)*np.sin(ik))
        return [xk, yk, zk, xkv, ykv, zkv, clk, rate]
