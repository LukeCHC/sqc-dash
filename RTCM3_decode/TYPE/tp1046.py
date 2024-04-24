# -*- coding: utf-8 -*-
"""
Created on Wed Mar 20 09:23:02 2024

@author: CHCUK-11
"""
import bitstruct
from copy import deepcopy
from time_transform.time_format import GpsTime,GloTime,BdsTime,GalTime
from RTCM3_decode.EPH.ephData import GPSEPH,BDSEPH,GLOEPH,GALFEPH,GALIEPH

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
