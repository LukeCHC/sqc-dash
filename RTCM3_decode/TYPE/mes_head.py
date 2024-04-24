# -*- coding: utf-8 -*-
"""
Created on Thu Mar 21 11:41:51 2024

@author: CHCUK-11
"""

from RTCM3_decode.SSR.ssrData import HEADS
from RTCM3_decode.Codec.getbitu import getbitu
from GNSS.sys_names import SysNames
from RTCM3_decode.common import SYS_GPS,SYS_GLO,SYS_GAL,SYS_BDS,SYS_QZS
from time_transform.time_format import GpsTime,GloTime,BdsTime,GalTime

def decode_ssr_epoch(rtcm,sys):
    #= RTKLIB_2.4.3\src\rtcm3.c\decode_ssr_epoch 
    message = rtcm.buff
    i = 24 + 12
    if (sysNames(sys).Sys == SYS_GLO):
        tod = getbitu(message,i,'u17')
        i += 17
        epo = tod
        time = gloTime().adjday(tod)
        gpsepo = time.GPSSOW
        #header = 'u12u17'
    elif (sysNames(sys).Sys == SYS_BDS):
        sow = getbitu(message,i,'u20')
        i += 20
        epo = sow
        time = bdsTime().adjweek(sow)
        gpsepo = time.GPSSOW
    else:
        sow = getbitu(message,i,'u20')
        i += 20
        epo = sow
        time = gpsTime().adjweek(sow)
        gpsepo = time.GPSSOW
    #ssr.update_epo(gpsepo)
        #header = 'u12u20'
    #unpack_bits = bitstruct.unpack(header, message)
    # unpack_bits[0] is the type
    #msgtype = unpack_bits[0]
    # GPS Epoch Time 1s
    return i,epo,gpsepo 

def decode_ssr1_head(rtcm,sys):
    heads = HEADS()
    i = 24 + 12 
    if(sysNames(sys).isQZS()):
        ns = 4
        fns ='u4'
    else: 
        ns = 6
        fns = 'u6'
    if (sysNames(sys).isGLO()):
        tmp = 53 + i
    else:
        tmp = 50 + ns + i
    if(tmp > rtcm.len*8):
        return -1
    buff = rtcm.buff
    i,epo,gpsepo = decode_ssr_epoch(rtcm,sys)
    heads.epoch = epo
    heads.gpsepo = gpsepo
    heads.udi = getbitu(buff,i,'u4'); i += 4
    heads.sync = getbitu(buff,i,'u1'); i +=1
    heads.refd = getbitu(buff,i,'u1'); i += 1
    heads.iod = getbitu(buff,i,'u4'); i += 4
    heads.provid = getbitu(buff,i,'u16'); i += 16
    heads.solid  = getbitu(buff,i,'u4'); i += 4
    heads.nsat   = getbitu(buff,i,fns); i += ns
    heads.hsize = i
    # if(sys == 'G'):
    #     header = 'u12u20u4u1u1u4u16u4u6'
    # elif(sys == 'R'):
    #     header = 'u12u17u4u1u1u4u16u4u6'
    # elif(sys =='C'):
    return heads

def decode_ssr2_head(rtcm,sys):
    heads = HEADS()
    i = 24 + 12 
    if(sysNames(sys).isQZS()):
        ns = 4
        fns ='u4'
    else: 
        ns = 6
        fns = 'u6'
    if (sysNames(sys).isGLO()):
        tmp = 52 + i # u17u4u1u4u16u4u6
    else:
        tmp = 49 + ns + i #'u24u12u20u4u1u4u16u4u6' =91 GPS
    if(tmp > rtcm.len*8):
        return -1
    buff = rtcm.buff
    i,epo,gpsepo = decode_ssr_epoch(rtcm,sys)
    heads.epoch = epo
    heads.gpsepo = gpsepo
    heads.udi = getbitu(buff,i,'u4'); i += 4
    heads.sync = getbitu(buff,i,'u1'); i +=1
    heads.iod = getbitu(buff,i,'u4'); i += 4
    heads.provid = getbitu(buff,i,'u16'); i += 16
    heads.solid  = getbitu(buff,i,'u4'); i += 4
    heads.nsat   = getbitu(buff,i,fns); i += ns
    heads.hsize = i
    return heads
