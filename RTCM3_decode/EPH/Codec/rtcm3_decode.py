# -*- coding: utf-8 -*-
"""
2022Jun14: separate buff and ssr/eph in input

Env: Windows10/Anaconda3/Python 3.8.8
Description: to read/decode type/message in rtcm3
Updated on Thursday Nov 19 12:15:25 2021
@author: Zoe_Chen
Ref:RTKlib/src/rtcm3.c 
    RTCM Standard 10403.3.pdf
     ssr_1_gal_qzss_sbas_bds_v08u.pdf(ssr1v08u)
     RTCM-SSR-Python-Demonstrator/rtcm_decoder.py
        List of RTCM-SSR messages considered:
        - 1019: GPS ephemeris
        - 1020: GLONASS ephemeris
        - 1042: Beidou ephemeris
        - 1044: QZSS ephemeris
        - 1045: Galileo F/NAV ephemeris
        - 1046: Galileo I/NAV ephemeris
        - 1057: GPS Orbit message
        - 1058: GPS Clock message
        - 1059: GPS Code bias
        - 1060: GPS combined orbit and clock
        - 1061: GPS URA message
        - 1265: GPS Phase Bias
        - 1063: GLONASS Orbit message
        - 1064: GLONASS Clock message
        - 1065: GLONASS Code bias
        - 1066: GLONASS combined orbit and clock
        - 1067: GLONASS URA message
        - 1266: GLONASS Phase Bias
        - 1240: Galileo Orbit Message
        - 1241: Galileo Clock Message
        - 1242: Galileo Code bias
        - 1243: Galileo combined orbit and clock
        - 1244: Galileo URA message
        - 1245: Galileo High Rate Clock message
        - 1267: Galileo Phase Bias 
        - 1246: QZSS Orbit message
        - 1247: QZSS Clock message
        - 1248: QZSS Code bias
        - 1249: QZSS combined orbit and clock
        - 1250: QZSS URA message
        - 1251: QZSS High Rate Clock message
        - 1268: QZSS Phase Bias
        - 1258: BDS Orbit message
        - 1259: BDS Clock message
        - 1260: BDS Code bias
        - 1261: BDS combined orbit and clock
        - 1262: BDS URA message
        - 1263: BDS High Rate Clock message
        - 1270: BDS Phase Bias
        - 1264: SSR VTEC

"""
import sys
sys.dont_write_bytecode = True
import bitstruct
from Codec.getbitu import getbitu
from copy import deepcopy
from libmain.TimeTrans.timeFormat import gpsTime,gloTime,bdsTime,galTime
from libmain.GNSS.sysNames import sysNames
from SSR.ssrData import HEADS
from com import SYS_GPS,SYS_GLO,SYS_GAL,SYS_BDS
from EPH.ephData import GPSEPH,BDSEPH,GLOEPH,GALFEPH,GALIEPH
from SSR.ssrData import SSRSAT
#from EPH.ephData import EPHSAT
#from GNSS import GPS,GAL,GLO,BDS




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

# decode SSR 1,4 message header
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




def decode_ssr1(rtcm,sys,ssrin):
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


def decode_ssr2(rtcm,sys,ssrin):
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
    

def decode_ssr3(rtcm,sys,ssrin):
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


def decode_ssr4(rtcm,sys,ssrin):
    """
    Message Type 1060: SSR GPS combined Orbit and Clock Correction
    # Table 3.5-44 in ref RTCM3
    # GLONASS 1066
    """
    buff = rtcm.buff
    #ssr0 = SSRSAT()
    msgtype = getbitu(buff,24,'u12')    
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
    

class signalID:
    """
    Traking mode update to "ssr_1_gal_qzss_sbas_bds_v08u" document
    # Table 3b
    """
    def signals(GNSS, S_TMI):
        if GNSS == 'GPS':
            sig_list = ['1C', '1P', '1W', '', '', '2C', '2D', '2S', '2L', '2X',
                        '2P', '2W', '', '', '5I', '5Q', '5X', '1S', '1L', '1X']
            signal = sig_list[S_TMI]

        elif GNSS == 'GLONASS':
            sig_list = ['1C', '1P', '2C', '2P', '1A', '1B', '1X',
                        '2A', '2B', '2X', '3I', '3Q', '3X']
            signal = sig_list[S_TMI]

        elif GNSS == 'Galileo':
            sig_list = ['1A', '1B', '1C', '1X', '1Z', '5I', '5Q', '5X', '7I',
                        '7Q', '7X', '8I', '8Q', '8X', '6A', '6B', '6C', '6X',
                      #  '6Z']
                        '6Z','','','','','','','','','','','','']
            signal = sig_list[S_TMI]

        elif GNSS == 'QZSS':
            sig_list = ['1C', '1S', '1L', '2S', '2L', '2X', '5I', '5Q', '5X',
                        '6S', 'SL', 'SX', '1X', '1Z', '5D', '5P', '5Z', '6E',
                        '6Z']
            signal = sig_list[S_TMI]

        elif GNSS == 'BDS':
            sig_list = ['2I', '2Q', '2X', '6I', '6Q', '6X', '7I', '7Q', '7X',
            #            '1D', '1P', '1X', '5D', '5P', '5X']
            # BDS track =28?
                         '1D', '1P', '1X', '5D', '5P', '5X','','','','','',
                         '','','','','','','','','','','','']
            signal = sig_list[S_TMI]

        elif GNSS == 'SBAS':
            sig_list = ['1C', '5I', '5Q', '5X']
            signal = sig_list[S_TMI]

        return signal


def decode_type1019(rtcm,ephin):
    """ GPS Ephemeris Message Type 1019"""
    # See 2.4.4.1 in gpssps.pdf
    message = rtcm.buff
    ephgps = GPSEPH()
    #ephgps = ephin
    try:
        # Definition of the bits of the message
        content =  ('u24u12u6u10u4s2s14u8u16s8s16s22u10s16s16s32s16u32s16u32u' + 
                     '16s16s32s16s32s16s32s24s8u6s1s1')
        unpack_bits = bitstruct.unpack(content, message)
        
        # Define constants
        pie = 3.14159265358979323846  # 20-decimal places
        # **************************** Parameters *************************** #
        # unpack_bits[0] is /preamble/0/length ignore
        #msg_type = unpack_bits[1]
        # GPS satellite ID
        IDnum = unpack_bits[2]
        #ephgps = ephin.eph[IDnum]
        
        # formatting
        sat_ID = str(IDnum)
        
        
        ephgps.gnss = 'GPS'
        ephgps.gnss_short = 'G'
        if len(sat_ID) < 2:
            ephgps.sat_id = 'G0' + sat_ID
        else:
            ephgps.sat_id = 'G' + sat_ID
        
        # GPS week number. Range: 0-1023
        week = unpack_bits[3]
        ephgps.week = week
        ephgps.gpsweek = week
        #ephgps.week     = gpsTime().adjweek(ephgps.toe)
        #= Note1: GPS week rollover problem... week number went from 1023 to 1024
        # August 21 to August 22, 1999, when GPS Week 1023. Need to add 1024
        # on on the night of April 6 to April 7, 2019. Need to add 2048.
        # The computation below is valid till next week roll over
        # Compute doy of first week roll-over
        
        
         
        # dy1 = date_to_doy(1999, 8, 21)
        # dy2 = date_to_doy(2019, 4, 6)
        # utc = datetime.datetime.utcnow()
        # year = utc.year
        # mon = utc.month
        # day = utc.day
        # doy = date_to_doy(year,mon,day)
        # [year, month, dom] = doy_to_date(year, doy)
        
        # if ((year <= 1999) & (doy <= dy1)):
        #     ephgps.week = week
        # elif ((year == 1999) & (doy > dy1)):
        #     ephgps.week = week + 1024
        # elif (( year > 1999) & (year < 2019)):
        #      ephgps.week = week + 1024 
        # elif ((year == 2019) & (doy <= dy2)):
        #     ephgps.week = week + 1024
        # else:
        #     ephgps.week = week + 2048
        
        # GPS SV Accuracy 
        ephgps.ura = unpack_bits[4]
        
        # GPS CODE on L2. 00 = reserved. 01 = P code. 10 = C/A code. 11 = L2C
        ephgps.code_L2 = unpack_bits[5]
        
        # Rate of Inclination Angle
        ephgps.idot = unpack_bits[6] * pow(2, -43) * pie
        
        # Issue of Data (Ephemeris)
        ephgps.iode = unpack_bits[7]
        
        # GPS toc
        ephgps.toc = unpack_bits[8] * pow(2, 4)
        
        # GPS af2
        ephgps.af2 = unpack_bits[9] * pow(2, -55)
        
        # GPS af1
        ephgps.af1 = unpack_bits[10] * pow(2, -43)
        
        # GPS af0
        ephgps.af0 = unpack_bits[11] * pow(2, -31)
        
        # GPS IODC
        ephgps.iodc = unpack_bits[12]
        
        # Amplitude of the Sine Harmonic Correction Term to the Orbit Radius
        ephgps.crs = unpack_bits[13] * pow(2, -5)
        
        # Mean Motion Difference from Computed Value
        ephgps.dn = unpack_bits[14] * pow(2, -43) * pie
        
        # Mean Anomaly at Reference Time
        ephgps.m0 = unpack_bits[15] * pow(2, -31) * pie
        
        # GPS cuc
        ephgps.cuc = unpack_bits[16] * pow(2, -29)
        
        # GPS eccentricity (e)
        ephgps.ecc = unpack_bits[17] * pow(2, -33)
        
        # Amplitude of the Sine Harmonic Correction Term
        # to the Argument of Latitude
        ephgps.cus = unpack_bits[18] * pow(2, -29)
        
        # Square Root of the Semi-Major Axis
        ephgps.root_a = unpack_bits[19] * pow(2, -19)
        
        # Reference Time Ephemeris
        ephgps.toe = unpack_bits[20] * pow(2, 4)
        ephgps.gpstoe = ephgps.toe
        #= Note 2: See Table2-15 in gpssps.pdf
        #  tk = t - toe *
        #  t is GPS system time at time of transmission, i.e., 
        #  GPS time corrected for transit time
        #  (range/speed of light). Furthermore, t
        #  shall be the actual total time difference between the 
        #  time t and the epoch time toe,and must account for 
        #  beginning or end of week crossovers.That is, if t
        #  is greater than 302,400 seconds, subtract 604,800 seconds from tk.
        #  If t is less tk than -302,400 seconds, add 604,800 seconds to tk.
        # cttime = gpsTime()
        # tt = cttime - gpsTime([week,ephgps.toe,cttime.Rollover])
        # #ephgps.week     = gpsTime().adjweek(ephgps.toe)
        # if(tt.total_seconds() < -302400 ):
        #     ephgps.week += 1
        # elif(tt.total_seconds() >= 302400):
        #     ephgps.week -= 1
        # ephgps.fullweek = gpsTime().fullweek(week)
        # Amplitude of the Cosine Harmonic Correction Term 
        # to the Angle of Inclination
        ephgps.cic = unpack_bits[21] * pow(2, -29)
        
        # Longitude of Ascending Node of Orbit Plane at Weekly Epoch (omega_0)
        ephgps.omega_0 = unpack_bits[22] * pow(2, -31) * pie
        
        # Amplitude of the Sine Harmonic Correction Term 
        # to the Angle of Inclination
        ephgps.cis = unpack_bits[23] * pow(2, -29)
    
        # Inclination Angle at Reference Time
        ephgps.i0 = unpack_bits[24] * pow(2, -31) * pie
        
        # Amplitude of the Cosine Harmonic Correction Term to the Orbit Radius
        ephgps.crc = unpack_bits[25] * pow(2, -5)
        
        # GPS argument of perigee (w) 
        ephgps.omega = unpack_bits[26] * pow(2, -31) * pie
        
        # Rate of Right Ascension
        ephgps.omega_dot = unpack_bits[27] * pow(2, -43) * pie
        
        # GPS t_GD
        ephgps.tgd = unpack_bits[28] * pow(2, -31)
        
        # GPS SV health
        ephgps.health = unpack_bits[29]
        
        # GPS L2 P data flag. L2P-code nav data: 0 = ON; 1 = OFF
        ephgps.L2P = unpack_bits[30]
        
        # GPS fit interval
        # 0: Curve fit interval is 4 hours, 1: > 4 hours
        ephgps.interval = unpack_bits[31]
        ephin.ephgps[IDnum-1] = deepcopy(ephgps)
    except:
        print('Warning in decoding_type1019')
        return -1
    return 2
 
def decode_type1020(rtcm,ephin):    
#class glo_ephemeris:
    """ GLONASS Satellite Ephemeris data Message Type 1020 """
    #def __init__(self, message):
    message = rtcm.buff
    ephglo = GLOEPH()
    #print('rtcm', len(rtcm.buff))
    #(print('1'))
    try:
        # Definition of the bits of the header of the message
        header1 = 'u24u12u6u5u1u1u2u5u6u1u1u1u7'
        header2 = 'u1u23u1u26u1u4u1u23u1u26u1u4u1u23u1u26u1u4'
        header3 = 'u1u1u10u2u1u1u21u1u4u5u1u4u11u2u1u11u1u31u5u1u21u1u7'
            
        header = header1 + header2 + header3
        # Unpack the bits of the header    
        unpack_bits = bitstruct.unpack(header, message)           
        #print('2')
        
        ephglo.gnss = 'GLONASS'
        ephglo.gnss_short = 'R'
        # **************************** Parameters *************************** #
        
        # unpack_bits[1] is the type, hence it is not considered here
            
        # GLONASS Satellite ID #u6
        IDnum = unpack_bits[2]
        if unpack_bits[2] < 10:
            GLO  = 'R' + '0' + f'{unpack_bits[2]}'
        else:
            GLO  = 'R' + f'{unpack_bits[2]}'
        ephglo.sat_id = GLO
        
        # u5 GLONASS sate freq chan numb [-7...13]
        ephglo.freq = unpack_bits[3] -7
        
        # GLONASS almanac healthy availability u1
        # ephglo.bn   = unpack_bits[5]
        # # GLONASS almanach healthy u1
        # if ephglo.bn == 0:
        #     ephglo.cn = 'n/a'
        # elif ephglo.bn == 1:
        #     ephglo.cn   = unpack_bits[4] 
        ephglo.cn = unpack_bits[4]
        ephglo.bn   = unpack_bits[5]
            
        
        # GLONASS P1 u2u5
        ephglo.p1   = unpack_bits[6]
            
        # GLONASS tk, first 5 bits: integer number of hours, next six bits
        # integer number of minutes, LSb number of thirty seconds interval
        tk_h = unpack_bits[7]
        tk_m = unpack_bits[8]
        tk_s = unpack_bits[9]
        #= THE Beginning of GLO subframe within the current day
        #= local time second of day hh:mm:ss
        ephglo.tk   = tk_h * 3600 + tk_m * 60 + tk_s * 30
        
        # GLONASS MSb of Bn word
        ephglo.msb_bn = unpack_bits[10]
        ephglo.health  = ephglo.msb_bn    
        # GLONASS P2
        ephglo.p2   = unpack_bits[11]
            
        # GLONASS tb Time to which GLO navigation data are referenced
        # Printed in [s] //IODE
        #= ICD v5.1: an index of a time interval within current day according
        #            to UTC(SU) + 03hours 00min
        ephglo.tb = unpack_bits[12]
        #= tb * 15 * 60  # [s]  # localtime second of day
        
        ephglo.iode = ephglo.tb  
 

        # GLONASS xn(tb), first derivative
        if unpack_bits[13] == 0:
            d_xn =  unpack_bits[14] * 2 ** (-20)
        else:
            d_xn = -unpack_bits[14] * 2 ** (-20)
        ephglo.dxn = d_xn
        
        # GLONASS xn(tb)
        if unpack_bits[15] == 0:
            xn =  unpack_bits[16] * 2 ** (-11)
        else:
            xn = -unpack_bits[16] * 2 ** (-11)            
        ephglo.xn = xn
        
        # GLONASS xn(tb)
        if unpack_bits[17] == 0:
            d2_xn =  unpack_bits[18] * 2 ** (-30)
        else:
            d2_xn = -unpack_bits[18] * 2 ** (-30)
        ephglo.ddxn = d2_xn
        
        # GLONASS dyn(tb)
        if unpack_bits[19] == 0:
            d_yn  =  unpack_bits[20] * 2 ** (-20)
        else:
            d_yn  = -unpack_bits[20] * 2 ** (-20)  
        ephglo.dyn = d_yn
        
        # GLONASS yn(tb)
        if unpack_bits[21] == 0:
            yn  =  unpack_bits[22] * 2 ** (-11)
        else:
            yn  = -unpack_bits[22] * 2 ** (-11)  
        ephglo.yn = yn   
        
        # GLONASS ddyn(tb)
        if unpack_bits[23] == 0:
            d2_yn  =  unpack_bits[24] * 2 ** (-30)
        else:
            d2_yn  = -unpack_bits[24] * 2 ** (-30)
        ephglo.ddyn = d2_yn
        
        # GLONASS dzn(tb)
        if unpack_bits[25] == 0:
            d_zn  =  unpack_bits[26] * 2 ** (-20)
        else:
            d_zn  = -unpack_bits[26] * 2 ** (-20)  
        ephglo.dzn = d_zn
        
        # GLONASS zn(tb)
        if unpack_bits[27] == 0:
            zn  =  unpack_bits[28] * 2 ** (-11)
        else:
            zn  = -unpack_bits[28] * 2 ** (-11)  
        ephglo.zn = zn
        
        # GLONASS ddzn(tb)
        if unpack_bits[29] == 0:
            d2_zn  =  unpack_bits[30] * 2 ** (-30)
        else:
            d2_zn  = -unpack_bits[30] * 2 ** (-30)
        ephglo.ddzn = d2_zn
        
        # GLONASS P3
        ephglo.p3   = unpack_bits[31]
        
        # GLONASS gamma(tb)
        if unpack_bits[32] == 0:
            ephglo.gamma  =  unpack_bits[33] * 2 ** (-40)
        else:
            ephglo.gamma  = -unpack_bits[33] * 2 ** (-40)
        
        # GLONASS-M P, Range 0-3
        ephglo.p    = unpack_bits[34]
        
        # GLONASS-M ln third string
        ephglo.ln_t   = unpack_bits[35]

        # GLONASS tau_n
        if unpack_bits[36] == 0:
            ephglo.tau  =  unpack_bits[37] * 2 ** (-30)
        else:
            ephglo.tau  = -unpack_bits[37] * 2 ** (-30)
            
        # GLONASS dtau_n
        if unpack_bits[38] == 0:
            ephglo.dtau  =  unpack_bits[39] * 2 ** (-30)
        else:
            ephglo.dtau  = -unpack_bits[39] * 2 ** (-30)
        
        # GLONASS En age,DF126
        ephglo.en   =  unpack_bits[40]
        
        # GLONASS P4
        ephglo.p4 = unpack_bits[41]
            
        # GLONASS-M Ft
        ephglo.ft   = unpack_bits[42]
        
        # GLONASS-M Nt 
        #= calendar number of day within four-year period
        ephglo.nt = unpack_bits[43]

        # GLONASS-M M
        ephglo.m   = unpack_bits[44]
        
        # GLONASS Availability additional data
        ephglo.ava   = unpack_bits[45]
        
        # GLONASS N_A GLO calendar number of day within the four-year period to TC
        ephglo.na   = unpack_bits[46]
            
        # GLONASS tau_c
        if ephglo.ava == 0:
            ephglo.tau_c = 0
        
        else:
            if unpack_bits[47] == 0:
                ephglo.tau_c  =  unpack_bits[48] * 2 ** (-31)
            else:
                ephglo.tau_c  = -unpack_bits[48] * 2 ** (-31)

        # GLONASS-M N4 four year interval number starting from 1996
        ephglo.n4 = unpack_bits[49]
        
        # GLONASS-M tau_gps
        # correction to GPS system time relative to GLO sys time
        if unpack_bits[50] == 0:
            ephglo.tau_gps  =  unpack_bits[51] * 2 ** (-20)
        else:
            ephglo.tau_gps  = -unpack_bits[51] * 2 ** (-20)
            
        # GLONASS-M ln fifth string
        ephglo.ln_f   = unpack_bits[52]
        
        #ephglo.toe = ephglo.tb * 900 - 10800 # lt to utc
        ephglo.toe = ephglo.tb * 900    # lt
        # period, dop, sod

        gpst = gloTime([ephglo.n4,ephglo.nt,ephglo.tk]).GLO2GPS()
 
        ephglo.gpstoe = gpst.GPSSOW
        ephglo.gpsweek = gpst.GPSWeek

        ephin.ephglo[IDnum-1] = deepcopy(ephglo)
    except:
        print('GLO', len(ephin.ephglo))
        print('Warning in decoding_type1020')
        return -1
    return 2
        
        
def decode_type1045(rtcm,ephin):
#class gal_ephemeris_fnav:
    """ GALILEO Satellite Ephemeris F/NAV data Message Type 1045"""
    #def __init__(self, message):
    message = rtcm.buff
    ephgalF = GALFEPH()
    try:
        # Define constants
        pie = 3.1415926535898
        # Definition of the bits of the message
        contents = 'u12u6u12u10u8s14u14s6s21s31s16s16s32s16u32s16u32u14s16' + \
                   's32s16s32s16s32s24s10u2u1u7'
        unpack_bits = bitstruct.unpack(contents, message)
        ephgalF.gnss = 'Galileo F/NAV'
        ephgalF.gnss_short = 'E'
    
        # **************************** Parameters *************************** #
        
        # unpack_bits[0] is the message number, hence it is not considered here
        
        # Galileo satellite ID
        IDnum = unpack_bits[1]
        # formatting
        sat_ID = str(IDnum)
        if len(sat_ID) < 2:
            ephgalF.sat_id = 'E0' + sat_ID
        else:
            ephgalF.sat_id = 'E' + sat_ID
        
        # Galileo week number
        ephgalF.week = unpack_bits[2]
        
        # Galileo IODnav 
        ephgalF.iod = unpack_bits[3]
        
        # Galileo SV SISA
        ephgalF.sisa = unpack_bits[4]
        
        # Rate of Inclination Angle
        ephgalF.idot = unpack_bits[5] * pow(2, -43) * pie
               
        # Galileo toc
        ephgalF.toc = unpack_bits[6] * 60
        
        # Galileo af2
        ephgalF.af_two = unpack_bits[7] * pow(2, -59)
        
        # Galileo af1
        ephgalF.af_one = unpack_bits[8] * pow(2, -46)
        
        # Galileo af0
        ephgalF.af_zero = unpack_bits[9] * pow(2, -34)
            
        # Amplitude of the Sine Harmonic Correction Term to the Orbit Radius
        ephgalF.crs = unpack_bits[10] * pow(2, -5)
        
        # Mean Motion Difference from Computed Value
        ephgalF.dn = unpack_bits[11] * pow(2, -43) * pie
        
        # Mean Anomaly at Reference Time
        ephgalF.m0 = unpack_bits[12] * pow(2, -31) * pie
        
        # Galileo cuc
        ephgalF.cuc = unpack_bits[13] * pow(2, -29)
        
        # Galileo eccentricity (e)
        ephgalF.ecc = unpack_bits[14] * pow(2, -33)
        
        # Amplitude of the Sine Harmonic Correction Term 
        # to the Argument of Latitude
        ephgalF.cus = unpack_bits[15] * pow(2, -29)
        
        # Square Root of the Semi-Major Axis
        ephgalF.root_a = unpack_bits[16] * pow(2, -19)
        
        # Reference Time Ephemeris
        ephgalF.toe = unpack_bits[17] * 60
        
        # Amplitude of the Cosine Harmonic Correction Term 
        # to the Angle of Inclination
        ephgalF.cic = unpack_bits[18] * pow(2, -29)
        
        # Longitude of Ascending Node of Orbit Plane at Weekly Epoch (omega_0)
        ephgalF.omega_0 = unpack_bits[19] * pow(2, -31) * pie
        
        # Amplitude of the Sine Harmonic Correction Term 
        # to the Angle of Inclination
        ephgalF.cis = unpack_bits[20] * pow(2, -29)
    
        # Inclination Angle at Reference Time
        ephgalF.i0 = unpack_bits[21] * pow(2, -31) * pie
        
        # Amplitude of the Cosine Harmonic Correction Term to the Orbit Radius
        ephgalF.crc = unpack_bits[22] * pow(2, -5)
        
        # Galileo argument of perigee (w) 
        ephgalF.omega = unpack_bits[23] * pow(2, -31) * pie
        
        # Rate of Right Ascension
        ephgalF.omega_dot = unpack_bits[24] * pow(2, -43) * pie
        
        # Galileo BGD E1/E5 broadcast group delay
        ephgalF.bgd_a = unpack_bits[25] * pow(2, -32)
        ephgalF.bgd_b = 0
        
        # Galileo SV health, 0 is ok
        ephgalF.health = unpack_bits[26]
        
        # Galileo Nav Data Validity status
        ephgalF.validity = unpack_bits[27]
        ephin.ephgalF[IDnum-1] = deepcopy(ephgalF)
    except:
        print('Warning in decoding_type1045')
        return -1
    return 2
        
        
def decode_type1046(rtcm,ephin):
#class gal_ephemeris_inav:
    """GALILEO Satellite Ephemeris I/NAVdata Message Type 1046"""
    message = rtcm.buff
    ephgalI = GALIEPH()
    #def __init__(self, message):
        # Define constants
    try:
        pie = 3.1415926535898
        # Definition of the bits of the message
        contents = 'u24u12u6u12u10u8s14u14s6s21s31s16s16s32s16u32s16u32u14s16' + \
                   's32s16s32s16s32s24s10s10u2u1u2u1u2'
        
        unpack_bits = bitstruct.unpack(contents, message)
        
        ephgalI.gnss = 'Galileo I/NAV'
        ephgalI.gnss_short = 'E'
        
        # **************************** Parameters *************************** #
        
        # unpack_bits[1] is the message number, hence it is not considered here
        
        # Galileo satellite ID
        IDnum = unpack_bits[2]
        # formatting
        sat_ID = str(IDnum)
        if len(sat_ID) < 2:
            ephgalI.sat_id = 'E0' + sat_ID
        else:
            ephgalI.sat_id = 'E' + sat_ID
        
        # Galileo week number
        ephgalI.week = unpack_bits[3]
       
        # Galileo IODnav 
        ephgalI.iode = unpack_bits[4]
        
        # Galileo SV SISA
        ephgalI.sisa = unpack_bits[5]
        
        # Rate of Inclination Angle
        ephgalI.idot = unpack_bits[6] * pow(2, -43) * pie
               
        # Galileo toc
        ephgalI.toc = unpack_bits[7] * 60
        
        # Galileo af2
        ephgalI.af2 = unpack_bits[8] * pow(2, -59)        
        # Galileo af1
        ephgalI.af1 = unpack_bits[9] * pow(2, -46)
        # Galileo af0
        ephgalI.af0 = unpack_bits[10] * pow(2, -34)
            
        # Amplitude of the Sine Harmonic Correction Term to the Orbit Radius
        ephgalI.crs = unpack_bits[11] * pow(2, -5)
        
        # Mean Motion Difference from Computed Value
        ephgalI.dn = unpack_bits[12] * pow(2, -43) * pie
        
        # Mean Anomaly at Reference Time
        ephgalI.m0 = unpack_bits[13] * pow(2, -31) * pie
        
        # Galileo cuc
        ephgalI.cuc = unpack_bits[14] * pow(2, -29)
        
        # Galileo eccentricity (e)
        ephgalI.ecc = unpack_bits[15] * pow(2, -33)
        
        # Amplitude of the Sine Harmonic Correction Term 
        # to the Argument of Latitude
        ephgalI.cus = unpack_bits[16] * pow(2, -29)
        
        # Square Root of the Semi-Major Axis
        ephgalI.root_a = unpack_bits[17] * pow(2, -19)
        
        # Reference Time Ephemeris
        ephgalI.toe = unpack_bits[18] * 60
        
        # Amplitude of the Cosine Harmonic Correction Term 
        # to the Angle of Inclination
        ephgalI.cic = unpack_bits[19] * pow(2, -29)
        
        # Longitude of Ascending Node of Orbit Plane at Weekly Epoch (omega_0)
        ephgalI.omega_0 = unpack_bits[20] * pow(2, -31) * pie
        
        # Amplitude of the Sine Harmonic Correction Term 
        # to the Angle of Inclination
        ephgalI.cis = unpack_bits[21] * pow(2, -29)
    
        # Inclination Angle at Reference Time
        ephgalI.i0 = unpack_bits[22] * pow(2, -31) * pie
        
        # Amplitude of the Cosine Harmonic Correction Term to the Orbit Radius
        ephgalI.crc = unpack_bits[23] * pow(2, -5)
        
        # Galileo argument of perigee (w) 
        ephgalI.omega = unpack_bits[24] * pow(2, -31) * pie
        
        # Rate of Right Ascension
        ephgalI.omega_dot = unpack_bits[25] * pow(2, -43) * pie
        
        # Galileo BGD E5a/E1 broadcast group delay
        ephgalI.bgd_a = unpack_bits[26] * pow(2, -32)
        
        # Galileo BGD E5b/E1 broadcast group delay
        ephgalI.bgd_b = unpack_bits[27] * pow(2, -32)        
        
        # E1-B Health 
        ephgalI.health = unpack_bits[28] 
        
        # E1-B validity 
        ephgalI.e1b_v = unpack_bits[29]
        
        
        t0 = galTime([ephgalI.week,ephgalI.toe,galTime().Rollover]).GAL2GPS()
        ephgalI.gpstoe =  t0.GPSSOW
        ephgalI.gpsweek = t0.GPSWeek
        ephin.ephgalI[IDnum-1] = deepcopy(ephgalI)
    except:
        print('Warning in decoding_type1046')
        return -1
    return 2
        
def decode_type1042(rtcm,ephin):        
    #class bds_ephemeris:
    """ Beidou Satellite Ephemeris Type 1042 """
    #def __init__(self, message):
    message = rtcm.buff
    ephbds = BDSEPH()
    try:    
        # Define constants
        pie = 3.1415926535898
        # Definition of the bits of the message
        # contents = 'u12u6u13u4s14u5u17s11s22s24u5s18s16s32s18u32s18u32u17' + \
        #            's18s32s18s32s18s32s24s10s10u1'
        contents = 'u24u12u6u13u4s14u5u17s11s22s24u5s18s16s32s18u32s18u32u17' + \
                    's18s32s18s32s18s32s24s10s10u1'
        
        unpack_bits = bitstruct.unpack(contents, message)
        
        ephbds.gnss = 'BDS'
        ephbds.gnss_short = 'C'
        
        # **************************** Parameters *************************** #
        
        # unpack_bits[1] is the message number, hence it is not considered here
        
        # Beidou satellite ID
        IDnum = unpack_bits[2]
        ephbds.prn = IDnum
        # formatting
        sat_ID = str(IDnum)
        if len(sat_ID) < 2:
            ephbds.sat_id = 'C0' + sat_ID
        else:
            ephbds.sat_id = 'C' + sat_ID
        
        # Beidou week number. 
        ephbds.week    = unpack_bits[3]
        #= fullweek (week + rollover *1024)
        #ephbds.week = bdsTime().adjBDSweek(ephbds.week)
        # Beidou SV URAI 
        ephbds.sva    = unpack_bits[4]

        # Rate of Inclination Angle
        ephbds.idot    = unpack_bits[5] * pow(2, -43) * pie
        
        # Beidou AODE/IODE
        ephbds.aode    = unpack_bits[6]
        ephbds.iode = int(ephbds.aode /720 % 240)
        # Beidou toc
        ephbds.toc     = unpack_bits[7] * 8
        
        # Beidou af2
        ephbds.af2  = unpack_bits[8] * pow(2, -66)
        
        # Beidou af1
        ephbds.af1  = unpack_bits[9] * pow(2, -50)
        
        # Beidou af0
        ephbds.af0 = unpack_bits[10] * pow(2, -33)
        
        # Beidou AODC/IODC
        ephbds.iodc    = unpack_bits[11]
        
        # Amplitude of the Sine Harmonic Correction Term to the Orbit Radius
        ephbds.crs     = unpack_bits[12] * pow(2,  -6)
        
        # Mean Motion Difference from Computed Value
        ephbds.dn      = unpack_bits[13] * pow(2, -43) * pie
        
        # Mean Anomaly at Reference Time
        ephbds.m0      = unpack_bits[14] * pow(2, -31) * pie
        
        # cuc
        ephbds.cuc     = unpack_bits[15] * pow(2, -31)
        
        # eccentricity (e)
        ephbds.ecc     = unpack_bits[16] * pow(2, -33)
        
        # Amplitude of the Sine Harmonic Correction Term 
        # to the Argument of Latitude
        ephbds.cus     = unpack_bits[17] * pow(2, -31)
        
        # Square Root of the Semi-Major Axis
        ephbds.root_a  = unpack_bits[18] * pow(2, -19)
        
        # Reference Time Ephemeris
        ephbds.toe = unpack_bits[19] * 8
        
        # Amplitude of the Cosine Harmonic Correction Term 
        # to the Angle of Inclination
        ephbds.cic = unpack_bits[20] * pow(2, -31)
        
        # Longitude of Ascending Node of Orbit Plane at Weekly Epoch (omega_0)
        ephbds.omega_0 = unpack_bits[21] * pow(2, -31) * pie
        
        # Amplitude of the Sine Harmonic Correction Term
        # to the Angle of Inclination
        ephbds.cis = unpack_bits[22] * pow(2, -31)
    
        # Inclination Angle at Reference Time
        ephbds.i0 = unpack_bits[23] * pow(2, -31) * pie
        
        # Amplitude of the Cosine Harmonic Correction Term to the Orbit Radius
        ephbds.crc = unpack_bits[24] * pow(2, -6)
        
        #  argument of perigee (w) 
        ephbds.omega = unpack_bits[25] * pow(2, -31) * pie
        
        # Rate of Right Ascension
        ephbds.omega_dot = unpack_bits[26] * pow(2, -43) * pie
        
        # Beidou TGD1 group delay differential
        ephbds.tgd1 = unpack_bits[27] * 0.1 * 1e-9        
        
        # Beidou TGD2 group delay differential
        ephbds.tgd2 = unpack_bits[28] * 0.1 * 1e-9     
        
        # BDS SV Health
        ephbds.health = unpack_bits[29]
        
        #= Ref: RTKLIB_2.4.3\src\rtcm3.c\type1042\eph.week
        #= BDS -> gps
        # bds toe to gps toe
        ctbtime = bdsTime()
        #ctgtime = gpsTime()
        t0 = bdsTime([ephbds.week,ephbds.toe,ctbtime.Rollover]).BDS2GPS()
        # tt = ctgtime - t0
        # ephbds.gpsweek = t0.GPSWeek
        # if(tt.total_seconds() < -302400 ):
        #     ephbds.gpsweek += 1
        # elif(tt.total_seconds() >= 302400):
        #     ephbds.gpsweek -= 1        
        ephbds.gpstoe = t0.GPSSOW
        ephbds.gpsweek = t0.GPSWeek
        #ephbds.toc = ephbds.gpstoe
        #= bds toc to gpstoc
        ephbds.toc = bdsTime([ephbds.week,ephbds.toc,ctbtime.Rollover]).BDS2GPS().GPSSOW
        ephin.ephbds[IDnum-1] = deepcopy(ephbds)
        
    except:
        print('Warning in decoding_type1042')
        return -1
    return 2
        
        
class qzs_ephemeris:
    """ QZSS Satellite Ephemeris Type 1044 """
    def __init__(self, message):
        # Define constants
        pie = 3.1415926535898
        # Definition of the bits of the message
        contents = 'u12u4u16s8s16s22u8s16s16s32s16u32s16u32u16s16s32s16s' + \
                   '32s16s32s24s14u2u10u4u6s8u10u1'
        
        unpack_bits = bitstruct.unpack(contents, message)
        
        self.gnss = 'QZSS'
        self.gnss_short = 'J'
        # **************************** Parameters *************************** #
        # unpack_bits[0] is the message number, hence it is not considered here
        
        # QZSS satellite ID
        sat_ID = unpack_bits[1]
        # formatting
        sat_ID = str(sat_ID + 192)
        if len(sat_ID) < 2:
            self.sat_id = 'J0' + sat_ID
        else:
            self.sat_id = 'J' + sat_ID
        
        # QZSS toc
        self.toc     = unpack_bits[2] * pow(2,   4)
        
        # QZSS af2
        self.af_two  = unpack_bits[3] * pow(2, -55)
        
        # QZSS af1
        self.af_one  = unpack_bits[4] * pow(2, -43)
        
        # QZSS af0
        self.af_zero = unpack_bits[5] * pow(2, -31)
        
        # QZSS IODE
        self.iode    = unpack_bits[6]
        
        # Amplitude of the Sine Harmonic Correction Term to the Orbit Radius
        self.crs     = unpack_bits[7] * pow(2,  -5)
        
        # Mean Motion Difference from Computed Value
        self.dn      = unpack_bits[8] * pow(2, -43) * pie
        
        # Mean Anomaly at Reference Time
        self.m0      = unpack_bits[9] * pow(2, -31) * pie
        
        #  cuc
        self.cuc     = unpack_bits[10] * pow(2, -29)
        
        #  eccentricity (e)
        self.ecc     = unpack_bits[11] * pow(2, -33)
        
        # Amplitude of the Sine Harmonic Correction Term 
        # to the Argument of Latitude
        self.cus     = unpack_bits[12] * pow(2, -29)
        
        # Square Root of the Semi-Major Axis
        self.root_a  = unpack_bits[13] * pow(2, -19)
        
        # Reference Time Ephemeris
        self.toe     = unpack_bits[14] * pow(2,   4)
        
        # Amplitude of the Cosine Harmonic Correction Term 
        # to the Angle of Inclination
        self.cic     = unpack_bits[15] * pow(2, -29)
        
        # Longitude of Ascending Node of Orbit Plane at Weekly Epoch (omega_0)
        self.omega_0  = unpack_bits[16] * pow(2, -31) * pie
        
        # Amplitude of the Sine Harmonic Correction Term 
        # to the Angle of Inclination
        self.cis     = unpack_bits[17] * pow(2, -29)
    
        # Inclination Angle at Reference Time
        self.i0      = unpack_bits[18] * pow(2, -31) * pie
        
        # Amplitude of the Cosine Harmonic Correction Term to the Orbit Radius
        self.crc     = unpack_bits[19] * pow(2,  -5)
        
        # Argument of perigee (w) 
        self.omega   = unpack_bits[20] * pow(2, -31) * pie
        
        # Rate of Right Ascension
        self.omega_dot = unpack_bits[21] * pow(2, -43) * pie
        
        # Rate of Inclination Angle
        self.idot      = unpack_bits[22] * pow(2, -43) * pie
        
        # QZSS Codes on L2 Channel
        self.cl2 = unpack_bits[23]
        
        # QZSS week number
        self.week = unpack_bits[24] + 1024

        # QZSS URA 
        self.ura = unpack_bits[25]
        
        # QZSS SV Health
        self.health = unpack_bits[26]
        
        # QZSS TGD group delay differential
        self.tgd = unpack_bits[27] * pow(2, -31)     
        
        # QZSS IODC
        self.iodc = unpack_bits[28]
        
        # QZSS fit interval
        self.interval = unpack_bits[29]
        
    
    
def data_decoding(rtcm,ssr=None,eph=None):
    # ret: 
    message = rtcm.buff
    #msg_type = bitstruct.unpack('u12', message[3:])[0]
    msg_type = getbitu(message,24,'u12')
    #print('msg_type in decoding',msg_type)
    #print('msg_type',msg_type,rtcm.len)
    if (msg_type == 1019):               #gpseph
        ret = decode_type1019(rtcm,eph)
    # elif (msg_type == 1020):             #gloeph
    #     ret = decode_type1020(rtcm,eph)
    # elif (msg_type == 1042):             #bdseph
    #     ret = decode_type1042(rtcm,eph)
    # # elif (msg_type == 1044):
    # #     ret = decode_type1044(rtcm,eph)
    # elif (msg_type == 1045):             # galFeph
    #     ret = decode_type1045(rtcm,eph)
    # elif (msg_type == 1046):             # galIeph
    #     ret = decode_type1046(rtcm,eph)
    elif (msg_type == 1057):
        ret = decode_ssr1(rtcm,SYS_GPS,ssr)
    elif (msg_type == 1058):
        ret = decode_ssr2(rtcm,SYS_GPS,ssr)
    # elif (msg_type == 1059):
    #     ret = decode_ssr3(rtcm,SYS_GPS,ssr)
    elif (msg_type == 1060):
        ret = decode_ssr4(rtcm,SYS_GPS,ssr)
    # elif (msg_type == 1061):
    #     ret = decode_ssr5(rtcm,SYS_GPS,ssr)
    # elif (msg_type == 1062):
    #     ret = decode_ssr6(rtcm,SYS_GPS,ssr)
    elif (msg_type == 1063):
        ret = decode_ssr1(rtcm,SYS_GLO,ssr)
    elif (msg_type == 1064):
        ret = decode_ssr2(rtcm,SYS_GLO,ssr)
    # elif (msg_type == 1065):
    #     ret = decode_ssr3(rtcm,SYS_GLO,ssr)
    elif (msg_type == 1066):
        ret = decode_ssr4(rtcm,SYS_GLO,ssr)
    # elif (msg_type == 1067):
    #     ret = decode_ssr5(rtcm,SYS_GLO,ssr)
    # elif (msg_type == 1068):
    #     ret = decode_ssr6(rtcm,SYS_GLO,ssr)
    elif (msg_type == 1240):
        ret = decode_ssr1(rtcm,SYS_GAL,ssr)
    elif (msg_type == 1241):
        ret = decode_ssr2(rtcm,SYS_GAL,ssr)
    # elif (msg_type == 1242):
    #     ret = decode_ssr3(rtcm,SYS_GAL,ssr)
    elif (msg_type == 1243):
        ret = decode_ssr4(rtcm,SYS_GAL,ssr)
    # elif (msg_type == 1244):
    #     ret = decode_ssr5(rtcm,SYS_GAL,ssr)
    # elif (msg_type == 1245):
    #     ret = decode_ssr6(rtcm,SYS_GAL,ssr)
    # elif (msg_type == 1246):
    #     ret = decode_ssr1(rtcm,SYS_QZS,ssr)
    # elif (msg_type == 1247):
    #     ret = decode_ssr2(rtcm,SYS_QZS,ssr)
    # elif (msg_type == 1248):
    #     ret = decode_ssr3(rtcm,SYS_QZS,ssr)
    # elif (msg_type == 1249):
    #     ret = decode_ssr4(rtcm,SYS_QZS,ssr)
    # elif (msg_type == 1250):
    #     ret = decode_ssr5(rtcm,SYS_QZS,ssr)        
    # elif (msg_type == 1251):
    #     ret = decode_ssr6(rtcm,SYS_QZS,ssr)
    # elif (msg_type == 1252):
    #     ret = decode_ssr1(rtcm,SYS_SBS,ssr)
    elif (msg_type == 1258):
        ret = decode_ssr1(rtcm,SYS_BDS,ssr)
    elif (msg_type == 1259):
        ret = decode_ssr2(rtcm,SYS_BDS,ssr)
    # elif (msg_type == 1260):
    #     ret = decode_ssr3(rtcm,SYS_BDS,ssr)
    elif (msg_type == 1261):
        ret = decode_ssr4(rtcm,SYS_BDS,ssr)
    # elif (msg_type == 1262):
    #     ret = decode_ssr5(rtcm,SYS_BDS,ssr)
    # elif (msg_type == 1263):
    #     ret = decode_ssr6(rtcm,SYS_BDS,ssr)
    else:
        ret = 0
    return ret
        
            
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
        