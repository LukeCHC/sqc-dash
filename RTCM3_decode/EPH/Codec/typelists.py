# -*- coding: utf-8 -*-
"""
Created on Mon Nov  8 14:42:49 2021

@author: Zoe Chen
"""

# Note: No 1242 and 1260, as these two types are not decoded 
# based on the format in RTCM3.pdf
typelists = [1057,1058,1059,1060,    #G
            1063,1064,1065,1066,     #R
            1240,1241,1243,          #C
            1258,1259,1261,          #E
            1019,1020,1042,1045,1046]                 # EPH
            # 1044 QZSS eph
#            1258,1259,1261]   


typelists_ssr = [1057,1058,1060,
                 #1059,
                 1063,1064,1066,
                 # 1065,
                 #1240,1241,1243,
                 1258,1259,1261]    # correction

orbtype = [1057,1063,1240,1258]
clktype = [1058,1064,1241,1259]

#typelists_eph = [1019,1020,1042,1044,1045,1046]
typelists_ephgps = [1019]  # GPS
typelists_ephglo = [1020]  # GL0
typelists_ephbds = [1042]  # BDS
typelists_ephgal = [1045]  # GAL1
typelists_ephgal = [1046]  # GAL2
typelists_ephgal = [1044]  # QZSS

def get_typelists(system,rFlag):
    if(rFlag ==1): #ssr
        if (system == 'G'):
            typelist = [1057,1058,1060]
        elif (system == 'R'):
            typelist = [1063,1064,1065]
        elif (system == 'C'):
            typelist = [1258,1259,1261]
        elif (system == 'E'):
            typelist = [1240,1241,1243]
        
    elif(rFlag == 0):
        if (system == 'G'):
            typelist = [1019]
        elif (system == 'R'):
            typelist = [1020]
        elif (system == 'E'):
            #typelist = [1045]
            typelist = [1046]
        elif (system == 'C'):
            typelist = [1042]
    return typelist


def get_typelists_ssr(system):
    if (system == 'G'):
        typelist = [1057,1058,1060]
    elif (system == 'R'):
        typelist = [1063,1064,1065]
    elif (system == 'C'):
        typelist = [1258,1259,1261]
    elif (system == 'E'):
        typelist = [1240,1241,1243]
    return typelist

def get_typelist_eph(system):
    if (system == 'G'):
        typelist = [1019]
    elif (system == 'R'):
        typelist = [1020]
    elif (system == 'E'):
            #typelist = [1045]
        typelist = [1046]
    elif (system == 'C'):
        typelist = [1042]
    return typelist

#typelists_ssr_gps = [1057,1058,1059,1060]
typelists_ssr_gps = [1057,1058,1060]