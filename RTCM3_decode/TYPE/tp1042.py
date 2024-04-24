# -*- coding: utf-8 -*-
"""
Created on Wed Mar 20 09:20:12 2024

@author: 
"""
import bitstruct
from copy import deepcopy
from time_transform.time_format import GpsTime,GloTime,BdsTime,GalTime
from RTCM3_decode.EPH.ephData import GPSEPH,BDSEPH,GLOEPH,GALFEPH,GALIEPH

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