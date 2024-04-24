# -*- coding: utf-8 -*-
"""
Created on Wed Mar 20 09:13:38 2024
List of RTCM-SSR messages considered:
        - 1019: GPS ephemeris - 
        - 1020: GLONASS ephemeris -
        - 1042: Beidou ephemeris -
        - 1044: QZSS ephemeris
        - 1045: Galileo F/NAV ephemeris -
        - 1046: Galileo I/NAV ephemeris - 
        - 1057: GPS Orbit message -
        - 1058: GPS Clock message -
        - 1059: GPS Code bias -
        - 1060: GPS combined orbit and clock -
        - 1061: GPS URA message
        - 1265: GPS Phase Bias
        - 1063: GLONASS Orbit message -
        - 1064: GLONASS Clock message -
        - 1065: GLONASS Code bias -
        - 1066: GLONASS combined orbit and clock -
        - 1067: GLONASS URA message 
        - 1266: GLONASS Phase Bias
        - 1240: Galileo Orbit Message -
        - 1241: Galileo Clock Message -
        - 1242: Galileo Code bias -
        - 1243: Galileo combined orbit and clock -
        - 1244: Galileo URA message
        - 1245: Galileo High Rate Clock message
        - 1267: Galileo Phase Bias 
        - 1246: QZSS Orbit message -
        - 1247: QZSS Clock message -
        - 1248: QZSS Code bias -
        - 1249: QZSS combined orbit and clock -
        - 1250: QZSS URA message
        - 1251: QZSS High Rate Clock message
        - 1268: QZSS Phase Bias
        - 1258: BDS Orbit message -
        - 1259: BDS Clock message -
        - 1260: BDS Code bias -
        - 1261: BDS combined orbit and clock -
        - 1262: BDS URA message
        - 1263: BDS High Rate Clock message
        - 1270: BDS Phase Bias
        - 1264: SSR VTE
        - 4062: swift
            - SBP 1528: swift atmospheric corrections -
            - SBP 1532: swift -
            - SBP 1533: swift ionospheric correction polynomial -
            - SBP 1534: swift tropospheric and ionospheric residual corrections and bounds - 
            - SBP 3001: swift Communicate monitored states and flag integrity failures -
            - SBP 3242: swift GAL Code Bias -
            - SBP 3243: swift GAL Combined Orbit and Clock Corrections -
            - SBP 3260: swift BDS Code Bias -
            - SBP 3261: swift BDS Combined Orbit and Clock Corrections -
            - SBP 3265: swift GPS Phase Bias -
            - SBP 3267: swift GAL Phase Bias -
            - SBP 3270: swift BDS Phase Bias -
@author: 
"""

from RTCM3_decode.TYPE import *
from RTCM3_decode.Codec.getbitu import getbitu
from RTCM3_decode.common import SYS_GPS,SYS_GLO,SYS_GAL,SYS_BDS,SYS_QZS

def data_decoding(rtcm, ssr=None,eph=None):
    message = rtcm.buff
    #msg_type = bitstruct.unpack('u12', message[3:])[0]
    msg_type = getbitu(message,24,'u12')
    #print('msg_type',msg_type,rtcm.len)
    if (msg_type == 1019):               #gpseph
        ret = tp1019.decode_type1019(rtcm,eph)
    # elif (msg_type == 1020):             #gloeph
    #     ret =  tp1020.decode_type1020(rtcm,eph)
    # elif (msg_type == 1042):             #bdseph
    #     ret =  tp1042.decode_type1042(rtcm,eph)
    # elif (msg_type == 1045):             # galFeph
    # #     ret =  tp1045.decode_type1045(rtcm,eph)
    # elif (msg_type == 1046):             # galIeph
    #     ret =  tp1046.decode_type1046(rtcm,eph)
    elif (msg_type == 1057):
        ret =  tp1057.decode_ssr1(rtcm,SYS_GPS,ssr)
    elif (msg_type == 1058):
        ret =  tp1058.decode_ssr2(rtcm,SYS_GPS,ssr)
    # elif (msg_type == 1059):
    #     ret =  tp1059.decode_ssr3(rtcm,SYS_GPS,ssr)
    elif (msg_type == 1060):
        ret = tp1060.decode_ssr4(rtcm,SYS_GPS,ssr)
    elif (msg_type == 1063):
        ret =  tp1063.decode_ssr1(rtcm,SYS_GLO,ssr)
    elif (msg_type == 1064):
        ret =  tp1064.decode_ssr2(rtcm,SYS_GLO,ssr)
    elif (msg_type == 1065):
        ret = tp1065. decode_ssr3(rtcm,SYS_GLO,ssr)
    elif (msg_type == 1066):
        ret =  tp1066.decode_ssr4(rtcm,SYS_GLO,ssr)
    elif (msg_type == 1240):
        ret =  tp1240.decode_ssr1(rtcm,SYS_GAL,ssr)
    elif (msg_type == 1241):
        ret =  tp1241.decode_ssr2(rtcm,SYS_GAL,ssr)
    elif (msg_type == 1242):
        ret =  tp1242.decode_ssr3(rtcm,SYS_GAL,ssr)
    elif (msg_type == 1243):
        ret =  tp1243.decode_ssr4(rtcm,SYS_GAL,ssr)
    elif (msg_type == 1246):
        ret =  tp1246decode_ssr1(rtcm,SYS_QZS,ssr)
    elif (msg_type == 1247):
        ret =  tp1247.decode_ssr2(rtcm,SYS_QZS,ssr)
    elif (msg_type == 1248):
        ret =  tp1248.decode_ssr3(rtcm,SYS_QZS,ssr)
    elif (msg_type == 1249):
        ret =  tp1249.decode_ssr4(rtcm,SYS_QZS,ssr)
    elif (msg_type == 1258):
        ret =  tp1058.decode_ssr1(rtcm,SYS_BDS,ssr)
    elif (msg_type == 1259):
        ret =  tp1259.decode_ssr2(rtcm,SYS_BDS,ssr)
    elif (msg_type == 1260):
        ret =  tp1060.decode_ssr3(rtcm,SYS_BDS,ssr)
    elif (msg_type == 1261):
        ret =  tp1261.decode_ssr4(rtcm,SYS_BDS,ssr)
    elif (msg_type == 4062):
        ret =  tp4062.decode_type4062(rtcm,ssr)
    else:
        ret = 0
    return ret
        






















