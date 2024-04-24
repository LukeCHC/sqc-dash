# -*- coding: utf-8 -*-
"""
Created on Wed Mar 20 11:38:51 2024

@author: 
"""
from copy import deepcopy
from RTCM3_decode.SSR.ssrData import SSRSAT
from RTCM3_decode.Codec.getbitu import getbitu
from GNSS.sys_names import SysNames
from RTCM3_decode.TYPE.mes_head import decode_ssr2_head

def decode_ssr2(rtcm,sys,ssrin):
    "SSR GPS Clock Correction"
    buff = rtcm.buff
    #msgtype = getbitu(buff,24,'u12')
    heads = decode_ssr2_head(rtcm,sys)
    #print('sync',msgtype,rtcm.len,heads.sync,heads.nsat)
    #print('nsat',heads.nsat)
    if(heads.nsat < 0):
        return -1
    
    if(sysNames(sys).isGPS()):
        # prn; iode,iodcrc;prn
        np = 6; offp = 0
        fnp ='u6'
        ssrt = ssrin.ssrgps
    elif(sysNames(sys).isGLO()):
        np = 5; offp = 0
        fnp ='u5'
        ssrt = ssrin.ssrglo
    elif(sysNames(sys).isGAL()):
        np = 6; offp = 0
        fnp ='u6'
        ssrt = ssrin.ssrgal
    elif(sysNames(sys).isBDS()):
        np = 6; offp = 1
        fnp ='u6'
        ssrt = ssrin.ssrbds
    elif(sysNames(sys).isQZS()):
        np = 4; offp = 192
        fnp ='u4'
        ssrt = ssrin.qzssats
    ssr0 = ssrt.get_ssr(heads.gpsepo,sys)
    if ssr0.gpsepo is None:
        ssr0.gpsepo = heads.gpsepo
    i = heads.hsize
    for j in range(heads.nsat):
        prn = getbitu(buff,i,fnp)+offp; i+=np
        #print(prn)
        assert prn>0
        k = prn -1
        #print('nsats',len(ssr0.sats),prn,k,i)
        satt2 = deepcopy(ssr0.sats[k]) # share satt with ssr1
        if(satt2 is None):
            satt2 = SSRSAT()
        if(satt2.prn is None):
            satt2.prn = deepcopy(prn)
        else:
            assert satt2.prn == prn
        satt2.epoch[1] = heads.epoch
        satt2.gpsepo[1] = heads.gpsepo
        satt2.udi[1] = heads.udi
        satt2.iod[1] = heads.iod
        # Delta Clock C0 [m]
        clk0 = getbitu(buff,i,'s22')*1E-4;  i+= 22
        satt2.clk[0] = float("%.4f" % clk0)
        # Delta Clock C1 [m/s]
        clk1 = getbitu(buff,i,'s21')*1E-6;  i+= 21
        satt2.clk[1] = float("%.4f" % clk1)
        # Delta Clock C2 [m/s^2]
        clk2 = getbitu(buff,i,'s27')*2E-8;  i+= 27
        satt2.clk[2] = float("%.4f" % clk2)
        satt2.update = 1
        satt2.provid = heads.provid 
        #satt2.refd = heads.refd # no refd in clock
        satt2.solid = heads.solid
        satt2.sync[1] = heads.sync
        satt2.gnss = sysNames(sys).Sys
        ssr0.sats[k] = deepcopy(satt2)
        
    if(heads.sync):
        flag = 10
    else:
        flag = 0
    return flag