# -*- coding: utf-8 -*-
"""
Created on Mon Jun 13 16:28:02 2022

@author: Zoe Chen
"""
from copy import deepcopy
from SSR.ssrData import SSRS_SYS
from RTCM3.rtcm3 import decoderaw
from common.common import SYS_GPS,SYS_BDS,SYS_GAL,SYS_GLO
#from common.common import SYS_GLO,SYS_GAL,SYS_BDS
from SSR.ssrData import SSRS,SSRnsat
from library.GNSS import GPS
#from common.common import AC0,
from common.common import AC1,AC2,AC3,AC4,AC5

def match_OC_v1(satorb,satclk):
    # In: sat0  multile orb, one clk for this sat
    # Out: newsat # one orb and one clk saved
    newsat = None
    if((satclk is not None) & (satorb is not None)):
        newsat = deepcopy(satclk)
        if (any(newsat.clk)):
            # orb only keep one from here
            newsat.orb = satorb.orb[0]
            newsat.orbv = satorb.orbv[0]
            newsat.refd = satorb.refd
            #newsat.syn
        else:
            newsat = None
    return newsat
    
def match_OC_v2(AC,sat1,sat2):
    #In: sat1 with multiple orb infor
    #    sat2 with clk infor
    #Out: newsat with both selected orb and clk
    if((sat1 is None) or (sat2 is None)): # No sat
        newsat = None
        return
        
    if(not any(sat2.clk)):
        newsat = None # No clk
        return
    else:
        newsat = deepcopy(sat2)
        
    if(not any(sat1.orb)):
        newsat = None # No orb
        return
    
    orbepo = sat1.gpsepo[0]
    orbiode = sat1.iode
    orb     = sat1.orb
    orbv    = sat1.orbv
    clkepo = sat2.gpsepo[1] 
    if(AC == 'AC0'):
        # there are possible error as orb might be missing, not 12 times
        diff = clkepo - orbepo
        if(len(orb) == 12):
            # no missing data
            j = int(diff/5)
        else:
            j = -1 # use the latest one ! possible error
        oldorb0 = orb[j][0]
        oldorb1 = orb[j][1]
        oldorb2 = orb[j][2]
        orb0 = oldorb0 + orbv[j][0] * diff # use the latest one
        orb1 = oldorb1 + orbv[j][0] * diff
        orb2 = oldorb2 + orbv[j][0] * diff
        neworb = [orb0,orb1,orb2]
    else:
        neworb = orb[0]
    
    #= add the infor to newsat
    # orb only keep one from here
    newsat.orb = neworb
    newsat.orbv = deepcopy(sat1.orbv[-1])
    newsat.iode = orbiode
    newsat.refd = sat1.refd
    # for SH, need to do cal
    # for DLR, no cal
    
    return newsat


def check_orb(ssrin):
    #= check if orb info is in ssrin
    #  found all orb
    orb = []
    nepo = len(ssrin.gpsepos)
    for i in range(nepo):
        satsepo = ssrin.ssrs[i]
        nsat = len(satsepo.sats)
        for j in range(nsat):
            sat0 = satsepo.sats[j]
            try:
                if any(sat0.orb):
                    orb.append(satsepo)
                    break
            except:
                # this sat is None
                # no orb in this sat
                pass
    return orb


def ssr_filter(sys,AC,ssrin,ssrtmp,ssrnew,resTime):
    #= Notes: for SH, multiple orb for the same epoch
    #         for DLR, one orb every 30 seconds
    #  if new orb in ssrnew, use new orb
    #  if no new orb in ssrnew, but orb in ssrin, use the old one
    
    #= In: ssrtmp: the latest ssr
    #= IO: ssrin: (old ssr), will be updated with ori ssrtmp 
    #      ssrnew: combined oc with ssrtmp, will be updated with combined oc
    #               delete old msg(earlier than resTime) in ssrnew
    #      match orb and clk if clk exists
    if sys == SYS_GPS:
        ssrt = ssrtmp.ssrgps # get msg for one system
    elif sys == SYS_BDS:
        ssrt = ssrtmp.ssrbds
    elif sys == SYS_GAL:
        ssrt = ssrtmp.ssrgal
    elif sys == SYS_GLO:
        ssrt = ssrtmp.ssrglo
    
    # choose only one system from Here
    ret = 0
    #= add all ssrt in ssrin
    #saveTime = resTime 
    ssrin.combine_ssrs(ssrt,resTime,saveTime = 60)
    
    #if((AC != 'AC0') and (AC != 'AC1')): # only do filter for SH and DLR
    if(AC != 'AC0'): # only do filter for SH and DLR
        #new = deepcopy(ssrt)
        nepo = len(ssrt.gpsepos)
        # orb only keep one from here
        #= transfer orb = [[orb0,orb1,orb2]] to [orb0,orb1,orb2]
        for i in range(nepo):
            satsepo = ssrt.ssrs[i]
            nsat = len(satsepo.sats)
            for j in range(nsat):
                new = satsepo.sats[j]
                if (new is not None):
                    try:
                        new.orb = new.orb[0]
                        new.orbv = new.orbv[0]
                    except:
                        #= no orb
                        new = None
        ssrnew.combine_ssrs(ssrt,resTime)
        return ret
    
    nepo = len(ssrt.gpsepos)
    # find the orb at latest epoch
    orb = check_orb(ssrt)
    new = SSRS()
    if(len(orb) == 0): # check orb in ssrin
        orb = check_orb(ssrin)
   
    if(len(orb) >0 ): # orb found 
        # cycle all epo, to check clk
        for i in range(len(orb)):
            orbt = orb[i]
            #  cycle all epo, to check clk
            # update ssrt to matched new ssr
            
            nepo = len(ssrt.gpsepos)
            orbepo = orbt.gpsepo
            for j in range(nepo):
                epo = ssrt.gpsepos[j]
                clkt = ssrt.ssrs[j]
                ssr0 = SSRnsat(sys) # for each epoch
                ssr0.gpsepo = epo
                if(clkt is not None):
                    nsat = len(clkt.sats)
                    for k in range(nsat):
                        satclk = clkt.sats[k]
                        satorb = orbt.sats[k]
                        newsat = None
                        if(epo == orbepo):
                            newsat = match_OC_v1(satorb,satclk)
                        elif( (epo > orbepo) & (epo < (orbepo + 60)) ):
                            newsat = match_OC_v2(AC,satorb,satclk)
                        if(newsat is not None):
                            newsat.sync = [0,0] # same as SH
                            newsat.dclk = newsat.clk[0]/GPS.c
                            if((newsat.refd is None) & any(newsat.orb)):
                                print('Warning newsat.refd is None')
                        ssr0.sats[k] = deepcopy(newsat)
                    # matched oc for all sats at each epoch
                    if(any(ssr0.sats)):
                        new.update_ssr(ssr0) 
        # add matched new(including all epochs) to ssrnew
        ssrnew.combine_ssrs(new,resTime)  
        
    return ret


def get_SSR_ACS(sys,msgACS,rtcmACS,ssrallin,ssrallnew,resTime):
    # I: msgACS
    # IO:update ssr based on new msg
    # IO:update rtcmACS for next cycle
    keylist = list(ssrallin)
    #listac  = list(rtcmACS)
    nlen = len(keylist)
    ret = 0
    for i in range(nlen):
        AC = keylist[i]
        #ACmsg = msgACS[AC].get_msg()
        ACmsg = msgACS[AC]
        ssracin = ssrallin[AC]
        ssracnew = ssrallnew[AC]
        rtcmAC = rtcmACS[AC]
        ssrtmp = SSRS_SYS()
        # considering all SYS
        ret = decoderaw(rtcmAC,ACmsg.msg,ssrin =ssrtmp)
        
        if(ret != 0):
            print('Warning in decode AC0')
            return ret
        
        # from here, only one system selected
        ret = ssr_filter(sys,AC,ssracin,ssrtmp,ssracnew,resTime)
        rtcmACS.update({AC:rtcmAC})
        ssrallin.update({AC:ssracin})
        ssrallnew.update({AC:ssracnew})
    return ret


def get_SSR(sys,msgACS,rtcmACS,ssrtmp,resTime):
    # I: msgACS
    # IO:update ssr based on new msg
    # IO:update rtcmACS for next cycle
    keylist = list(ssrtmp)
    #listac  = list(rtcmACS)
    nlen = len(keylist)
    ret = 0
    for i in range(nlen): # cycle AC
        AC = keylist[i]
        #ACmsg = msgACS[AC].get_msg()
        ACmsg = msgACS[AC]
        #ssracin = ssrallin[AC]
        #ssracnew = ssrallnew[AC]
        rtcmAC = rtcmACS[AC]
        ssrt = SSRS_SYS()
        # considering all SYS
        ret = decoderaw(rtcmAC,ACmsg.msg,ssrin =ssrt)
        
        if(ret != 0):
            #print('Warning in decode AC0')
            return ret
        
        # from here, only one system selected
        #ret = ssr_filter(sys,AC,ssracin,ssrtmp,ssracnew,resTime)
        rtcmACS.update({AC:rtcmAC})
        #ssrallin.update({AC:ssracin})
        #ssrallnew.update({AC:ssracnew})
        ssrtmp.update({AC: ssrt})
    return ret

def get_SSR_SYS(sys,ssrtmp,ssrsysin,ssrsysnew,resTime):
    # update ssr for each system based on the new ssr(ssrtmp)
    keylist = list(ssrsysin)
    #listac  = list(rtcmACS)
    nlen = len(keylist)
    ret = 0
    for i in range(nlen):
        AC = keylist[i]
        #ACmsg = msgACS[AC].get_msg()
        #ACmsg = msgACS[AC]
        ssrt0  = ssrtmp[AC]
        ssracin = ssrsysin[AC]
        ssracnew = ssrsysnew[AC]
        #rtcmAC = rtcmACS[AC]
        
        # considering all SYS
        #ret = decoderaw(rtcmAC,ACmsg.msg,ssrin =ssrtmp)
                
        # from here, only one system selected
        ret = ssr_filter(sys,AC,ssracin,ssrt0,ssracnew,resTime)
        #rtcmACS.update({AC:rtcmAC})
        ssrsysin.update({AC:ssracin})
        ssrsysnew.update({AC:ssracnew})
    return ret


def collect_msgs(AC1msg,AC2msg,AC3msg,AC4msg,AC5msg):
    msgACS ={}
    ACmsg1 = AC1msg.get_msg()
    ACmsg2 = AC2msg.get_msg()
    ACmsg3 = AC3msg.get_msg()
    ACmsg4 = AC4msg.get_msg()
    ACmsg5 = AC5msg.get_msg()
    msgACS.update({AC1: ACmsg1})
    msgACS.update({AC2: ACmsg2})
    msgACS.update({AC3: ACmsg3})
    msgACS.update({AC4: ACmsg4})
    msgACS.update({AC5: ACmsg5})
    return msgACS   