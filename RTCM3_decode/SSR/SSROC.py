# -*- coding: utf-8 -*-
"""
Created on Wed Nov 10 14:33:27 2021
# orbCorr,clkCorr based on BNC
\BNC_2.12.17\src\RTCM3\RTCM3coDecoder.cpp
# 2022 Jan 13: add BDS
# 2021 Dec 31: clkorbs add aclist
               clkorbs.remove_epo based on resTime
@author: Zoe Chen
"""
import numpy as np
#from GNSS import GPS
#from GNSS import GLO,BDS,GAL
#import gc
# from common.common import SYS_GPS
# from common.common import SYS_GLO,SYS_GAL,SYS_BDS
from SSR.ssrData import MSG,Types,orb_type,clk_type

#Maxepo = 6 # 30s
    
class ClkOrbs:  
    def __init__(self):
        # all sats for ac i for one epoch
        # self.clkorbs[i] =[sat1,sat2...]
        self.clkorbs = []  # all sats from all ACs
        self.gpsepo = None
        self.acs    = []  # holding acs for each epochs
        
    def add_acsat(self,epoch,sat0,AC):
        # add infor for the same sat for each AC
        if sat0 is not None:
            if(sat0.acname is None):
                sat0.acname = AC
                sat0.epoch = sat0.epoch[1]
                sat0.gpsepo = sat0.gpsepo[1]
        if (self.gpsepo is None):
            self.gpsepo = epoch
        if(AC not in self.acs):
            if(len(self.acs) == 0):
                self.acs= [AC]
                self.clkorbs = [None]
            else:
                self.acs.append(AC)
                self.clkorbs.append(None)
        #else:
        #    self.acs.append(AC)
        #    self.clkorbs.append[None]
            
        jac = np.where(np.array(self.acs) == AC)[0][0]
        if(self.clkorbs[jac] is None):
            self.clkorbs[jac]= [sat0]
        else:
            self.clkorbs[jac].append(sat0)
        return                                
    
    def __repr__(self):
        return ('clkorbs class with objects: epochs[epo],' +
                'clkorbs[epo]')
        

def oc2corr(sys,ssrlist,resTime):
    # cycle all sats OC in ssrlist 
    # Out: clkorbs, orb AC/prn at resTime [restime,clkorb]
    #      new clkorb in ssrlist added
    #      = outdated clkorb deleted (not necessary)
    # ssrlist: AC1: ALL epos, all sats
    # clkorbs: resTime: all sats, all AC for each sat
    clkorbs  = ClkOrbs()
    if(ssrlist):
        keylist = list(ssrlist)
        nlen = len(keylist)
        for i in range(nlen):
            AC = keylist[i]
            ssrtmp= ssrlist[AC]
            #resTime = ssrtmp.gpsepos[0]
            try:
                jt = np.where(np.array(ssrtmp.gpsepos)== resTime)[0]
                #jt = [-1] # for realtime debug
                if(len(jt)>0):
                    j = jt[0]
                    epoch = ssrtmp.gpsepos[j]
                    ssrtmp2 = ssrtmp.ssrs[j]
                    if ssrtmp2 is not None:
                        for k in range(len(ssrtmp2.sats)):
                            sat0 = ssrtmp2.sats[k]
                            clkorbs.add_acsat(epoch,sat0,AC)
                else:
                    #print('Warning no resTime in oc2corr',AC,resTime)
                    #print('Avail Epo in ssrnew',ssrtmp.gpsepos)
                    pass
                    
            except:
                print('warning: ssrlist to corr')
    return clkorbs        
           

def corr2orbit(rescorr,sys):
    #= orb(one type), includes multiple sats
    msg_type = orb_type(sys)  
        
    msg0 = MSG()
    msg0.type = msg_type
    nsat = len(rescorr.sats)
    nusat = 0
    for j in range(nsat):
        if(rescorr.sats[j] is not None):
            nusat += 1
            if(msg0.epoch is None):
                msg0.epoch = rescorr.sats[j].epoch
            if(msg0.udi is None):
                msg0.udi = rescorr.sats[j].udi[1]
            if(msg0.sync is None):        
                msg0.sync = rescorr.sats[j].sync[1]
            if(msg0.iod is None):
                msg0.iod = rescorr.sats[j].iod[1]
            if(msg0.refd is None):
                msg0.refd = rescorr.sats[j].refd
            if(msg0.solid is None):
                msg0.solid = rescorr.sats[j].solid
            if(msg0.provid is None):
                msg0.provid = rescorr.sats[j].provid
            
            msg0.prn.append(rescorr.sats[j].prn)
            msg0.dr.append(rescorr.sats[j].orb[0])
            msg0.dt.append(rescorr.sats[j].orb[1])
            msg0.dn.append(rescorr.sats[j].orb[2])
            msg0.dot_dr.append(rescorr.sats[j].orbv[0])
            msg0.dot_dt.append(rescorr.sats[j].orbv[1])
            msg0.dot_dn.append(rescorr.sats[j].orbv[2])
            msg0.iode.append(rescorr.sats[j].iode)
            msg0.iodcrc.append(rescorr.sats[j].iodcrc)
    msg0.nsat = nusat
    return msg0


def corr2clock(rescorr,sys):
    msg_type = clk_type(sys)
    
    msg0 = MSG()
    msg0.type = msg_type
    nsat = len(rescorr.sats)
    nusat = 0
    for j in range(nsat):
        if(rescorr.sats[j] is not None):
            nusat += 1
            if(msg0.epoch is None):
                msg0.epoch = rescorr.sats[j].epoch
            if(msg0.udi is None):
                msg0.udi = rescorr.sats[j].udi[1]
            if(msg0.sync is None):        
                msg0.sync = rescorr.sats[j].sync[1]
            if(msg0.iod is None):
                msg0.iod = rescorr.sats[j].iod[1]
            if(msg0.refd is None):
                msg0.refd = rescorr.sats[j].refd
            if(msg0.solid is None):
                msg0.solid = rescorr.sats[j].solid
            if(msg0.provid is None):
                msg0.provid = rescorr.sats[j].provid
            
            msg0.prn.append(rescorr.sats[j].prn)
            msg0.dc0.append(rescorr.sats[j].dclk)
            msg0.dc1.append(0)
            msg0.dc2.append(0)
            # msg0.dc0.append(rescorr.sats[j].clk[0])
            # msg0.dc1.append(rescorr.sats[j].clk[1])
            # msg0.dc2.append(rescorr.sats[j].clk[2])
    msg0.nsat = nusat
    return msg0

def corr2ssr(rescorr,sys):
    ssr = Types()
    msg_orb = corr2orbit(rescorr,sys)
    msg_clk = corr2clock(rescorr,sys)
    ssr.add_msg(msg_orb)
    ssr.add_msg(msg_clk)
    return ssr
    