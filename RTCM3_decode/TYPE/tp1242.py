# -*- coding: utf-8 -*-
"""
Created on Wed Mar 20 14:13:33 2024

@author: 
"""
from copy import deepcopy
from RTCM3_decode.Codec.getbitu import getbitu
from GNSS.sys_names import SysNames
from RTCM3_decode.TYPE.mes_head import decode_ssr2_head

def decode_ssr3(rtcm,sys,ssrin):
    "SSR Galileo Code Bias"
    buff = rtcm.buff
    heads = decode_ssr2_head(rtcm,sys)
    flag = 0
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
    ssr0 = ssrt.get_ssr0(heads.gpsepo,sys)
    i = heads.hsize
    for j in range(heads.nsat):
        prn = getbitu(buff,i,fnp)+offp; i+=np
        #print(prn)
        assert prn>0
        k = prn -1
        #print('nsats',len(ssr0.sats),prn,k,i)
        ssrt = deepcopy(ssr0.sats[k])
        if(ssrt.prn is None):
            ssrt.prn = prn
        else:
            assert ssrt.prn == prn
        ssrt.gpsepo[2] = heads.gpsepo
        ssrt.udi[2] = heads.udi
        ssrt.iod[2] = heads.iod
        # Delta Clock C0 [m]
        ssrt.clk[0] = getbitu(buff,i,'s22')*1E-4;  i+= 22
        # Delta Clock C1 [m/s]
        ssrt.clk[1] = getbitu(buff,i,'s21')*1E-6;  i+= 21
        # Delta Clock C2 [m/s^2]
        ssrt.clk[2] = getbitu(buff,i,'s27')*2E-8;  i+= 27
        ssrt.update = 1
        ssr0.sats[k] = deepcopy(ssrt)
    if(heads.sync):
        flag = 10
    else:
        flag = 0
    return flag
