# -*- coding: utf-8 -*-
"""
Created on Wed Mar 20 11:55:51 2024

@author: 
"""

from copy import deepcopy
from RTCM3_decode.SSR.ssrData import SSRSAT
from RTCM3_decode.Codec.getbitu import getbitu
from GNSS.sys_names import SysNames
from RTCM3_decode.TYPE.mes_head import decode_ssr1_head

def decode_ssr1(rtcm,sys,ssrin):
    "SSR Galileo Orbit Correction"
    buff = rtcm.buff
    #msgtype = getbitu(buff,24,'u12')
    heads = decode_ssr1_head(rtcm,sys)
    #print('sync',msgtype,rtcm.len,heads.sync,heads.nsat,heads.udi)
    if(heads.nsat < 0):
        return -1
    if(sysNames(sys).isGPS()):
        # prn; iode,iodcrc;prn
        np = 6;ni = 8;nj =0; offp = 0
        fnp ='u6';fni = 'u8';fnj = 0
        # Note: ssrt is shared in ssr1,ssr2,ssr3,ssr4
        #       can not be initialized here
        ssrt  = ssrin.ssrgps 
    elif(sysNames(sys).isGLO()):
        np = 5;ni = 8;nj =0; offp = 0
        fnp ='u5';fni = 'u8';fnj = 0
        ssrt  = ssrin.ssrglo
    elif(sysNames(sys).isGAL()):
        np = 6;ni = 10;nj =0; offp = 0
        fnp ='u6';fni = 'u10';fnj = 0
        ssrt  = ssrin.ssrgal
    elif(sysNames(sys).isBDS()):
        # np = 6;ni = 10;nj =24; offp = 1 # RTKLIB
        # fnp ='u6';fni = 'u10';fnj = 'u24'
        # np = 6;ni = 8;nj =0; offp = 0
        # fnp ='u6';fni = 'u8';fnj = 0
        np = 6;ni = 10;nj =8; offp = 0 #v08
        fnp ='u6';fni = 'u10';fnj = 'u8'
        ssrt  = ssrin.ssrbds
    elif(sysNames(sys).isQZS()):
        np = 4;ni = 8;nj =0; offp = 192
        fnp ='u6';fni = 'u8';fnj = 0
    
    ssr0 = ssrt.get_ssr(heads.gpsepo,sys)
    i = heads.hsize
    ssr0.gpsepo = heads.gpsepo
    for j in range(heads.nsat):
        
        prn = getbitu(buff,i,fnp)+offp; i+=np
        #if(sys == 'C'):
        #    print('prn',prn)
        assert prn >0
        k = prn -1
        # orb is shared for the same sys/epoch (Ex: SH) 
        satt1 = deepcopy(ssr0.sats[k])
        if(satt1 is None):
            satt1 = SSRSAT()
        satt1.prn      = prn
        satt1.iode     = getbitu(buff,i,fni);         i+= ni
        satt1.iodcrc   = getbitu(buff,i,fnj);         i+= nj
        # ssrt.orb[0]   = getbitu(buff,i,'s22')*1E-4;  i+= 22
        # ssrt.orb[1]   = getbitu(buff,i,'s20')*4E-4;  i+= 20
        # ssrt.orb[2]   = getbitu(buff,i,'s20')*4E-4;  i+= 20
        # ssrt.orbv[0]  = getbitu(buff,i,'s21')*1E-6;  i+= 21
        # ssrt.orbv[1]  = getbitu(buff,i,'s19')*4E-6;  i+= 19
        # ssrt.orbv[2]  = getbitu(buff,i,'s19')*4E-6;  i+= 19
        
        # Note: for SH, there are multiple orb for the same epoch
        orb0   = getbitu(buff,i,'s22')*1E-4;  i+= 22
        orb1   = getbitu(buff,i,'s20')*4E-4;  i+= 20
        orb2   = getbitu(buff,i,'s20')*4E-4;  i+= 20
        #print(getbitu(buff,i,'s21'))
        orbv0  = getbitu(buff,i,'s21')*1E-6;  i+= 21
        orbv1  = getbitu(buff,i,'s19')*4E-6;  i+= 19
        orbv2  = getbitu(buff,i,'s19')*4E-6;  i+= 19
        satt1.orb.append([float("%.4f" % orb0),float("%.4f" % orb1),
                          float("%.4f" % orb2)])
        satt1.orbv.append([float("%.4f" % orbv0),float("%.4f" % orbv1),
                           float("%.4f" % orbv2)])
        
        satt1.epoch[0] = heads.epoch
        satt1.gpsepo[0]  = heads.gpsepo
        satt1.udi[0] = heads.udi
        satt1.iod[0] = heads.iod
        satt1.update = 1
        satt1.gnss = sysNames(sys).Sys
        satt1.provid = heads.provid
        satt1.refd = heads.refd
        satt1.solid = heads.solid
        satt1.sync[0] = heads.sync
        ssr0.sats[k] = deepcopy(satt1)
        # ssrt,ssrin is automaticly updated after ssr0 updated
        
    if(heads.sync):
        flag = 10
    else:
        flag = 0
    return flag