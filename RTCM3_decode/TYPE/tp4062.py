# -*- coding: utf-8 -*-
"""
Created on Wed Mar 20 14:24:49 2024

@author: CHCUK-11
"""
from RTCM3_decode.SSR import ssrData
from copy import deepcopy
from time_transform import time_format
from RTCM3_decode.common import SYS_GPS,SYS_GLO,SYS_GAL,SYS_BDS,SYS_QZS
GPS_SATS = 32; BDS_SATS = 65; GAL_SATS = 36 

CGCODEC_NFREQ = 5
CGCODEC_MAX_NUM_CODE = 61
CGCODEC_CODE_NONE = 0
CGCODEC_NUM_FREQ = 6 
SWIFTSBPHEADERLEN = 80
SWIFTRTCMHEADERLEN = 52
SSR1HGLOLEN = 53
SSR1HQZSLEN = 54
SSR1HALLLEN = 56
SSR2HGLOLEN = 52
SSR2HQZSLEN = 53
SSR2HALLLEN = 55
SSR1LEN = 12
SSR2LEN = 70
SSR3LEN = 5
SSR4LEN = 191
SSR5LEN = 6
SSR5LEN = 22
MAXCODE = 61

CGCODEC_CODE_NONE=0  #obs code: unkown
CGCODEC_CODE_L1C=1   #obs code: L1C/A, G1C/A, E1C(GPS,GLO,GAL,QZS,SBS)
CGCODEC_CODE_L1P=2   #obs code: L1P, G1P (GPS,GLO)
CGCODEC_CODE_L1W=3   #obs code: L1 Z-track (GPS)
CGCODEC_CODE_L1Y=4   #obs code: L1Y (GPS)
CGCODEC_CODE_L1M=5   #obs code: L1M (GPS)
CGCODEC_CODE_L1N=6   #obs code: L1codeless (GPS)
CGCODEC_CODE_L1S=7   #obs code: L1C(D) (GPS,QZS)
CGCODEC_CODE_L1L=8   #obs code: L1C(P) (GPS,QZS)
CGCODEC_CODE_L1E=9   #obs code: L1-SAIF (QZS)
CGCODEC_CODE_L1A=10  #obs code: E1A (GAL)
CGCODEC_CODE_L1B=11  #obs code: E1B (GAL)
CGCODEC_CODE_L1X=12  #obs code: E1B+C, L1C(D+P) (GAL,QZS)
CGCODEC_CODE_L1Z=13  #obs code: E1A+B+C, L1SAIF (GAL, QZS)
CGCODEC_CODE_L2C=14  #obs code: L2C/A, G1C/A (GPS, GLO)
CGCODEC_CODE_L2D=15  #obs code: L2 L1C/A-(P2-P1) (GPS)
CGCODEC_CODE_L2S=16  #obs code: L2C(M) (GPS, QZS)
CGCODEC_CODE_L2L=17  #obs code: L2C(L) (GPS,QZS)
CGCODEC_CODE_L2X=18  #obs code: L2C(M+L), B1I+Q (GPS,QZS,CMP)
CGCODEC_CODE_L2P=19  #obs code: L2P, G2P (GPS,GLO)
CGCODEC_CODE_L2W=20  #obs code: L2 Z-track (GPS)
CGCODEC_CODE_L2Y=21  #obs code: L2Y (GPS)
CGCODEC_CODE_L2M=22  #obs code: L2M (GPS)
CGCODEC_CODE_L2N=23  #obs code: L2codeless (GPS)
CGCODEC_CODE_L5I=24  #obs code: L5/E5aI (GPS, GAL, QZS, SBS) 
CGCODEC_CODE_L5Q=25  #obs code: L5/E5aQ (GPS, GAL, QZS, SBS)
CGCODEC_CODE_L5X=26  #obs code: L5/E5aI+Q (GPS, GAL, QZS, SBS)
CGCODEC_CODE_L7I=27  #obs code: E5bI, B2I (GAL, CMP)
CGCODEC_CODE_L7Q=28  #obs code: E5bQ, B2Q (GAL, CMP)
CGCODEC_CODE_L7X=29  #obs code: E5bI+Q, B2I+Q (GAL, CMP)
CGCODEC_CODE_L6A=30  #obs code: E6A (GAL)
CGCODEC_CODE_L6B=31  #obs code: E6B (GAL)
CGCODEC_CODE_L6C=32  #obs code: E6C (GAL)
CGCODEC_CODE_L6X=33  #obs code: E6B+C, LEXS+L, B3I+Q (GAL, QZS, CMP)
CGCODEC_CODE_L6Z=34  #obs code: E6A+B+C/L6 (GAL, QZS-Block II)
CGCODEC_CODE_L6S=35  #obs code: LEXS (QZS)
CGCODEC_CODE_L6L=36  #obs code: LEXL (QZS)
CGCODEC_CODE_L8I=37  #obs code: E5(a+b)I (GAL)
CGCODEC_CODE_L8Q=38  #obs code: E5(a+b)Q (GAL)
CGCODEC_CODE_L8X=39  #obs code: E5(a+b)I+Q (GAL), BD3-B2a+b
CGCODEC_CODE_L2I=40  #obs code: BII (CMP)
CGCODEC_CODE_L2Q=41  #obs code: B1Q (CMP)
CGCODEC_CODE_L6I=42  #obs code: B3I (CMP)
CGCODEC_CODE_L6Q=43  #obs code: B3Q (CMP)
CGCODEC_CODE_L3I=44  #obs code: G3I (GLO)
CGCODEC_CODE_L3Q=45  #obs code: G3Q (GLO)
CGCODEC_CODE_L3X=46  #obs code: G3I+Q (GLO)
CGCODEC_CODE_L1I=47  #obs code: B1I (BDS)
CGCODEC_CODE_L1Q=48  #obs code: B1Q (BDS)
CGCODEC_CODE_L5D=49  #obs code: L5D (QZS-Block II)
CGCODEC_CODE_L5P=50  #obs code: L5P (QZS-Block II)
CGCODEC_CODE_L5Z=51  #obs code: L5Z (QZS-Block II)
CGCODEC_CODE_L6E=52  #obs code: L6E (QZS-BLOCK II)
CGCODEC_CODE_L7D=53  #obs code: B2b (BDS3-B2b)
CGCODEC_CODE_L7P=54  #obs code: B2b (BDS3-B2b)
CGCODEC_CODE_L7Z=55  #obs code: B2b (BDS3-B2b)
CGCODEC_CODE_L1D=56  #obs code: B1Q (BDS3-B1)
CGCODEC_CODE_L8D=57  #obs code: B2a+b (BDS3-B2)
CGCODEC_CODE_L8P=58  #obs code: B2a+b (BDS3-B2)
CGCODEC_CODE_L6D=59  #obs code: B3A D (BDS3)
CGCODEC_CODE_L6P=60  #obs code: B3A P (BDS3)

ssrudint = [1,2,5,10,15,30,60,120,240,300,600,900,1800,3600,7200,10800]

cgcodec_mm_sig_ssr =["","1C","1P","1W","1Y","1M","1N","1S","1L","1E",
                     "1A","1B","1X","1Z","2C","2D","2S","2L","2X","2P",
                     "2W","2Y","2M","2N","5I","5Q","5X","7I","7Q","7X",
                     "6A","6B","6C","6X","6Z","6S","6L","8L","8Q","8X",
                     "2I","2Q","6I","6Q","3I","3Q","3X","","1I","1Q",
                     "5D","5P","5Z","6E","7D","7P","7Z","1D","5X","8P"]
cgcodec_mm_sig_ssr_gps_swift = ["1C","1P","1W","","","2C","2D","2S","2L","2X",
                                "2P","2W","","","5I","5Q","5X","1X","1Y","1X"]
cgcodec_mm_sig_ssr_gal_swift = ["1A","1B","1C","1X","1Z","5I","5Q","5X","7I",
                                "7Q","7X","8I","8Q","8X","6A","6B","6C","6X","6Z",""]
cgcodec_mm_sig_ssr_bds_swift = ["2I","2Q","2X","6I","6Q","6X","7I","7Q","7X",
                                "8D","8P","8S","5D","5P","5X","2I","2Q","2X","",""]
obscodes = ["","1C","1P","1W","1Y","1M","1N","1S","1L","1E",
            "1A","1B","1X","1Z","2C","2D","2S","2L","2X","2P",
            "2W","2Y","2M","2N","5I","5Q","5X","7I","7Q","7X",
            "6A","6B","6C","6X","6Z","6S","6L","8L","8Q","8X",
            "2I","2Q","6I","6Q","3I","3Q","3X","1I","1Q","5D",
            "5P","5Z","6E","7D","7P","7Z","1D","8D","8P","6D",
            "6P"]
obsfreqs = [0,1,1,1,1,1,1,1,1,1,
            1,1,1,1,2,2,2,2,2,2,
            2,2,2,2,3,3,3,5,5,5,
            4,4,4,4,4,4,4,6,6,6,
            2,2,4,4,3,3,3,1,1,3,
            3,3,4,5,5,5,1,6,6,4,
            4]
#------------------------------------------------------------------------------
def checkprnsys(sys,prn):
    if sys ==0 and 0<prn<=32: #GPS
        return 1
    elif sys == 3 and 0<prn<=64: #BDS
        return 1 
    elif sys == 5 and 0<prn<=36: #GAL
        return 1
    else:
        return -1
       
def codec_getbitu(buff,pos,lens):
    bits = 0
    for i in range(pos, pos + lens):
        bits = (bits << 1) + ((buff[i // 8] >> (7 - i % 8)) & 1)
    return bits

def codec_getbituswap(buff,pos,lens):
    bits = 0
    for i in range(pos, pos + lens):
        bits = (bits << 1) + ((buff[i // 8] >> (7 - i % 8)) & 1)
    if(lens == 16):
        bits = ((bits & 0x00FF) << 8) | ((bits & 0xFF00) >> 8)
    if(lens == 32):
        bits = ((bits & 0xFF) << 24) | ((bits & 0xFF00) << 8) | ((bits & 0xFF0000) >> 8) | ((bits & 0xFF000000) >> 24)
    return bits

def codec_getbitsswap(buff,pos,lens):
    bits = 0
    bits2 = 0
    for i in range(pos, pos + lens):
        bits = (bits << 1) + ((buff[i // 8] >> (7 - i % 8)) & 1)
    bits2 = bits
    bits2 = ((bits2 & 0x00FF) << 8) | ((bits2 & 0xFF00) >> 8)
    return  bits2

def codec_getsnbits(buff,pos,lens):
    bits = codec_getbitu(buff, pos+1, lens-1)
    sign = -1 if (buff[pos // 8] & (0x01 << (7 - pos % 8))) else 1 
    if sign < 0:    
        return -bits
    else:
        return bits

def codec_getbits(buff,pos,lens):
    bits = codec_getbitu(buff, pos, lens)
    if lens <= 0 or lens >=32 or not (bits & (1<<(lens - 1))):
        return bits
    else:
        return bits|(~0<<lens)

def get_pbias_freq_gps(mode):
    if mode in [CGCODEC_CODE_L1C, CGCODEC_CODE_L1P, CGCODEC_CODE_L1W, CGCODEC_CODE_L1M,CGCODEC_CODE_L1Y]:
        return 0
    elif mode in [CGCODEC_CODE_L2C, CGCODEC_CODE_L2D, CGCODEC_CODE_L2S, CGCODEC_CODE_L2L, CGCODEC_CODE_L2X, 
                  CGCODEC_CODE_L2P, CGCODEC_CODE_L2W, CGCODEC_CODE_L2X, CGCODEC_CODE_L2M]:
        return 1
    elif mode in [CGCODEC_CODE_L5I, CGCODEC_CODE_L5Q, CGCODEC_CODE_L5X]:
        return 2
    else:
        return -1

def get_pbias_freq_glo(mode):
    if mode in [CGCODEC_CODE_L1C, CGCODEC_CODE_L1P]:
        return 0
    elif mode in [CGCODEC_CODE_L2C, CGCODEC_CODE_L2P]:
        return 1
    else:
        return -1

def get_pbias_freq_gal(mode):
    if mode in [CGCODEC_CODE_L1A, CGCODEC_CODE_L1B,CGCODEC_CODE_L1C, CGCODEC_CODE_L1X, CGCODEC_CODE_L1Z]:
        return 0
    elif mode in [CGCODEC_CODE_L7I, CGCODEC_CODE_L7Q, CGCODEC_CODE_L7X]:
        return 2
    elif mode in [CGCODEC_CODE_L8I, CGCODEC_CODE_L8Q, CGCODEC_CODE_L8X]:
        return 3
    elif mode in [CGCODEC_CODE_L6A, CGCODEC_CODE_L6B, CGCODEC_CODE_L6C, CGCODEC_CODE_L6X, CGCODEC_CODE_L6Z]:
        return 4
    else:
        return -1

def get_pbias_freq_bds(mode):
    if mode in [CGCODEC_CODE_L1I, CGCODEC_CODE_L2I, CGCODEC_CODE_L1Q, CGCODEC_CODE_L2Q, CGCODEC_CODE_L2X]:
        return 0
    elif mode in [CGCODEC_CODE_L7I, CGCODEC_CODE_L7Q, CGCODEC_CODE_L7X, CGCODEC_CODE_L7D, CGCODEC_CODE_L7P, CGCODEC_CODE_L7Z]:
        return 1
    elif mode in [CGCODEC_CODE_L6I, CGCODEC_CODE_L6Q, CGCODEC_CODE_L6X]:
        return 2
    elif mode in [CGCODEC_CODE_L1D, CGCODEC_CODE_L1P, CGCODEC_CODE_L1X]:
        return 3
    elif mode in [CGCODEC_CODE_L5D, CGCODEC_CODE_L5P, CGCODEC_CODE_L5X]:
        return 4
    else:
        return -1
    
def get_pbias_freq_qzs(mode):
    if mode in [CGCODEC_CODE_L1C, CGCODEC_CODE_L1S, CGCODEC_CODE_L1L, CGCODEC_CODE_L1X, CGCODEC_CODE_L1Z]:
        return 0
    elif mode in [CGCODEC_CODE_L2S, CGCODEC_CODE_L2L, CGCODEC_CODE_L2X]:
        return 1
    elif mode in [CGCODEC_CODE_L5I, CGCODEC_CODE_L5Q, CGCODEC_CODE_L5X]:
        return 2
    else:
        return -1
    
def codec_get_pbias_freq(sys,mode):
    if (mode >= MAXCODE) or (mode<=CGCODEC_CODE_NONE):
        return -1 
    if sys == SYS_GPS:
        return get_pbias_freq_gps(mode)
    elif sys == SYS_GAL:
        return get_pbias_freq_gal(mode)
    elif sys == SYS_GLO:
        return get_pbias_freq_glo(mode)
    elif sys == SYS_BDS:
        return get_pbias_freq_bds(mode)
    elif sys == SYS_QZS:
        return get_pbias_freq_qzs(mode)
    return

def codec_obs2code(obs,freq):
    if freq is not None:
        freq = 0
    for i in range(0, CGCODEC_MAX_NUM_CODE):
        if obs == obscodes[i]:
            if freq is not None:
                freq = obsfreqs[i]
            return i
    return CGCODEC_CODE_NONE
#------------------------------------------------------------------------------
def decode_type4062(rtcm,ssr):
    "swift" 
    buff = rtcm.buff
    protocolType = codec_getbitu(buff, 36, 4)
    try:
        if protocolType == 0:
            "atmospheric data"
            sbptype = codec_getbitu(buff, 40, 16)
            senderID = codec_getbitu(buff, 56, 16)
            meglen = codec_getbitu(buff, 72, 8)
            decode_SBP_atm(sbptype, rtcm, meglen,ssr)     
        elif protocolType == 1:
            "sys ssr"
            sbptype = codec_getbitu(buff, 40, 12)
            decode_SBP_ssr(sbptype, rtcm, ssr)
    except:
        print('Warning in decoding_type4062')
        return -1
    return 3

def decode_SBP_atm(sbptype,rtcm,meglen,ssr):
    if sbptype == 3001:
        try:
            decode_SBP3001(rtcm,meglen,ssr)
        except:
            print('Warning in decoding SBP3001')
            pass
    elif sbptype == 1528:
        try:
            decode_SBP1528(rtcm, meglen,ssr)
        except:
            print('Warning in decoding SBP1528')
            pass
    elif sbptype == 1532:
        try:
            decode_SBP1532(rtcm, meglen,ssr)
        except:
            print('Warning in decoding SBP1532')
            pass    
    elif sbptype == 1533:
        try:
            decode_SBP1533(rtcm, meglen,ssr)
        except:
            print('Warning in decoding SBP1533')
            pass
    elif sbptype == 1534:
        try:
            decode_SBP1534(rtcm, meglen,ssr)
        except:
            print('Warning in decoding SBP1534')
            pass
    return

def decode_SBP_ssr(sbptype,rtcm,ssr):
    if sbptype == 3242:
        try:
            decode_ssr3(rtcm,SYS_GAL,ssr,1)
        except:
            print('Warning in decoding SBP3242')
            pass
    elif sbptype == 3243:
        try:
            decode_ssr4(rtcm,SYS_GAL,ssr,1)
        except:
            print('Warning in decoding SBP3243')
    elif sbptype == 3260:
        try:
            decode_ssr3(rtcm,SYS_BDS,ssr,1)
        except:
            print('Warning in decoding SBP3260')
    elif sbptype == 3261:
        try:
            decode_ssr4(rtcm,SYS_BDS,ssr,1)
        except:
            print('Warning in decoding SBP3261')
    elif sbptype == 3265:
        try:
            decode_ssr7_ex(rtcm,SYS_GPS,ssr,1)
        except:
            print('Warning in decoding SBP3265')
            pass
    elif sbptype == 3267:
        try:
            decode_ssr7_ex(rtcm,SYS_GAL,ssr,1)
        except:
            print('Warning in decoding SBP3267')
    elif sbptype == 3270:
        try:
            decode_ssr7_ex(rtcm,SYS_BDS,ssr,1)
        except:
            print('Warning in decoding SBP3270')       
    return
#------------------------------------------------------------------------------
def decode_SBP1528(rtcm,meglen,ssr):
    "Provide the reference area and grid structure for atmospheric corrections"
    i = SWIFTSBPHEADERLEN
    buff = rtcm.buff
    swift1528 = ssrData.swift_grid()
    obstow = codec_getbituswap(buff, i, 32); i+=32
    obsweek = codec_getbituswap(buff, i, 16); i+=16
    swift1528.time = timeFormat.gpsTime([obsweek,obstow,0]).datetime
    
    swift1528.udi = codec_getbitu(buff, i, 8); i+=8
    swift1528.solid = codec_getbitu(buff, i, 8); i+=8
    swift1528.iodatm = codec_getbitu(buff, i, 8); i+=8
    swift1528.tilesid = codec_getbituswap(buff, i, 16); i+=16
    swift1528.tileid = codec_getbituswap(buff, i, 16); i+=16
    slat = codec_getbitsswap(buff, i, 16); i+=16
    if slat <= 2**14:
        swift1528.NWlat = (slat*90)/2**14
    else:
        swift1528.NWlat = ((slat-2**14)*90)/2**14 - 90
    
    slon = codec_getbitsswap(buff, i, 16); i+=16
    if slon <= 2**15:    
        swift1528.NWlon = (slon*180)/2**15
    else:
        swift1528.NWlon = ((slon-2**15)*180)/2**15 - 180    
    swift1528.splat = (codec_getbituswap(buff, i, 16))*0.01; i+=16
    swift1528.splon = (codec_getbituswap(buff, i, 16))*0.01; i+=16
    swift1528.rows = codec_getbituswap(buff, i, 16); i+=16
    swift1528.columns = codec_getbituswap(buff, i, 16); i+=16
    swift1528.bitmark = codec_getbitu(buff, i, 64); i+=64
    ssr.swift.swiftgrid.append(swift1528)
    return

def decode_SBP1533(rtcm,meglen,ssr):
    "Provide tile wide ionospheric correction polynomial"
    i = SWIFTSBPHEADERLEN
    buff = rtcm.buff
    #swift1533 = ssr.swift.swiftion
    swift1533 = ssrData.swift_ion()
    obstow = codec_getbituswap(buff, i, 32); i+=32
    obsweek = codec_getbituswap(buff, i, 16); i+=16
    swift1533.time = timeFormat.gpsTime([obsweek,obstow,0]).datetime
    
    nmsg = codec_getbitu(buff, i, 8); i+=8
    nseq = codec_getbitu(buff, i, 8); i+=8
    udi = codec_getbitu(buff, i, 8); i+=8
    swift1533.udi = ssrudint[udi]
    swift1533.solid = codec_getbitu(buff, i, 8); i+=8
    swift1533.iodatm = codec_getbitu(buff, i, 8); i+=8
    swift1533.tilesid = codec_getbituswap(buff, i, 16); i+=16
    swift1533.tileid = codec_getbituswap(buff, i, 16); i+=16
    ns = codec_getbitu(buff, i, 8); i+=8
    if ns <0:
        print("Warning in decoderaw SBP1533")
    else:
        j = 0
        while j < ns and i + 88 <= rtcm.len * 8:
            prn = codec_getbitu(buff, i, 8); i+=8
            sys = codec_getbitu(buff, i, 8); i+=8
            sat = checkprnsys(sys, prn)
            if 0 < sat :
                ionmeg = ssrData.swift_ion_prn()
                ionmeg.svid = prn
                ionmeg.sysid = sys 
                ionmeg.stecQT = codec_getbitu(buff, i, 8); i+=8
                # ionmeg.ionpolyC.append(codec_getbitsswap(buff, i, 16)); i+=16
                # ionmeg.ionpolyC.append(codec_getbitsswap(buff, i, 16)); i+=16
                # ionmeg.ionpolyC.append(codec_getbitsswap(buff, i, 16)); i+=16
                # ionmeg.ionpolyC.append(codec_getbitsswap(buff, i, 16)); i+=16
                ionmeg.ionpolyC.append((codec_getbitsswap(buff, i, 16))*0.05); i+=16
                ionmeg.ionpolyC.append((codec_getbitsswap(buff, i, 16))*0.02); i+=16
                ionmeg.ionpolyC.append((codec_getbitsswap(buff, i, 16))*0.02); i+=16
                ionmeg.ionpolyC.append((codec_getbitsswap(buff, i, 16))*0.02); i+=16
                ionmeg.update = 1
                swift1533.ion.append(ionmeg)
            else:
                continue
            j+=1
        # for j in range(0, ns):
        #     if (i + 88) <= (rtcm.len *8):
        #         prn = codec_getbitu(buff, i, 8); i+=8
        #         sys = codec_getbitu(buff, i, 8); i+=8
        #         sat = checkprnsys(sys, prn)
        #         if sat>0:
        #             ionmeg = ssrData.swift_ion_prn()
        #             ionmeg.svid = prn
        #             ionmeg.sysid = sys 
        #             ionmeg.stecQT = codec_getbitu(buff, i, 8); i+=8
        #             ionmeg.ionpolyC.append(codec_getbitsswap(buff, i, 16)); i+=16
        #             ionmeg.ionpolyC.append(codec_getbitsswap(buff, i, 16)); i+=16
        #             ionmeg.ionpolyC.append(codec_getbitsswap(buff, i, 16)); i+=16
        #             ionmeg.ionpolyC.append(codec_getbitsswap(buff, i, 16)); i+=16
        #             ionmeg.update = 1
        #             swift1533.ion.append(ionmeg)
        #         else:
        #             pass
        #     else:
        #         pass
        ssr.swift.swiftion.append(swift1533)
    return

def decode_SBP1534(rtcm,meglen,ssr):
    "Provide grid point specific tropospheric and ionospheric residual corrections and bounds"
    i = SWIFTSBPHEADERLEN
    buff = rtcm.buff
    #swift1534 = ssr.swift.swiftatm
    swift1534 = ssrData.swift_atm()
    obstow = codec_getbituswap(buff, i, 32); i+=32
    obsweek = codec_getbituswap(buff, i, 16); i+=16
    swift1534.time = timeFormat.gpsTime([obsweek,obstow,0]).datetime
    
    nmsg = codec_getbitu(buff, i, 8); i+=8
    nseq = codec_getbitu(buff, i, 8); i+=8
    udi = codec_getbitu(buff, i, 8); i+=8
    swift1534.udi = ssrudint[udi]
    swift1534.solid = codec_getbitu(buff, i, 8); i+=8
    swift1534.atmiod = codec_getbitu(buff, i, 8); i+=8
    swift1534.tilesid = codec_getbituswap(buff, i, 16); i+=16
    swift1534.tileid = codec_getbituswap(buff, i, 16); i+=16
    swift1534.tropQI = codec_getbitu(buff, i, 8); i+=8
    swift1534.grididx = codec_getbituswap(buff, i, 16); i+=16
    swift1534.tropdelay.append(codec_getbitsswap(buff, i, 16)); i+=16
    swift1534.tropdelay.append(codec_getbits(buff, i, 8)); i+=8
    swift1534.tropdelaystd = codec_getbitu(buff, i, 8); i+=8
    swift1534.tropebmean.append(codec_getbitu(buff, i, 8)); i+=8
    swift1534.tropebstd.append(codec_getbitu(buff, i, 8)); i+=8
    swift1534.tropebmean.append(codec_getbitu(buff, i, 8)); i+=8
    swift1534.tropebstd.append(codec_getbitu(buff, i, 8)); i+=8
    ns = codec_getbitu(buff, i, 8); i+=8
    
    if ns < 0:
        print("Warning in decoderaw SBP1534")
        pass
    else:
        for j in range(0,ns):
            if (i+72) <= (rtcm.len *8):
                prn = codec_getbitu(buff, i, 8); i+=8
                sys = codec_getbitu(buff, i, 8); i+=8
                sat = checkprnsys(sys, prn)
                if sat > 0 :
                    atmmeg = ssrData.swift_atm_prn()
                    atmmeg.svid = prn
                    atmmeg.sysid = sys
                    atmmeg.STECres = codec_getbitsswap(buff, i, 16); i+=16
                    atmmeg.STECstd = codec_getbitu(buff, i, 8); i+=8
                    atmmeg.STECebmean = codec_getbitu(buff, i, 8); i+=8
                    atmmeg.STECebstd = codec_getbitu(buff, i, 8); i+=8
                    atmmeg.STECebmeanC = codec_getbitu(buff, i, 8); i+=8
                    atmmeg.STECebstdC = codec_getbitu(buff, i, 8); i+=8
                    atmmeg.update = 1
                    swift1534.atm.append(atmmeg)
                else:
                    pass
            else:
                pass
        ssr.swift.swiftatm.append(swift1534)
    return

def decode_SBP1532(rtcm,meglen,ssr):
    i = SWIFTSBPHEADERLEN
    buff = rtcm.buff
    #swift1532 = ssr.swift.swiftatm
    swift1532 = ssrData.swift_atm()
    swift1532.tilesid = codec_getbituswap(buff, i, 16); i+=16
    swift1532.tileid = codec_getbituswap(buff, i, 16); i+=16
    obstow = codec_getbituswap(buff, i, 32); i+=32
    obsweek = codec_getbituswap(buff, i, 16); i+=16
    swift1532.time = timeFormat.gpsTime([obsweek,obstow,0]).datetime
    
    nmsg = codec_getbituswap(buff, i, 8); i+=16
    nseq = codec_getbituswap(buff, i, 8); i+=16
    udi = codec_getbitu(buff, i, 8); i+=8
    swift1532.udi = ssrudint[udi]
    swift1532.atmiod = codec_getbitu(buff, i, 8); i+=8
    swift1532.tropQI = codec_getbitu(buff, i, 8); i+=8
    swift1532.grididx = codec_getbituswap(buff, i, 16); i+=16
    swift1532.tropdelay.append(codec_getbitsswap(buff, i, 16)); i+=16
    swift1532.tropdelay.append(codec_getbits (buff, i, 8)); i+=8
    swift1532.tropdelaystd = codec_getbitu(buff, i, 8); i+=8
    j = 0
    while (i+40) <= (rtcm.len *8):
        prn = codec_getbitu(buff, i, 8); i+=8
        sys = codec_getbitu(buff, i, 8); i+=8
        sat = checkprnsys(sys, prn)
        if sat > 0 :
            atmmeg = ssrData.swift_atm_prn()
            atmmeg.svid = prn
            atmmeg.sysid = sys
            atmmeg.STECres = codec_getbitsswap(buff, i, 16); i+=16
            atmmeg.STECstd = codec_getbitu(buff, i, 8); i+=8
            atmmeg.update = 1
            swift1532.atm.append(atmmeg)
            j+=1
        else:
            pass
    ssr.swift.swiftatm.append(swift1532)  
    return

def decode_SBP3001(rtcm,meglen,ssr):
    "Communicate monitored states and flag integrity failures"
    i = SWIFTSBPHEADERLEN
    if (rtcm.len *8) >= (248+i):
        buff = rtcm.buff
        #swift3001 = ssr.swift.swiftintegflag
        swift3001 = ssrData.swift_integflag()
        obstow = codec_getbituswap(buff, i, 32); i+=32
        obsweek = codec_getbituswap(buff, i, 16); i+=16
        swift3001.obstime = timeFormat.gpsTime([obsweek,obstow,0]).datetime
        
        corrtow = codec_getbituswap(buff, i, 32); i+=32
        corrweek = codec_getbituswap(buff, i, 16); i+=16
        swift3001.corrtime = timeFormat.gpsTime([corrweek,corrtow,0]).datetime
        
        swift3001.solid = codec_getbitu(buff, i, 8); i+=8
        swift3001.tilesid = codec_getbituswap(buff, i, 16); i+=16
        swift3001.tileid = codec_getbituswap(buff, i, 16); i+=16
        swift3001.chainid = codec_getbitu(buff, i, 8); i+=8
        swift3001.useG = codec_getbitu(buff, i, 8); i+=8
        swift3001.useE = codec_getbitu(buff, i, 8); i+=8
        swift3001.useC = codec_getbitu(buff, i, 8); i+=8
        i+=48 # reserved
        swift3001.usetropgp = codec_getbitu(buff, i, 8); i+=8
        swift3001.useionogp = codec_getbitu(buff, i, 8); i+=8
        swift3001.useionotilesatlos = codec_getbitu(buff, i, 8); i+=8
        swift3001.useionogpsatlos = codec_getbitu(buff, i, 8); i+=8
        swift3001.update = 1
        ssr.swift.swiftintegflag.append(swift3001)
    else:
        print("Warning in decoderaw SBP3001")
        pass
    return

#------------------------------------------------------------------------------
def decode_ssr3(rtcm,sys,ssr,rtcmtype):
    "SBP 3242, 3260"
    buff = rtcm.buff
    if sys==SYS_GPS and rtcmtype==1:
        curRtcmType = 0
    else:
        curRtcmType = rtcmtype
    
    codes_gps= [CGCODEC_CODE_L1C, CGCODEC_CODE_L1P, CGCODEC_CODE_L1W, CGCODEC_CODE_L1Y, CGCODEC_CODE_L1M,
                CGCODEC_CODE_L2C, CGCODEC_CODE_L2D, CGCODEC_CODE_L2S, CGCODEC_CODE_L2L, CGCODEC_CODE_L2X,
                CGCODEC_CODE_L2P, CGCODEC_CODE_L2W, CGCODEC_CODE_L2Y, CGCODEC_CODE_L2M, CGCODEC_CODE_L5I,
                CGCODEC_CODE_L5Q, CGCODEC_CODE_L5X]
    
    #codes_glo= [CGCODEC_CODE_L1C, CGCODEC_CODE_L1P, CGCODEC_CODE_L2C, CGCODEC_CODE_L2P]
    
    codes_gal= [CGCODEC_CODE_L1A, CGCODEC_CODE_L1B, CGCODEC_CODE_L1C, CGCODEC_CODE_L1X, CGCODEC_CODE_L1Z,
                CGCODEC_CODE_L5I, CGCODEC_CODE_L5Q, CGCODEC_CODE_L5X, CGCODEC_CODE_L7I, CGCODEC_CODE_L7Q,
                CGCODEC_CODE_L7X, CGCODEC_CODE_L8I, CGCODEC_CODE_L8Q, CGCODEC_CODE_L8X, CGCODEC_CODE_L6A,
                CGCODEC_CODE_L6B, CGCODEC_CODE_L6C, CGCODEC_CODE_L6X, CGCODEC_CODE_L6Z]
    
    # codes_qzs= [CGCODEC_CODE_L1C, CGCODEC_CODE_L1S, CGCODEC_CODE_L2S, CGCODEC_CODE_L2L, CGCODEC_CODE_L2X,
    #             CGCODEC_CODE_L5I, CGCODEC_CODE_L5Q, CGCODEC_CODE_L5X, CGCODEC_CODE_L6S, CGCODEC_CODE_L6L,
    #             CGCODEC_CODE_L6X, CGCODEC_CODE_L1X]
    
    codes_bds= [CGCODEC_CODE_L1I, CGCODEC_CODE_L1Q, CGCODEC_CODE_L1X, CGCODEC_CODE_L7I, CGCODEC_CODE_L7Q,
                CGCODEC_CODE_L6I, CGCODEC_CODE_L6Q, CGCODEC_CODE_L6X]
    
    #codes_sbs= [CGCODEC_CODE_L1C, CGCODEC_CODE_L5I, CGCODEC_CODE_L5Q, CGCODEC_CODE_L5X]
    
    provid = 0; solid = 0;
    if curRtcmType ==0:
        i = 24+12
    else:
        i = SWIFTRTCMHEADERLEN

    SSR2H = SSR2HALLLEN
    
    if (i+SSR2H) > rtcm.len*8:
        print("Warning in decoderaw ssr3")
        return
    
    if sys == SYS_BDS:
        tow = codec_getbitu(buff, i, 20); i+=20
        realtimebds = timeFormat.bdsTime()
        towbds = realtimebds.adjweek(tow)
        ssrtime = towbds.datetime
        if towbds.GPSSOW in ssr.swift.bdsssr.epoch:
            #tindex = ssr.swift.bdsssr.epoch.index(tow)
            tindex = ssr.swift.bdsssr.epoch.index(towbds.GPSSOW)
            ssrlist = ssr.swift.bdsssr.ssr[tindex]
        else:
            #ssr.swift.bdsssr.epoch.append(tow)
            ssr.swift.bdsssr.epoch.append(towbds.GPSSOW)
            ssr.swift.bdsssr.ssr.append(ssrData.swift_ssr_sys(SYS_BDS))
            ssrlist = ssr.swift.bdsssr.ssr[-1]
    
    elif sys == SYS_GAL:
        tow = codec_getbitu(buff, i, 20); i+=20
        realtimegal = timeFormat.galTime()
        towgal = realtimegal.adjweek(tow)
        ssrtime = towgal.datetime
        if towgal.GPSSOW in ssr.swift.galssr.epoch:
            #tindex = ssr.swift.galssr.epoch.index(tow)
            tindex = ssr.swift.galssr.epoch.index(towgal.GPSSOW)
            ssrlist = ssr.swift.galssr.ssr[tindex]
        else:
            #ssr.swift.galssr.epoch.append(tow)
            ssr.swift.galssr.epoch.append(towgal.GPSSOW)
            ssr.swift.galssr.ssr.append(ssrData.swift_ssr_sys(SYS_GAL))
            ssrlist = ssr.swift.galssr.ssr[-1]
        
    udi = codec_getbitu(buff, i, 4); i+=4
    sync = codec_getbitu(buff, i, 1); i+=1
    iod = codec_getbitu(buff, i, 4); i+=4
    provid = codec_getbitu(buff, i, 16); i+=16
    solid = codec_getbitu(buff, i, 4); i+=4
    if (sys == SYS_QZS):
        nsat = codec_getbitu(buff, i, 4); i+=4
    else:
        nsat = codec_getbitu(buff, i, 6); i+=6
    
    udint = ssrudint[udi]
    
    if nsat < 0:
        print("Warning in decoderaw ssr3")
        return
    
    if sys == SYS_GPS: 
        np=6; offp=0; codes=codes_gps; ncode=17;ssrid = 0
    # elif sys == SYS_GLO:
    #     np=5; offp=0; codes=codes_glo; ncode=4
    elif sys == SYS_GAL:
        np=6; offp=0; codes=codes_gal; ncode=19;ssrid = 3
    # elif sys == SYS_QZS:
    #     np=4; offp=0; codes=codes_qzs; ncode=13
    elif sys == SYS_BDS:
        np=6; offp=0; codes=codes_bds; ncode=9;ssrid = 5
    
    ncode = 20
    for j in range(0,nsat):
        if (i+SSR3LEN+np)<=(rtcm.len*8):            
            prn = codec_getbitu(buff, i, np) + offp; i+=np
            nbias = codec_getbitu(buff, i, 5); i+=5
            cbias = [0 for m in range(MAXCODE)]
            for k in range(0,nbias):
                mode = codec_getbitu(buff, i, 5); i+=5
                bias = (codec_getbits(buff, i, 14))*0.01; i+=14
                if mode < ncode:
                    if rtcmtype == 0:
                        cbias[mode] = bias
                    else:
                        if sys == SYS_GPS:
                            curcode = codec_obs2code(cgcodec_mm_sig_ssr_gps_swift[mode] , None)
                        elif sys == SYS_GAL:
                            curcode = codec_obs2code(cgcodec_mm_sig_ssr_gal_swift[mode] , None)
                        elif sys == SYS_BDS:
                            curcode = codec_obs2code(cgcodec_mm_sig_ssr_bds_swift[mode] , None)
                        cbias[curcode] = bias
                else:
                    print("Warning in decoderaw ssr3")
                    pass
            codeCount = 0
            ssr3prndata = deepcopy(ssrlist.sats[j])
            ssr3prndata.codeCount = codeCount
            ssr3prndata.sys_id = ssrid
            ssr3prndata.svid = prn
            ssr3prndata.t0[4] = ssrtime
            ssr3prndata.udi[4] = udint
            ssr3prndata.iod[4] = iod            
            for n in range(0,MAXCODE):
                if (cbias[n] != 0) and (ssr3prndata.codeCount < CGCODEC_NUM_FREQ*2):
                    dataindex = ssr3prndata.codeCount
                    ssr3prndata.cbias[dataindex] = cbias[n]
                    #ssr3prndata.codeIndex[dataindex] = n
                    ssr3prndata.codeCount = dataindex+1

            ssrlist.sats[j] = ssr3prndata
    return

def decode_ssr4(rtcm,sys,ssr,rtcmtype):
    "SBP 3243, 3261"
    buff = rtcm.buff
    refd = 0
    #
    if rtcmtype == 0:
        i = 24+12
    else:
        i = SWIFTRTCMHEADERLEN
    SSR1H = SSR1HALLLEN
    if i+SSR1H > (rtcm.len)*8:
        print("Warning in decoderaw ssr4")
        return
    if sys == SYS_BDS:
        tow = codec_getbitu(buff, i, 20); i+=20
        realtimebds = timeFormat.bdsTime()
        towbds = realtimebds.adjweek(tow)
        ssrtime = towbds.datetime
        if towbds.GPSSOW in ssr.swift.bdsssr.epoch:
            #tindex = ssr.swift.bdsssr.epoch.index(tow)
            tindex = ssr.swift.bdsssr.epoch.index(towbds.GPSSOW)
            ssrlist = ssr.swift.bdsssr.ssr[tindex]
        else:
            #ssr.swift.bdsssr.epoch.append(tow)
            ssr.swift.bdsssr.epoch.append(towbds.GPSSOW)
            ssr.swift.bdsssr.ssr.append(ssrData.swift_ssr_sys(SYS_BDS))
            ssrlist = ssr.swift.bdsssr.ssr[-1]
    
    elif sys == SYS_GAL:
        tow = codec_getbitu(buff, i, 20); i+=20
        realtimegal = timeFormat.galTime()
        towgal = realtimegal.adjweek(tow)
        ssrtime = towgal.datetime
        if towgal.GPSSOW in ssr.swift.galssr.epoch:
            #tindex = ssr.swift.galssr.epoch.index(tow)
            tindex = ssr.swift.galssr.epoch.index(towgal.GPSSOW)
            ssrlist = ssr.swift.galssr.ssr[tindex]
        else:
            #ssr.swift.galssr.epoch.append(tow)
            ssr.swift.galssr.epoch.append(towgal.GPSSOW)
            ssr.swift.galssr.ssr.append(ssrData.swift_ssr_sys(SYS_GAL))
            ssrlist = ssr.swift.galssr.ssr[-1]
    
    udi = codec_getbitu(buff, i, 4); i+=4
    sync = codec_getbitu(buff, i, 1); i+=1
    if rtcmtype == 0:
        refd = codec_getbitu(buff, i, 1); i+=1
    iod = codec_getbitu(buff, i, 4); i+=4
    provid = codec_getbitu(buff, i, 16); i+=16
    solid = codec_getbitu(buff, i, 4); i+=4
    if (sys == SYS_QZS):
        nsat = codec_getbitu(buff, i, 4); i+=4
    else:
        nsat = codec_getbitu(buff, i, 6); i+=6
    udint = ssrudint[udi]
    #
    if nsat < 0 :
        print("Warning in decoderaw ssr4")
        return
    if sys == SYS_GPS:
        np=6;ni=8;nj=0;offp=0;ssrid=0
    # elif sys == SYS_GLO:
    #     np=5;ni=8;nj=0;offp=0
    elif sys == SYS_GAL:
        np=6;ni=10;nj=0;offp=0;ssrid=3
    elif sys == SYS_BDS:
        np=6;offp=0;ssrid=5
        if rtcmtype == 0:
            ni=10;nj=8
        else:
            ni=8;nj=0 
    
    for j in range(0,nsat):
        if (i+SSR4LEN+np+ni+nj) <= (rtcm.len)*8:
            prn = codec_getbitu(buff, i, np)+offp; i+=np
            iode = codec_getbitu(buff, i, ni); i+=ni
            iodcrc = codec_getbitu(buff, i, nj); i+=nj
            ssr4prndata = deepcopy(ssrlist.sats[j]) 
            ssr4prndata.deph[0] = codec_getbits(buff, i, 22)*1E-4; i+=22
            ssr4prndata.deph[1] = codec_getbits(buff, i, 20)*4E-4; i+=20
            ssr4prndata.deph[2] = codec_getbits(buff, i, 20)*4E-4; i+=20
            ssr4prndata.ddeph[0] = codec_getbits(buff, i, 21)*1E-6; i+=21
            ssr4prndata.ddeph[1] = codec_getbits(buff, i, 19)*4E-6; i+=19
            ssr4prndata.ddeph[2] = codec_getbits(buff, i, 19)*4E-6; i+=19
            ssr4prndata.dclk[0] = codec_getbits(buff, i, 22)*1E-4; i+=22
            ssr4prndata.dclk[1] = codec_getbits(buff, i, 21)*1E-6; i+=21
            ssr4prndata.dclk[2] = codec_getbits(buff, i, 27)*2E-8; i+=27
            ssr4prndata.sys_id = ssrid
            ssr4prndata.prn = prn
            ssr4prndata.iode = iode
            ssr4prndata.refd = refd
            ssr4prndata.iodcrc = iodcrc
            ssr4prndata.t0[0] = ssrtime
            ssr4prndata.t0[1] = ssrtime
            ssr4prndata.udi[0] = udint
            ssr4prndata.udi[1] = udint
            ssr4prndata.iod[0] = iod
            ssr4prndata.iod[1] = iod 
            ssrlist.sats[j] = ssr4prndata
    return

def decode_ssr7_ex(rtcm,sys,ssr,rtcmtype):
    "SBP 3265, 3267, 3270"
    buff = rtcm.buff
    pbias= [0 for i in range(MAXCODE)]
    stdpb= [0 for i in range(MAXCODE)]
    
    if rtcmtype == 0:
        i = 24+12
    else:
        i = SWIFTRTCMHEADERLEN
    if sys==SYS_QZS:
        ns=4
    else:
        ns=6
    if sys == SYS_GLO:
        syscheck = 52
    else:
        syscheck = 49
    if (i+syscheck-2)>(rtcm.len)*8:
        print("Warning in decoderaw ssr7_ex")
        return
    
    if sys == SYS_BDS:
        tow = codec_getbitu(buff, i, 20); i+=20
        realtimebds = timeFormat.bdsTime()
        towbds = realtimebds.adjweek(tow)
        ssrtime = towbds.datetime
        if towbds.GPSSOW in ssr.swift.bdsssr.epoch:
            #tindex = ssr.swift.bdsssr.epoch.index(tow)
            tindex = ssr.swift.bdsssr.epoch.index(towbds.GPSSOW)
            ssrlist = ssr.swift.bdsssr.ssr[tindex]
        else:
            #ssr.swift.bdsssr.epoch.append(tow)
            ssr.swift.bdsssr.epoch.append(towbds.GPSSOW)
            ssr.swift.bdsssr.ssr.append(ssrData.swift_ssr_sys(SYS_BDS))
            ssrlist = ssr.swift.bdsssr.ssr[-1]
    elif sys == SYS_GAL:
        tow = codec_getbitu(buff, i, 20); i+=20
        realtimegal = timeFormat.galTime()
        towgal = realtimegal.adjweek(tow)
        ssrtime = towgal.datetime
        if towgal.GPSSOW in ssr.swift.galssr.epoch:
            #tindex = ssr.swift.galssr.epoch.index(tow)
            tindex = ssr.swift.galssr.epoch.index(towgal.GPSSOW)
            ssrlist = ssr.swift.galssr.ssr[tindex]
        else:
            #ssr.swift.galssr.epoch.append(tow)
            ssr.swift.galssr.epoch.append(towgal.GPSSOW)
            ssr.swift.galssr.ssr.append(ssrData.swift_ssr_sys(SYS_GAL))
            ssrlist = ssr.swift.galssr.ssr[-1]
    elif sys == SYS_GPS:
        tow = codec_getbitu(buff, i, 20); i+=20
        realtimegps = timeFormat.gpsTime()
        towgps = realtimegps.adjweek(tow)
        ssrtime = towgps.datetime
        if tow in ssr.swift.gpsssr.epoch:
            tindex = ssr.swift.gpsssr.epoch.index(tow)
            ssrlist = ssr.swift.gpsssr.ssr[tindex]
        else:
            ssr.swift.gpsssr.epoch.append(tow)
            ssr.swift.gpsssr.ssr.append(ssrData.swift_ssr_sys(SYS_GPS))
            ssrlist = ssr.swift.gpsssr.ssr[-1]
    udi = codec_getbitu(buff, i, 4); i+=4
    sync = codec_getbitu(buff, i, 1); i+=1
    iod = codec_getbitu(buff, i, 4); i+=4    
    provid = codec_getbitu(buff, i, 16); i+=16
    solid = codec_getbitu(buff, i, 4); i+=4
    if sys == SYS_QZS:
        nsat = codec_getbitu(buff, i, 4); i+=4
    else:
        nsat = codec_getbitu(buff, i, 6); i+=6
    udint = ssrudint[udi]
    #
    if nsat <0:
        print("Warning in decoderaw ssr7_ex")
        return
    if sys == SYS_GPS:
        np=6;offp=0;ssrid=0
    # elif sys == SYS_GLO:
    #     np=5;offp=0
    elif sys == SYS_GAL:
        np=6;offp=0;ssrid=3
    elif sys == SYS_BDS:
        np=6; offp=0;ssrid=5
        
    if rtcmtype==0:
        nm=6; ns=2
    elif rtcmtype ==1:
        nm=5; ns=1
    for j in range(0,nsat):
        if (i+5+17+np) <= (rtcm.len)*8:
            prn = codec_getbitu(buff, i, np)+offp; i+=np
            nbias = codec_getbitu(buff, i, 5); i+=5
            if rtcmtype == 0:
                yaw_ang = codec_getbitu(buff, i, 9); i+=9
                yaw_rate = codec_getbits(buff, i, 8); i+=8
            else:
                yaw_ang = codec_getbitu(buff, i, 9)*0.00360625; i+=9
                yaw_rate = codec_getbits(buff, i, 8)*0.0001220703125; i+=8
            for k in range(0,nbias):
                mode = codec_getbitu(buff, i, nm); i+=nm
                swl = codec_getbitu(buff, i, ns); i+=ns
                sdc = codec_getbitu(buff, i, 4); i+=4
                bias = codec_getbits(buff, i, 20); i+=20
                if rtcmtype==0:
                    std = codec_getbitu(buff, i, 17); i+=17
                    code = codec_obs2code(cgcodec_mm_sig_ssr[mode] , None)
                else:
                    std = 0
                    if sys==SYS_GPS:
                        code = codec_obs2code(cgcodec_mm_sig_ssr_gps_swift[mode], None)
                    elif sys==SYS_GAL:
                        code = codec_obs2code(cgcodec_mm_sig_ssr_gal_swift[mode] , None)
                    elif sys==SYS_BDS:
                        code = codec_obs2code(cgcodec_mm_sig_ssr_bds_swift[mode] , None)
                if (code > CGCODEC_CODE_NONE) and (code < MAXCODE):
                    pbias[code]=bias*0.0001
                    stdpb[code]=std*0.0001
            ssr7prndata = deepcopy(ssrlist.sats[j])
            ssr7prndata.sys_id = ssrid
            ssr7prndata.svid = prn
            ssr7prndata.t0[5] = ssrtime
            ssr7prndata.udi[5] = udint
            ssr7prndata.iod[5] =iod
            ssr7prndata.yaw_ang = yaw_ang/256*180
            ssr7prndata.yaw_rate = yaw_rate/8192*180
            for k in range(0,MAXCODE):
                if pbias[k] != 0:
                    curFreq = codec_get_pbias_freq(sys, k)
                    if curFreq >= 0 and curFreq < CGCODEC_NFREQ:
                        ssr7prndata.pbias[curFreq] = pbias[k]
                        ssr7prndata.stdpb[curFreq] = stdpb[k]
            ssrlist.sats[j] = ssr7prndata 
    return
