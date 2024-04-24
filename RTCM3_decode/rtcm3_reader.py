# -*- coding: utf-8 -*-
"""
Created on Wed Mar 20 14:47:43 2024

@author: CHCUK-11
"""
import sys
import bitstruct
sys.dont_write_bytecode = True
from RTCM3_decode.EPH.ephData import ephnsat,ephlist
from RTCM3_decode.Codec.crc24q import crc24q
from RTCM3_decode.SSR.ssrData import SSRS_SYS
from RTCM3_decode.Codec.getbitu import getbitu
from RTCM3_decode.type_list import data_decoding

class rtcm3:
    def __init__(self):
        self.time = None
        self.nav = None
        #self.ssrgps = SSRS()  # decoded ssr
        #self.ssrbds = SSRS()  # decoded ssr
        #self.ssrgal = SSRS()  # decoded ssr
        #self.ssrglo = SSRS()  # decoded ssr
        self.nbyte = 0
        self.buff = bytearray(4096)
        self.len =  0 # full msg lenth

def input_rtcm3(rtcm,bytein,ssrin,ephin):
    # Ref: RTKLIB-rtklib_2.4.3\src\rtcm.c\input_rtcm3
    #print(data)    
    #rtcm.len = rtcm.len + len(data)
    PREAMBLE = b'\xd3' #RTCM3_preamble
    buffs = rtcm.nbyte
    buffe = buffs + 1
    #buff = rtcm.buff
    #buff[buffs:buffe] = data
    
    if(rtcm.nbyte == 0):    
        if(bytein != PREAMBLE):
            return 0
        #if(type(data) == bytes):
        rtcm.buff[buffs:buffe] = bytein
        rtcm.nbyte += 1
        return 0
    rtcm.buff[buffs:buffe] = bytein
    rtcm.nbyte += 1
    #print('nbyte',rtcm.nbyte)
    if rtcm.nbyte == 3:
        frame_header_unpack = bitstruct.unpack('u8u6u10',rtcm.buff) 
        rtcm.len   = frame_header_unpack[2] + 3
        #print('msglen',rtcm.len)
    
    if((rtcm.nbyte < 3) or (rtcm.nbyte < rtcm.len + 3 )):
        #print('nbyte',rtcm.nbyte,rtcm.len)
        return 0
    rtcm.nbyte = 0 # restart new full message
     
    # if(rtcm.nbyte == (rtcm.len + 3)):
    #     print('nbyte',rtcm.nbyte)
        #compute crc value for the complete msg, 
        #if correctly received,it should be 0
    # crc_fun = crcmod.crcmod.mkCrcFun(0x1864CFB,rev=False,
    #                                   initCrc=0x000000, xorOut=0x000000)
    # nlen = rtcm.len + 3
    # crc_value = crc_fun(rtcm.buff[0:nlen])
    
    # if crc_value != 0:
    #     print('warning in rtcm crc check')
    #     return 0
    
    #check parity
    #nlen = rtcm.len + 3
    if(crc24q(rtcm.buff,rtcm.len) != getbitu(rtcm.buff,rtcm.len*8,'u24')):
        #print('warning in rtcm crc check',rtcm.len)
        return 0
    return data_decoding(rtcm,ssrin,ephin)      

def decoderaw(rtcm,newmsg,ssrin=None,ephin=None):
    #Ref: rtklib_2.4.3\src\rtksvr.c\decoderaw
    # Filter ascii in rtcm
    datal = newmsg.splitlines(keepends= True)
    rec = 0
    rec0 = 0
    ret = 0
    buff = bytearray(len(newmsg))
    for i in range(len(datal)):
        nlen = len(datal[i])
        if (datal[i].find(b'RTCM') > 0):
            rec0 += nlen
            #print('ascii line', i)
            rec -= 1
        else:
            buff[rec:rec+nlen] = newmsg[rec0:rec0+nlen]
            rec0 += nlen
            rec += nlen
    ssrin=SSRS_SYS()
    eph0 = ephnsat()
    for i in range(len(buff)):
        if i == 69:
            print('lol')
        databyte = buff[i:i+1]
        ret = input_rtcm3(rtcm,databyte,ssrin,eph0)
        if (ret == -1):
            print('Warning in decoderaw')
    return ssrin, eph0

def rtcm3ssrf_read(filein): #for read RTCM3 file     
    with open(filein,'rb') as f:
        datain= f.read() # binary data
    rtcm = rtcm3()
    ret, ephdata = decoderaw(rtcm, datain)
    return ret, ephdata

# filepath = "D:\\AC\\GMV\\296987test.rtcm3"
#filepath = "D:\\swift_decode\\UK-20240229-SWIFT-SSR.rtcm3"
# filepath ="C:\Software\ROCG\EPH\EPH.rtcm3"
# data, ephdata = rtcm3ssrf_read(filepath)


