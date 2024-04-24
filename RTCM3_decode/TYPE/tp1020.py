# -*- coding: utf-8 -*-
"""
Created on Wed Mar 20 09:17:54 2024

@author: 
"""
import bitstruct
from copy import deepcopy
from time_transform.time_format import GpsTime,GloTime,BdsTime,GalTime
from RTCM3_decode.EPH.ephData import GPSEPH,BDSEPH,GLOEPH,GALFEPH,GALIEPH

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