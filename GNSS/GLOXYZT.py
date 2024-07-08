# -*- coding: utf-8 -*-
"""
GLONASS XYZT
Created on Wed Jun 21 2021
@author: Dr Hui Zhi
"""

from GNSS import GPS
from time_transform.time_format import utcTime
import numpy as np
from datetime import datetime as dt

class GLOXYZT():
    def __init__(self, IODEarr, tTagArr):
        self.IODEarr = IODEarr
        #= dt(gpsTime), to be calculated, ntag
        if (type(tTagArr) == dt): # only one epoch
            self.tTagArr = [tTagArr]
            self.ntag = 1
        elif (type(tTagArr) == list): # multiple epochs
            self.tTagArr = tTagArr
            self.ntag = len(self.tTagArr)
        #self.tTagArr = tTagArr # gpsTime
        
    def calculateRate(self, motionRowI, accelRowI):
        EarthRate = 7.292115E-05        # radian
        Gravity   = 398600.4418               # all in km
        Radius    = 6378.136                # all in km
        C20       = -1082.62575E-06
        
        posX   = motionRowI[0]
        posY   = motionRowI[1]
        posZ   = motionRowI[2]
        velX   = motionRowI[3]
        velY   = motionRowI[4]
        velZ   = motionRowI[5]
        accelX = accelRowI[0]
        accelY = accelRowI[1]
        accelZ = accelRowI[2]
        
        r2 = posX**2 + posY**2 + posZ**2
        r  = np.sqrt(r2)
        muBar = Gravity / r2
        rho   = Radius / r
        rho2  = rho*rho
        
        xBar  = posX / r
        yBar  = posY / r
        zBar  = posZ / r
        zBar2 = zBar * zBar

        cFactor = (3.0/2.0) * C20 * muBar * rho2

        w  = EarthRate
        w2 = w * w

        rotX = w2 * posX + 2.0 * w * velY
        rotY = w2 * posY - 2.0 * w * velX

        vX = -muBar*xBar + cFactor*xBar*(1.0 - 5.0*zBar2) + accelX + rotX
        vY = -muBar*yBar + cFactor*yBar*(1.0 - 5.0*zBar2) + accelY + rotY
        vZ = -muBar*zBar + cFactor*zBar*(3.0 - 5.0*zBar2) + accelZ
        return np.array([velX, velY, velZ, vX, vY, vZ])
    
    def RungeKuttaInteg(self, motion, step, accel):
        D1 = self.calculateRate(motion                  , accel)
        D2 = self.calculateRate((motion + D1*(step/2.0)), accel)
        D3 = self.calculateRate((motion + D2*(step/2.0)), accel)
        D4 = self.calculateRate((motion + D3* step     ), accel)
        res = motion + (D1 + D2*2.0 + D3*2.0 + D4)*(step/6.0)
        return res
    
    def integrate(self, motion, dt, step, accel):
        result = motion
        # dt is float
        for i in range(result.shape[0]):
            if dt[i] >= 0.0:
                while dt[i]  >= step:
                    result[i] = self.RungeKuttaInteg(result[i], step, accel[i])
                    dt[i]     = dt[i] - step
                if dt[i] > 0.0:
                    result[i] = self.RungeKuttaInteg(result[i], dt[i], accel[i])
            else:
                while dt[i]  <= -step:
                    result[i] = self.RungeKuttaInteg(result[i], -step, accel[i])
                    dt[i]     = dt[i] + step;
                if dt[i] < 0.0:
                    result[i] = self.RungeKuttaInteg(result[i], dt[i], accel[i])
        return result
        """
        # dt is a numpy array
        if dt.any() >= 0.0:
            idx1 = np.where(dt >= step)[0]
            while dt.any() >= step:
                result[idx1,:] = self.RungeKuttaInteg(
                    result[idx1,:], step, accel[idx1,:])
                dt[idx1] -= step
                idx1 = np.where(dt >= step)[0]
            if dt.any() >= 0.0:
                idx2 = np.where(dt >= 0)[0]
                result[idx2,:] = self.RungeKuttaInteg(
                    result[idx2,:], dt[idx2,None], accel[idx2,:])
        if dt.any() < 0.0:
            idx3 = np.where(dt <= -step)[0]
            while dt.any() <= -step:
                result[idx3,:] = self.RungeKuttaInteg(
                    result[idx3,:], -step, accel[idx3,:])
                dt[idx3] += step
                idx3 = np.where(dt <= -step)[0]
            if dt.any() < 0.0:
                idx4 = np.where(dt < 0)[0]
                result[idx4,:] = self.RungeKuttaInteg(
                    result[idx4,:], dt[idx4,None], accel[idx4,:])
        
        # dt is float
        if dt >= 0.0:
            while dt  >= step:
                result = self.RungeKuttaInteg(result, step, accel)
                dt     = dt - step
            if dt > 0.0:
                result = self.RungeKuttaInteg(result, dt, accel)
        else:
            while dt  <= -step:
                result = self.RungeKuttaInteg(result, -step, accel)
                dt     = dt + step;
            if dt < 0.0:
                result = self.RungeKuttaInteg(result, dt, accel)
        """
        
    def res(self):
        selData  = self.IODEarr
        TOC      = selData[:,0]  # UTC time in R brdc file
        Tau      = selData[:,3]
        Gamma    = selData[:,4]
        # mftime   = selData[:,5]
        posX     = selData[:,6]
        velX     = selData[:,7]
        accelX   = selData[:,8]
        # heathX   = selData[:,9]
        posY     = selData[:,10]
        velY     = selData[:,11]
        accelY   = selData[:,12]
        # freq     = selData[:,13]
        posZ     = selData[:,14]
        velZ     = selData[:,15]
        accelZ   = selData[:,16]
        # age      = selData[:,17]
        
        step    = 20
        #leapSec = 18
        
        #tocDT   = np.array([datetime.strptime(str(x),'%Y%m%d%H%M%S.%f') 
        #                    for x in TOC])
        toc  = np.array([utcTime(x).UTC2GPS().datetime for x in TOC])
                             
        #tb      = tocSOW + leapSec
        dt      = [(self.tTagArr[i] - toc[i]).total_seconds() for i in range(self.ntag)]       # - travelTime
        motion  = np.c_[posX, posY, posZ, velX, velY, velZ]
        accel   = np.c_[accelX, accelY, accelZ]
        result  = self.integrate(motion, dt, step, accel)
        pos     = result[:,:3] * 1000
        vel     = result[:,3:6] * 1000
        
        rv     = np.hstack(
            [np.dot(pos[n],vel[n]) for n in range(pos.shape[0])])
        speRel = -2 * rv / GPS.c**2
        clock  = Tau + Gamma * dt - speRel
        dclock = Gamma
        
        return np.c_[pos, vel, clock, dclock]
    