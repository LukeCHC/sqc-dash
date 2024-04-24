# -*- coding: utf-8 -*-
"""
Created on Wed Mar 20 09:13:14 2024

@author: 
"""
import bitstruct
from copy import deepcopy
from RTCM3_decode.EPH.ephData import GPSEPH,BDSEPH,GLOEPH,GALFEPH,GALIEPH

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