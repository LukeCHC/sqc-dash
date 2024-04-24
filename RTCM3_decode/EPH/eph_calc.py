# -*- coding: utf-8 -*-
"""
Created on Wed Nov 24 08:55:23 2021
# Eph 2 xyz
# from decoded EPH to CLass needed by GNSS 
@author: Zoe Chen
"""
#import GNSS
#import numpy as np
from time_transform.time_format import GpsTime,dt2float
#import time
#import Coord
#from datetime import datetime
#import Common.coord_and_time_transformations as trafo
from GNSS import GPSKepler
from GNSS.BDSKepler import BDSKepler
from GNSS.GALKepler import GALKepler
from GNSS.GLOXYZT import GLOXYZT
#from GNSS import GPS
import numpy as np


def GPS_EPH2BRDC(EPH):
    # Input EPH class
    # Output eph 2D array needed by GNSS
    # IODEarr in GNSS/GPSKepler.py
    # Ref:     # GNSS/GPSEphParam
    BRDC = []
    # TOTAL = 30 [0-29]
    # self.bias,           self.drift,    self.driftRate, self.IODE, 
    #  self.Crs,          self.Deltan,           self.M0, self.Cuc,      
    #  self.e,                self.Cus,       self.sqrtA, self.Toe_SOW,       
    # self.Cic,            self.omega0,         self.Cis, self.i0,               
    # self.Crc,             self.omega,    self.omegaDOT, self.IDOT, 
    # self.CodesOnL2, self.Toe_GPSWeek, self.L2PDataFlag, self.SVaccuracy, 
    # self.SVhealth,          self.TGD,        self.IODC, self.TransmissionTime, 
    # self.FitInterval,         refTime]
    # 0-19 used for calculation
    BRDC.append(EPH.af0)
    BRDC.append(EPH.af1)
    BRDC.append(EPH.af2)
    BRDC.append(EPH.iode)
    
    BRDC.append(EPH.crs)
    BRDC.append(EPH.dn)
    BRDC.append(EPH.m0)
    BRDC.append(EPH.cuc)
    
    BRDC.append(EPH.ecc)
    BRDC.append(EPH.cus)
    BRDC.append(EPH.root_a)
    BRDC.append(EPH.toe)           # Toe_SOW
    
    BRDC.append(EPH.cic)
    BRDC.append(EPH.omega_0)
    BRDC.append(EPH.cis)
    BRDC.append(EPH.i0)
    
    BRDC.append(EPH.crc)
    BRDC.append(EPH.omega)
    BRDC.append(EPH.omega_dot)
    BRDC.append(EPH.idot)
    
    #===
    BRDC.append(EPH.code_L2)
    BRDC.append(EPH.week)          #? # Toe_GPSWeek
    BRDC.append(EPH.L2P)
    BRDC.append(EPH.ura)
    
    BRDC.append(EPH.health)
    BRDC.append(EPH.tgd)
    BRDC.append(EPH.iodc)
    BRDC.append(0)                 # No TransmissionTime in EPH
    BRDC.append(EPH.interval)
    
    # refTime = int(datetime.strftime(
    #         #TIME.gpsw2gpst(self.Toe_GPSWeek, self.Toe_SOW), '%Y%m%d%H%M%S'))
    #          TimeTrans.gpsw2gpst(EPH.week, EPH.toe), '%Y%m%d%H%M%S'))
    refTime = dt2float(gpsTime([EPH.week,EPH.toe,gpsTime().Rollover]).datetime)
    BRDC.append(refTime)           #? refTime
            
    return BRDC

def BDS_EPH2BRDC(EPH):
    # Input EPH class
    # Output eph 2D array needed by GNSS
    # IODEarr in GNSS/BDSKepler.py
    # Ref:     # GNSS/BDSEphParam
    BRDC = []
    #=== obs_tM, Dummy.Dummy.sys[self.sat_sys], self.prn,
    #         self.bias, self.drift, self.driftRate, self.IODE, self.Crs, 
    #         self.Deltan, self.M0, self.Cuc, self.e, self.Cus, self.sqrtA, 
    #         self.Toe_SOW, self.Cic, self.omega0, self.Cis, self.i0, self.Crc, 
    #         self.omega, self.omegaDOT, self.IDOT, self.Toe_BDSWeek, 
    #         self.SVaccuracy, self.SVhealth, self.TGD1, self.TGD2, 
    #         self.TransmissionTime, self.AODC]
    # 0-20 used for calculation
    BRDC.append(EPH.af0)
    BRDC.append(EPH.af1)
    BRDC.append(EPH.af2)
    BRDC.append(EPH.iode)
    
    BRDC.append(EPH.crs)
    BRDC.append(EPH.dn)
    BRDC.append(EPH.m0)
    BRDC.append(EPH.cuc)
    
    BRDC.append(EPH.ecc)
    BRDC.append(EPH.cus)
    BRDC.append(EPH.root_a)
    BRDC.append(EPH.toe)           # Toe_SOW
    
    BRDC.append(EPH.cic)
    BRDC.append(EPH.omega_0)
    BRDC.append(EPH.cis)
    BRDC.append(EPH.i0)
    
    BRDC.append(EPH.crc)
    BRDC.append(EPH.omega)
    BRDC.append(EPH.omega_dot)
    BRDC.append(EPH.idot)
    
    #===
    BRDC.append(EPH.week)          #? # BDSWeek

    #BRDC.append(EPH.ura)           # SVaccuracy
    BRDC.append(0)                  # ? no SVaccuracy  
    BRDC.append(EPH.health)
    BRDC.append(EPH.tgd1)
    BRDC.append(EPH.tgd2)
    BRDC.append(0)                 # No TransmissionTime in EPH
    BRDC.append(EPH.iodc)
    
    #BRDC.append(EPH.interval)
    
    #refTime = dt2float(gpsTime([EPH.gpsweek,EPH.gpstoe,gpsTime().Rollover]).datetime)
    #BRDC.append(refTime)           #? refTime
            
    return BRDC


def GAL_EPH2BRDC(EPH):
    # Input EPH class
    # Output eph 2D array needed by GNSS
    # IODEarr in GNSS/BDSKepler.py
    # Ref:     # GNSS/BDSEphParam
    BRDC = []
    #=== obs_tM, Dummy.Dummy.sys[self.sat_sys], self.prn,
    #         self.bias, self.drift, self.driftRate, self.IODE, self.Crs, 
    #         self.Deltan, self.M0, self.Cuc, self.e, self.Cus, self.sqrtA, 
    #         self.Toe_SOW, self.Cic, self.omega0, self.Cis, self.i0, self.Crc, 
    #         self.omega, self.omegaDOT, self.IDOT, self.Toe_BDSWeek, 
    #         self.SVaccuracy, self.SVhealth, self.TGD1, self.TGD2, 
    #         self.TransmissionTime, self.AODC]
    # 0-20 used for calculation
    BRDC.append(EPH.af0)
    BRDC.append(EPH.af1)
    BRDC.append(EPH.af2)
    BRDC.append(EPH.iode)
    
    BRDC.append(EPH.crs)
    BRDC.append(EPH.dn)
    BRDC.append(EPH.m0)
    BRDC.append(EPH.cuc)
    
    BRDC.append(EPH.ecc)
    BRDC.append(EPH.cus)
    BRDC.append(EPH.root_a)
    BRDC.append(EPH.toe)           # Toe_SOW col11
    
    BRDC.append(EPH.cic)
    BRDC.append(EPH.omega_0)
    BRDC.append(EPH.cis)
    BRDC.append(EPH.i0)
    
    BRDC.append(EPH.crc)
    BRDC.append(EPH.omega)
    BRDC.append(EPH.omega_dot)
    BRDC.append(EPH.idot)
    
    BRDC.append(EPH.toc)  # dataSource? Not used in GALKepler
    #===
    BRDC.append(EPH.week)          #? # Toe_GPSWeek col21

    BRDC.append(EPH.sisa)
    
    BRDC.append(EPH.health)
    BRDC.append(EPH.bgd_a)
    BRDC.append(EPH.bgd_b)
    #BRDC.append(0)                 # No TransmissionTime in EPH
    #BRDC.append(EPH.iodc)
    #= transmission time of message,second of GAL Week
    BRDC.append(EPH.toc)
    
    refTime = dt2float(gpsTime([EPH.gpsweek,EPH.gpstoe,gpsTime().Rollover]).datetime)
    BRDC.append(refTime)           #? refTime
            
    return BRDC


def GLO_EPH2BRDC(EPH):
    # Input EPH class
    # Output eph 2D array needed by GNSS
    # IODEarr in GNSS/GLOXYZT.py
    # Ref:     # GNSS/GLOEphParam
    BRDC = []
    a = gpsTime([EPH.gpsweek,EPH.gpstoe,gpsTime().Rollover]).GPS2UTC().datetime
    # %Y%m%d%H%M%S
    BRDC.append(dt2float(a))     # toc utc
    BRDC.append(EPH.gnss_short)
    BRDC.append(EPH.sat_id)
    BRDC.append(EPH.tau)         #bias
    
    BRDC.append(EPH.gamma)
    #=== mftime (tk + nd *86400) in seconds of the UTC week    
    #mftime = EPH.tk + nd * 86400 # not used
    mftime = EPH.gpstoe  # SOW in gps Time, different from BRDC
    BRDC.append(mftime)  
    
    BRDC.append(EPH.xn)
    BRDC.append(EPH.dxn)
    
    BRDC.append(EPH.ddxn)
    BRDC.append(EPH.cn)  # healthy
    BRDC.append(EPH.yn)
    BRDC.append(EPH.dyn)           # Toe_SOW
    
    BRDC.append(EPH.ddyn)
    BRDC.append(EPH.freq)
    BRDC.append(EPH.zn)
    BRDC.append(EPH.dzn)
    
    BRDC.append(EPH.ddzn)
    BRDC.append(EPH.en)   # age          
    return BRDC

def GPS_BRDCxyz(Eph,CTsow):
    # CTsow: epoch in GPS format
    # cal xyz at one epoch given brdc
    brdc = GPS_EPH2BRDC(Eph)
    brdc2d = np.array(brdc).reshape(1,len(brdc))  #
    #print('brdc2d', len(brdc2d))
    #print('CTsow', CTsow[0])
    CTsow_new = gpsTime().adjweek(int(CTsow[0])).datetime
    #print('CTsow_new', CTsow_new)
    resu = GPSKepler(brdc2d,CTsow_new).res()
    #resu = GPSKepler(brdc2d,CTsow).res()
    brdcxyz = np.array(resu[0:3]).reshape(1,3)
    brdcxyzvel = np.array(resu[3:6]).reshape(1,3)
    return brdcxyz,brdcxyzvel


def BDS_BRDCxyz(Eph,CTsow):
    # CTsow: epoch in GPS format
    # cal xyz at one epoch given brdc
    brdc = BDS_EPH2BRDC(Eph)
    brdc2d = np.array(brdc).reshape(1,len(brdc))  #
    CTsow_new = gpsTime().adjweek(int(CTsow[0])).datetime
    resu = BDSKepler(brdc2d,CTsow_new).res()
    #resu = BDSKepler(brdc2d,CTsow).res()
    brdcxyz = np.array(resu[0:3]).reshape(1,3)
    brdcxyzvel = np.array(resu[3:6]).reshape(1,3)
    return brdcxyz,brdcxyzvel


def GAL_BRDCxyz(Eph,CTsow):
    # CTsow: epoch in GPS format
    # cal xyz at one epoch given brdc
    brdc = GAL_EPH2BRDC(Eph)
    brdc2d = np.array(brdc).reshape(1,len(brdc))  #
    CTsow_new = gpsTime().adjweek(int(CTsow[0])).datetime
    resu = GALKepler(brdc2d,CTsow_new).res()
    #resu = GALKepler(brdc2d,CTsow).res()
    brdcxyz = np.array(resu[0:3]).reshape(1,3)
    brdcxyzvel = np.array(resu[3:6]).reshape(1,3)
    return brdcxyz,brdcxyzvel


def GLO_BRDCxyz(Eph,CTsow):
    # CTsow: epoch in GPS format
    # cal xyz at one epoch given brdc
    brdc = GLO_EPH2BRDC(Eph)
    brdc2d = np.array(brdc).reshape(1,len(brdc))  #
    CTsow_new = gpsTime().adjweek(int(CTsow[0])).datetime
    resu = GLOXYZT(brdc2d,CTsow_new).res()
    #resu = GLOXYZT(brdc2d,CTsow).res()
    brdcxyz = np.array(resu[0,0:3]).reshape(1,3)
    brdcxyzvel = np.array(resu[0,3:6]).reshape(1,3)
    return brdcxyz,brdcxyzvel

# def ephgps_brdcxyz(Eph):
#     # Input: Eph (Usually update every two hour for GPS) for one sat
#     # Output: cal brdc for all epochs within 2 hours
#     # [epoch, sat,iode, res,resrac]
#     epo0 = Eph.toe
#     #iode = Eph.iode
#     brdc_epos = []
#     epoend = epo0 + 2*60*60
#     epos = np.arange(epo0,epoend,5)
       
#     for i in range(epos):
#         sow = epos[i]
#         brdc2d = EPH2BRDC(Eph)
#         res = GPSKepler(brdc2d,sow).res()
#         brdc_epos.append([sow,res])
#     return brdc_epos

# def ephgps_brdcxyz_nsat(EphUser):
#     # Input: EphUser for all sats
#     # Output: brdc_nsats for all sats and all epochs
#     brdc_nsats_nepos = []
#     nsat = GPS.MaxNoSV 
#     for i in range(nsat):
#         Eph = EphUser.gps[i]
#         brdc_epos = ephgps_brdcxyz(Eph)
#         iode = Eph.iode
#         satid = i+1
#         brdc_nsats_nepos.append([iode,satid,brdc_epos])
#     return brdc_nsats_nepos


# def SSR23D(ssr):
#     # Input SSR class
#     # Output 3D array needed by GNSSEph.py
#     corrt = ssr
#     corr  = corrt.reshape(1,1,3)
#     return corr


# def iodeBDS(aode):
#     iode = (aode/720 %240) 
#     return iode

# def GPSEph(tTagArr,sysArrBRDC):
#     # sysArrBRDC : eph params
#     # tTagArr: epoch gps second of week
#     # out: xyzT
#     res  = GNSS.GPSKepler(sysArrBRDC,tTagArr).res()
#     return res
               

# def GALEph(tTagArr,sysArrBRDC):
#     res  = GNSS.GALKepler(sysArrBRDC[:,:,3:],tTagArr).res()
#     return res


# def GLOEph(tTagArr,sysArrBRDC):
#     toc = tTagArr #CT time seconds of week
#     # ymdh 2 moscow /900 
#     #iode = GNSS.matchIODE.iodeGLO(toc) 
    
#     res  = GNSS.GLOKepler(sysArrBRDC[:,:,3:],tTagArr).res()
#     return res


# def BDSEph(tTagArr,sysArrBRDC):
#     # Out: [xk, yk, zk, xkv, ykv, zkv, clk, rate]
#     res  = GNSS.BDSKepler(sysArrBRDC[:,:,3:],tTagArr).res()
#     return res


# def dataEPH(cor, brdc, sys, AC):
#         if sys=='G':
#             eph = GPSEph(cor, brdc)
            
#         if sys=='R':
#             eph = GLOEph(cor, brdc)
            
#         if sys=='C':
#             eph = BDSEph(cor, brdc)
                
#         if sys=='E':
#             eph = GALEph(cor, brdc)
                
#         return eph
    
        
# def orb_rac2xyz(brdcxyz,brdcxyzVel,corrRAC): 
#     # Input corrRAC [3]
#     # Out: xyz[3]
#     brdcxyz = brdcxyz.reshape(1,1,3)
#     brdcxyzVel = brdcxyzVel.reshape(1,1,3)    
#     corrRAC = corrRAC.reshape(1,1,3)    
#     XYZT = Coord.coordTrans(brdcxyz, brdcxyzVel)
#     xyz = XYZT.rac2ecef(corrRAC)
#     corr_orb_xyz = xyz.reshape(3)
#     return corr_orb_xyz

# xyz to rac 
# def orb_xyz2rac(brdcxyz,brdcxyzVel,corrXYZ):
#     brdcxyz = brdcxyz.reshape(1,1,3)
#     brdcxyzVel = brdcxyzVel.reshape(1,1,3)    
#     corrXYZ = corrXYZ.reshape(1,1,3)      
#     XYZT = Coord.coordTrans(brdcxyz, brdcxyzVel)
#     RAC = XYZT.ecef2rac(corrXYZ)
#     RAC = RAC.reshape(3)
#     return RAC


#def orb_rac2xyz_2D(brdcxyz2D,brdcxyzVel2D,corrRAC): 
#    # Input corrRAC [svnum,3]
#    # Out: xyz[svnum,3]
#    svnum = GPS.MaxNoSV
#    brdcxyz = brdcxyz2D.reshape(1,svnum,3)
#    brdcxyzVel = brdcxyzVel2D.reshape(1,svnum,3)        
#    corrRAC = corrRAC.reshape(1,svnum,3)    
#    XYZT = Coord.coordTrans(brdcxyz, brdcxyzVel)
#    xyz = XYZT.rac2ecef(corrRAC)
#    corr_orb_xyz = xyz.reshape(svnum,3)
#    return corr_orb_xyz


#def orb_xyz2rac_2D(brdcxyz2D,brdcxyzVel2D,corrxyz): 
#    # Input corrRAC [svnum,3]
#    # Out: xyz[svnum,3]
#    svnum = GPS.MaxNoSV
#    brdcxyz = brdcxyz2D.reshape(1,svnum,3)
#    brdcxyzVel = brdcxyzVel2D.reshape(1,svnum,3)        
#    corrxyz = corrxyz.reshape(1,svnum,3)    
##    XYZT = Coord.coordTrans(brdcxyz, brdcxyzVel)
#    xyz = XYZT.ecef2rac(corrxyz)
#    corr_orb_xyz = xyz.reshape(svnum,3)
#    return corr_orb_xyz