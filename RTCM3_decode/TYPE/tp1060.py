# -*- coding: utf-8 -*-
"""
Created on Wed Mar 20 11:47:25 2024

@author: CHCUK-11
"""
from copy import deepcopy
from RTCM3_decode.SSR.ssrData import SSRSAT
from RTCM3_decode.Codec.getbitu import getbitu
from GNSS.sys_names import SysNames
from RTCM3_decode.TYPE.mes_head import decode_ssr1_head

def decode_ssr4(rtcm,sys,ssrin):
    """
    Message Type 1060: SSR GPS combined Orbit and Clock Correction
    # Table 3.5-44 in ref RTCM3
    """
    buff = rtcm.buff
    #ssr0 = SSRSAT()
    #msgtype = getbitu(buff,24,'u12')    
    heads = decode_ssr1_head(rtcm,sys)
    #print('sync',msgtype,rtcm.len,heads.sync,heads.nsat)
    if(heads.nsat < 0):
        return -1
    if(sysNames(sys).isGPS()):
        # prn; iode,iodcrc;prn
        np = 6;ni = 8;nj =0; offp = 0
        fnp ='u6';fni = 'u8';fnj = 0
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
        # np = 6;ni = 10;nj =24; offp = 1
        # fnp ='u6';fni = 'u10';fnj = 'u24'
        # np = 6;ni = 8;nj =0; offp = 0
        # fnp ='u6';fni = 'u8';fnj = 0
        np = 6;ni = 10;nj =8; offp = 0
        fnp ='u6';fni = 'u10';fnj = 'u8'
        ssrt  = ssrin.ssrbds
    elif(sysNames(sys).isQZS()):
        np = 4;ni = 8;nj =0; offp = 192
        fnp ='u6';fni = 'u8';fnj = 0
    
    ssr0 = ssrt.get_ssr(heads.gpsepo,sys)
    ssr0.gpsepo = heads.gpsepo
    i = heads.hsize
    for j in range(heads.nsat):
        
        prn = getbitu(buff,i,fnp)+offp; i+=np
        #if(sys == 'C'):
        #    print('prn',prn)
        assert prn >0
        k = prn -1
        #satt = deepcopy(ssr0.sats[k][0])
        satt4 = SSRSAT()  # new sat in ssr4
        satt4.prn = prn
        satt4.iode     = getbitu(buff,i,fni);     i+= ni
        satt4.iodcrc   = getbitu(buff,i,fnj);    i+= nj
        orb0   = getbitu(buff,i,'s22')*1E-4;  i+= 22
        orb1   = getbitu(buff,i,'s20')*4E-4;  i+= 20
        orb2   = getbitu(buff,i,'s20')*4E-4;  i+= 20
        orbv0  = getbitu(buff,i,'s21')*1E-6;  i+= 21
        orbv1  = getbitu(buff,i,'s19')*4E-6;  i+= 19
        orbv2  = getbitu(buff,i,'s19')*4E-6;  i+= 19
        satt4.orb.append([float("%.4f" % orb0),
                          float("%.4f" % orb1),
                          float("%.4f" % orb2)])
        satt4.orbv.append([float("%.4f" % orbv0),
                           float("%.4f" % orbv1),
                           float("%.4f" % orbv2)])
        
        # Delta Clock C0 [m]
        clk0   = getbitu(buff,i,'s22')*1E-4;  i+= 22
        satt4.clk[0]   = float("%.4f" % clk0)
        # Delta Clock C1 [m/s]
        clk1   = getbitu(buff,i,'s21')*1E-6;  i+= 21
        satt4.clk[1]   = float("%.4f" % clk1)
        # Delta Clock C2 [m/s^2]
        clk2   = getbitu(buff,i,'s27')*2E-8;  i+= 27
        satt4.clk[2]   = float("%.4f" % clk2)
        satt4.gpsepo[0]  = heads.gpsepo
        satt4.gpsepo[1]  = heads.gpsepo
        satt4.epoch[0] = heads.epoch; satt4.epoch[1]=heads.epoch
        satt4.udi[0] = heads.udi;satt4.udi[1] = heads.udi
        satt4.iod[0] = heads.iod;satt4.iod[1] = heads.iod
        satt4.update = 1
        satt4.gnss = sysNames(sys).Sys
        satt4.provid = heads.provid
        satt4.refd = heads.refd
        satt4.solid = heads.solid
        satt4.sync[0] = heads.sync; satt4.sync[1] = heads.sync
        ssr0.sats[k] = deepcopy(satt4)
    if(heads.sync):
        flag = 10
    else:
        flag = 0
    return flag