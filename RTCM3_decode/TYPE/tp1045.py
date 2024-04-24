# -*- coding: utf-8 -*-
"""
Created on Wed Mar 20 09:21:48 2024

@author: CHCUK-11
"""
import bitstruct
from copy import deepcopy
from RTCM3_decode.EPH.ephData import GPSEPH,BDSEPH,GLOEPH,GALFEPH,GALIEPH

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
        