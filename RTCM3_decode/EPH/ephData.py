# -*- coding: utf-8 -*-
"""
Created on Wed Feb 16 14:12:41 2022

@author: Zoe Chen
"""
import sys
sys.dont_write_bytecode = True
#import threading
import gc
#import time
#import logging
from time_transform.time_format import GpsTime
from GNSS import GPS, BDS, GLO, GAL
#from TOOLS.id2num import id2num


Maxiod = 3

class SharedEPH(object):
    def __init__(self):
        self.EPH = []
        #self.lock = threading.Lock()
    
    def updateEPH(self,EPH):
        #self.lock.acquire()
        self.EPH = EPH
        #self.lock.release()

    def getEPH(self):
        #self.lock.acquire()
        EPH = self.EPH
        #self.lock.release()
        return EPH     
    
    #def updatebrdc_gps(self,brdcgps):
    #    self.lock.acquire()
    #    self.brdcgps = brdcgps
    #    self.lock.release()

    #def getbrdc_gps(self):
    #    self.lock.acquire()
    #    brdcgps = self.brdcgps
    #    self.lock.release()
    #    return brdcgps  
      
class GPSEPH:
    def __init__(self):
        self.sat_id    = None
        self.week      = None
        self.ura       = None
        self.code_L2   = None
        self.idot      = None
        
        self.iode      = None
        self.toc       = None
        self.af2       = None
        self.af1       = None
        self.af0       = None
        
        self.iodc      = None
        self.crs       = None
        self.dn        = None
        self.m0        = None
        self.cuc       = None
        
        self.ecc       = None
        self.cus       = None
        self.root_a    = None
        self.toe       = None # Reference Time Ephemeris # Second of week
        self.cic       = None
        
        self.omega_0   = None
        self.cis       = None
        self.i0        = None
        self.crc       = None
        self.omega     = None
        
        self.omega_dot = None
        self.tgd       = None
        self.health    = None
        self.L2P       = None
        self.interval  = None
        
        # additional info
        self.gnss       = None
        self.gnss_short = None
        self.fullweek   = None
        self.gpsweek    = None
        self.gpstoe     = None
        
class BDSEPH:
    def __init__(self):
        self.gnss      = None
        self.gnss_short = None
        self.prn       = None
        self.sat_id    = None
        self.week      = None # original bds week
        self.sva       = None
        self.idot      = None
        self.aode      = None   
        self.toc       = None
        self.af2       = None
        self.af1       = None
        self.af0       = None
        self.iodc      = None
        self.crs       = None
        self.dn      = None
        self.m0        = None
        self.cuc       = None
        self.ecc       = None
        self.cus       = None
        self.root_a    = None
        self.toe       = None
        self.cic       = None
        self.omega_0   = None
        self.cis       = None
        self.i0        = None
        self.crc       = None
        self.omega     = None
        self.omega_dot = None
        self.tgd1      = None
        self.tgd2      = None
        self.health    = None
        self.iode      = None # to be calculated based on aode
        self.gpstoe    = None # transfer toe(bdstime) to gps.toe
        self.gpsweek   = None # transfer bds week to gpsweek
        
        
        
class GALFEPH:
    # 1045 FNAV
    def __init__(self):
        self.sat_id = None
        self.root_a    = None
        self.dn        = None
        self.ecc       = None
        self.i0        = None
        self.idot      = None
        self.omega_0   = None
        self.omega_dot = None
        self.omega     = None
        self.m0        = None
        self.crc       = None
        self.crs       = None
        self.cuc       = None
        self.cus       = None
        self.cic       = None
        self.cis       = None
        self.af0       = None
        self.af1       = None
        self.af2       = None
        self.toe       = None
        self.toc       = None
        self.week      = None
        
        #self.iod       = dec_msg.iod   # GAL added by Zoe
        self.health    = None
        self.bgd_a      = None
        self.bgd_b      = None
        self.iode      = None   # 


class GALIEPH:
    # 1046 INAV
    def __init__(self):
        self.gnss      = None
        self.gnss_short = None
        self.sat_id    = None
        self.week      = None
        self.iode       = None
        self.sisa      = None
        self.idot      = None
        self.toc       = None
        self.af0       = None
        self.af1       = None
        self.af2       = None
        self.crs       = None
        self.dn        = None
        self.m0        = None
        self.cuc       = None
        self.ecc       = None
        self.cus       = None
        self.root_a    = None
        self.toe       = None
        self.cic       = None
        self.omega_0   = None
        self.cis       = None
        self.i0        = None
        self.crc       = None
        self.omega     = None
        self.omega_dot = None
        self.bgd_a     = None
        self.bgd_b     = None
        self.health    = None
        self.e1b_v     = None
        #self.iod       = dec_msg.iod   # GAL added by Zoe
        self.gpstoe    = None
        self.gpsweek   = None
        
class GLOEPH:
    # 1020 sequence based on decoding
    def __init__(self):
        self.gnss       = None
        self.gnss_short = None
        
        self.sat_id     = None
        self.freq       = None
        self.bn         = None
        self.cn         = None
        self.p1         = None
        self.tk         = None
        self.msb_bn     = None
        self.p2         = None
        self.tb         = None
        self.dxn        = None
        
        self.xn         = None
        self.ddxn       = None
        self.dyn        = None
        self.yn         = None
        self.ddyn       = None
        self.dzn        = None
        self.zn         = None
        self.ddzn       = None
        self.p3         = None
        self.p          = None
        self.ln_t       = None
        self.tau        = None
        self.dtau       = None
        self.en         = None
        self.p4         = None
        self.ft         = None
        self.nt         = None
        self.m          = None
        self.ava        = None
        self.na         = None
        self.tau_c      = None
        self.n4         = None
        self.tau_gps    = None
        self.ln_f       = None
        self.gamma      = None
        self.ch         = None
        self.health     = None
        self.toe        = None
        self.gpstoe     = None
        self.gpsweek    = None
        self.iode       = None # to be calculated        
    
class ephnsat:
    # for one epoch
    def __init__(self):
        # total MaxNoSV
        #if(sys=='G'):
        self.ephgps = [None] * GPS.MaxNoSV
        #elif (sys == 'C'):
        self.ephbds = [None] * BDS.MaxNoSV
        #elif(sys == 'E'):
        #self.ephgalF = [None] * GAL.MaxNoSV
        self.ephgalI = [None] * GAL.MaxNoSV
        #elif(sys == 'R'):
        self.ephglo = [None] * GLO.MaxNoSV
        return

class ephlist:
    def __init__(self):
        self.gpseph = []
        self.bdseph = []
        self.galeph = []
        self.gloeph = []
            
            
class ephUser:
    def __init__(self):
        # total MaxNoSV
        # 2 iod for each sat
        #= true need add new sat
        #  false iode is the latest
        
        #if(sys=='G'):
        self.ephgps = [None] * GPS.MaxNoSV
        # sat,iode for quich search
        self.ephgpslist = [None] * GPS.MaxNoSV
        self.epogpslist = [None] * GPS.MaxNoSV
        self.ephgpsflag = False # true need add new sat
        # brdc for each sat
        #elif (sys == 'C'):
        self.ephbds = [None] * BDS.MaxNoSV
        self.ephbdslist = [None] * BDS.MaxNoSV
        self.epobdslist = [None] * BDS.MaxNoSV
        self.ephbdsflag = False # true need add new sat
   
        #elif(sys == 'E'):
        self.ephgal = [None] * GAL.MaxNoSV
        self.ephgallist = [None] * GAL.MaxNoSV
        self.epogallist = [None] * GAL.MaxNoSV
        self.ephgalflag = False # true need add new sat
            
        #elif(sys == 'R'):
        self.ephglo = [None] * GLO.MaxNoSV
        self.ephglolist = [None] * GLO.MaxNoSV
        self.epoglolist = [None] * GLO.MaxNoSV
        self.ephgloflag = False # true need add new sat
        
    def add_eph_gps(self,ephin):
        New = False
        # [iode1,iode2,iode3] for each sat
        # ts = time.perf_counter()
        nsat = len(ephin.ephgps)
        for i in range(nsat):
            try:
                if(ephin.ephgps[i].health == 0):
                    if(self.ephgpslist[i] is None):                
                        self.ephgps[i] = [ephin.ephgps[i]]
                        self.ephgpslist[i]= [ephin.ephgps[i].iode]
                        self.epogpslist[i] = [ephin.ephgps[i].toe]
                        New = True
                    else:
                        list0 = list(self.ephgpslist[i])
                        if(ephin.ephgps[i].iode not in list0):
                            self.ephgps[i].append(ephin.ephgps[i])
                            self.ephgpslist[i].append(ephin.ephgps[i].iode)
                            self.epogpslist[i].append(ephin.ephgps[i].toe)
                            New = True
                            prnlist = self.ephgpslist[i]
                            # for one prn, save * epochs/iode
                            if (len(prnlist) > Maxiod):
                                del self.ephgps[i][0]
                                del self.ephgpslist[i][0]
                                del self.epogpslist[i][0]
                                gc.collect()
            except:
                pass
        # te = time.perf_counter()
        # difft = te -ts
        # logging.info('add_eph_gps seconds= {}'.format(difft))
        return New
    
    
    def update_ephgps_flag(self):
        #= true need add new sat
        #       eph is empyt
        #       eph len <= 2
        #       eph newepo > ct + 3600
        #  false iode is the latest
        if(not any(self.ephgps)):
            self.ephgpsflag = True
            return
        else:
            self.ephgpsflag = False
        
        try:
            ct = gpsTime()
            hour = ct.datetime.hour
            mod = hour%2  # update gps at even hours
            #mod = ct.datetime.minute % 10
            #maxepo = ct.GPSSOW
            #if ((mod == 0) & (ct.datetime.minute <5)):
            #=== Update 2022Jul28
            #= 68 06:00:10
            #= IODE updated at 00:10, so update eph before/after five mins
            if (((mod == 0) & (ct.datetime.minute <2))
                or ((mod == 1) & (ct.datetime.minute > 58))):
            #if (ct.datetime.minute %5) == 0: #every 5 minutes
                self.ephgpsflag = True
                return
            else:
                self.ephgpsflag = False
            #self.ephgpsflag = True
        except:
            pass
        return
    
    def add_eph_bds(self,ephin):
        New = False
        # [iode1,iode2,iode3]
        # [sat1,sat2,sat3] for each sat
        nsat = len(ephin.ephbds)
        for i in range(nsat):
            if(ephin.ephbds[i] is not None):
                try:
                    if(ephin.ephbds[i].health == 0):
                        # index = id2num(ephin.ephGPS.sat_id) - 1 
                        if(self.ephbdslist[i] is None):                
                            self.ephbds[i] = [ephin.ephbds[i]]
                            self.ephbdslist[i]= [ephin.ephbds[i].iode]
                            self.epobdslist[i] = [ephin.ephbds[i].gpstoe]
                            New = True
                        else:
                            list0 = list(self.ephbdslist[i])
                            if(ephin.ephbds[i].iode not in list0):
                                self.ephbds[i].append(ephin.ephbds[i])
                                self.ephbdslist[i].append(ephin.ephbds[i].iode)
                                self.epobdslist[i].append(ephin.ephbds[i].gpstoe)
                                New = True
                                prnlist = self.ephbdslist[i]
                                # for one prn, save * epochs/iode
                                if (len(prnlist) > Maxiod):
                                    del self.ephbds[i][0]
                                    del self.ephbdslist[i][0]
                                    gc.collect()
                    else:
                        pass
                        # print('eph Unhealth',ephin.eph[i].sat_id,
                        #                      ephin.eph[i].health,
                        #                      ephin.eph[i].toe)
                except:
                    pass
        return New
    
    
    def update_ephbds_flag(self):
        #= true need add new sat
        #       eph is empyt
        #       eph len <= 2
        #       eph newepo > ct + 3600
        #  false iode is the latest
        if(not any(self.ephbds)):
            self.ephbdsflag = True
            return
        else:
            self.ephbdsflag = False
        
        try:
            ct = gpsTime()
            hour = ct.datetime.hour
            mod = hour%1  # update bds every one hour
            #maxepo = ct.GPSSOW
            if ((mod == 0) & (ct.datetime.minute <5)):
                self.ephbdsflag = True
                return
            else:
                self.ephbdsflag = False
        except:
            pass
        return
        
    def add_eph_gal(self,ephin):
        New = False
        # [iode1,iode2,iode3]
        # [sat1,sat2,sat3] for each sat
        # ADD GALI in ephuser
        nsat = len(ephin.ephgalI)
        for i in range(nsat):
            if(ephin.ephgalI[i] is not None):
                try:
                    if(ephin.ephgalI[i].health == 0):
                        # index = id2num(ephin.ephGPS.sat_id) - 1 
                        if(self.ephgallist[i] is None):                
                            self.ephgal[i] = [ephin.ephgalI[i]]
                            self.ephgallist[i]= [ephin.ephgalI[i].iode]
                            self.epogallist[i] = [ephin.ephgalI[i].gpstoe]
                            New = True
                        else:
                            list0 = list(self.ephgallist[i])
                            if(ephin.ephgalI[i].iode not in list0):
                                self.ephgal[i].append(ephin.ephgalI[i])
                                self.ephgallist[i].append(ephin.ephgalI[i].iode)
                                self.epogallist[i].append(ephin.ephgalI[i].gpstoe)
                                New = True
                                prnlist = self.ephgallist[i]
                                # for one prn, save * epochs/iode
                                if (len(prnlist) > Maxiod):
                                    del self.ephgal[i][0]
                                    del self.ephgallist[i][0]
                                    gc.collect()
                    else:
                        pass
                except:
                    pass
        return New
    
    def update_ephgal_flag(self):
        #= true: need add new sat
         #       eph is empyt
        #        eph update time
        if(not any(self.ephgal)):
            self.ephgalflag = True
            return
        else:
            self.ephgalflag = False
            
        try:
            ct = gpsTime()
            minute = ct.datetime.minute
            mod = minute%10  # update GAL every 10min
            if ((mod >= 0) & (mod <= 5)):
                self.ephgalflag = True
                return
            else:
                self.ephgalflag = False
        except:
            pass
        
        return
    
    def add_eph_glo(self,ephin):
        New = False
        # [iode1,iode2,iode3]
        # [sat1,sat2,sat3] for each sat
        nsat = len(ephin.ephglo)
        for i in range(nsat):
            if(ephin.ephglo[i] is not None):
                try:
                    if(ephin.ephglo[i].health == 0):
                        if(self.ephglolist[i] is None):                
                            self.ephglo[i] = [ephin.ephglo[i]]
                            self.ephglolist[i]= [ephin.ephglo[i].iode]
                            self.epoglolist[i] = [ephin.ephglo[i].gpstoe]
                            New = True
                        else:
                            list0 = list(self.ephglolist[i])
                            if(ephin.ephglo[i].iode not in list0):
                                self.ephglo[i].append(ephin.ephglo[i])
                                self.ephglolist[i].append(ephin.ephglo[i].iode)
                                self.epoglolist[i].append(ephin.ephglo[i].gpstoe)
                                New = True
                                prnlist = self.ephglolist[i]
                                # for one prn, save * epochs/iode
                                if (len(prnlist) > Maxiod):
                                    del self.ephglo[i][0]
                                    del self.ephglolist[i][0]
                                    gc.collect()
                    else:
                        pass
                        # print('eph Unhealth',ephin.eph[i].sat_id,
                        #                      ephin.eph[i].health,
                        #                      ephin.eph[i].toe)
                except:
                    pass
        return New
    
    def update_ephglo_flag(self):
        #= true need add new sat
        #       eph is empyt
        #       eph update time
        #  false: iode is the latest
        if(not any(self.ephglo)):
            self.ephgloflag = True
            return
        else:
            self.ephgloflag = False
        
        try:
            ct = gpsTime()
            minute = ct.datetime.minute
            #mod = minute%15  # update GLO every 30min(15/45)
            #maxepo = ct.GPSSOW
            if (((minute >= 15) & (minute <=20)) or 
                ((minute >= 45)& minute<= 50)):
                self.ephgloflag = True
                return
            else:
                self.ephgloflag = False
        except:
            pass
        
        return
    
# class gps_brdc():
#     def __init__(self):    
#         self.brdc   = [] 
#         self.brdclist = []
        
#     def add_brdc(self,epoch0,epoch,brdcgps):
#         self.brdc.append([epoch,brdcgps])
#         self.brdclist.append(epoch)
        
#         # del old brdc
#         for i in range(len(self.brdclist)):
#             if(self.brdclist[i] < epoch0):
#                 del self.brdclist[i]
#                 del self.brdc[i]
#                 gc.collect()
        
#         return
        
        