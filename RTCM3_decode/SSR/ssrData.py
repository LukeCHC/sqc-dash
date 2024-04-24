"""
   Group of classes to create RTCM-SSR objects.
   Input : decoded rtcm-ssr message
   Output: object oriented ssr message
   
   ****************************************************************************
   Description:
   the SSR class is initialized with objects the epos, the epo information
   (epoch,ssrs). for each ssr(SSRNSAT), including all systems.
   for each system, including all sates(SSRSAT)
   This objects are updated for each sat there is a new message 
   calling the class msgtype.
"""
import sys
sys.dont_write_bytecode = True
import numpy as np
from GNSS import GPS,BDS,GAL,GLO
from RTCM3_decode.common import SYS_GPS,SYS_GLO,SYS_GAL,SYS_BDS
from copy import deepcopy

class HEADS:
    def __init__(self):
        self.epoch  = None  # SSR epoch
        self.gpsepo = None  # SSR gps epo 
        self.udi    = None  # SSR update Interval
        self.sync   = None  # Multiple Message Indicator
        self.refd   = None  # sat ref datum (0:ITRF,1:regional)
        self.iod    = None  # IOD SSR
        self.provid = None  # provider ID 
        self.solid  = None  # solution ID
        self.nsat   = None  # nsat
        self.hsize  = None  # head side
        
class SSRSAT:
    # ssr variables for each sat
    def __init__(self):
        self.t0     = None  # gps time
        self.gpsepo  = [None] * 6  # gps epoch [orb,clk,hrclk,ura,bias,pbias]
        self.epoch   =[None] * 6  # original epo 
        self.udi    = [None] * 6  # SSR update Interval
        self.sync   = [None] * 6  # Multiple Message Indicator
        self.refd   = None  # sat ref datum (0:ITRF,1:regional)
        self.iod    = [None] * 6  # IOD SSR
        self.provid = None  # provider ID
        self.solid  = None  # solution ID
        self.prn    = None  # sat prn number
        self.iode   = None  # issue of data BDS1058/t0 modulo
        self.iodcrc = None  # issue of data crc for beidou/sbas
        self.orb    = []  # orbit, rac # space for multiple orbs for one epo 
        self.orbv   = [] # orbit dr,da,dc
        self.clk    = [None] *3  # clock dc0,dc1,dc2
        self.hrclk  = None  # high-rate clock corection (m) 
        self.cbias  = None  # code biases (m)
        self.pbias  = None  # phase biases (m)
        self.stdpb  = None  # std-dev of phase biases (m)
        self.gnss   = None  # system SHORT name
        self.track  = None  # DF380 in Code Bias
        self.name   = None  # 
        self.update = None  # update flag
        self.ura    = None  # URA indicator
        
        # for mix 
        self.acname = None
        self.dclk   = 0
        self.dClkResult = 0
        self.diffRao = []
        self.eph     = None
    
    def __repr__(self):
        return ('sat: p1 decoded from msg,' +
                'p2 for mix, AC,eph,dClkResult,diffRao')

class SSRnsat:
    # for all sats in a SYS
    # default is one SSRSAT for each sat self.sats[0] when decoding
    # multiple records for each sat from multiple ACS when mixing
    def __init__(self,sys):
        self.gpsepo   = None # same gpsepo for all sats
        if(sys == SYS_GPS):
            self.sats = [None] * GPS.MaxNoSV
        elif(sys == SYS_GLO):
            self.sats = [None] * GLO.MaxNoSV
        elif(sys == SYS_GAL):
            self.sats = [None] * GAL.MaxNoSV
        elif(sys == SYS_BDS):
            self.sats = [None] * BDS.MaxNoSV
            
    def update_sat(self,ssrsat0,jac=None):
        # add infor for each sat
        # infor from different AC j for each sat can be added
        if jac is None:
            jac = 0
        idex = ssrsat0.prn - 1
        if(self.gpsepo is None):
            self.gpsepo = ssrsat0.gpsepo
        self.sats[idex][jac] = ssrsat0
        return
    
class SSRS:
    def __init__(self):
        # this class is for one system
        self.gpsepos = [] #all epochs
        self.ssrs = [] # one ssr for one epoch
            
    def update_sat(self,sat0):
        # I: ssr0 for each sat
        epo0 = sat0.gpsepo
        if(epo0 not in self.gpsepos):
            self.gpsepos.append(epo0)
        try:
            epoidx = np.where(np.array(self.gpsepos) == epo0)[0][0]
        except:
            print('Warning epo not found in SSR')
        self.ssrs[epoidx].update_sat(sat0)
               
    def update_ssr(self,ssr0):
        # I: ssr0 for all sat at one epo
        #    ssr0 is ready when call this function
        epo0 = ssr0.gpsepo
        if(epo0 not in self.gpsepos):
            self.gpsepos.append(epo0)
            self.ssrs.append(ssr0)
        # = when called in ssr_filter, epos are repeated to check for different orbs
        #   ignore the ssr0 if epo has been done for previous orbs cycle
        #else: 
        #    print('Warning epo exists in ssrData.SSRS')
                   
    def combine_ssrs(self,ssrs0,resTime=None,saveTime=None):
        # Notes: to combine two SSRS
        # I: ssrs0 include multiple gpsepos
        nepo = len(ssrs0.gpsepos)
        for i in range(nepo):
            epo = ssrs0.gpsepos[i]
            ssrt = deepcopy(ssrs0.ssrs[i])
            self.ssrs.append(ssrt)
            self.gpsepos.append(epo)
        if(resTime is not None):
            self.filter_ssr(resTime,saveTime)
        return
               
    def filter_ssr(self,resTime,saveTime=None):
        if(saveTime is None):
            saveTime = 0
        keepTime = resTime -saveTime 
        if(keepTime < 0):
            # Note: resTime is the begining of the week
            keepTime = 60

        nepo = len(self.gpsepos)
        if nepo > 6: # at least keep 6 epos(30 seconds) 
            for j in range(nepo-1,-1,-1):
                epo0 = self.gpsepos[j]
                if(epo0 < keepTime):
                    del self.gpsepos[j]
                    del self.ssrs[j]
        return
     
    def get_ssr(self,epo,sys):
        # Initialize ssrs for specified epo and sys
        # get ssr for specified epo 
        # ssr0 will be updated when call this function
        if(epo not in self.gpsepos):
            self.gpsepos.append(epo)
            if(sys == SYS_GPS):
                self.ssrs   = np.append(self.ssrs,SSRnsat(sys))
            elif(sys == SYS_GLO):
                self.ssrs   = np.append(self.ssrs,SSRnsat(sys))
            elif(sys == SYS_BDS):
                self.ssrs   = np.append(self.ssrs,SSRnsat(sys))
            elif(sys == SYS_GAL):
                self.ssrs   = np.append(self.ssrs,SSRnsat(sys))
        try:
            epoidx = np.where(np.array(self.gpsepos) == epo)[0][0]
            ssr0 = self.ssrs[epoidx]
        except:
            print('Wrong! ssr0 should be found in SSRS')
        return ssr0
    
    
class SSRS_SYS:
    def __init__(self):
        # this class collects all sys 
        self.ssrgps = SSRS()  # decoded G ssr
        self.ssrbds = SSRS()  # decoded C ssr
        self.ssrgal = SSRS()  # decoded E ssr
        self.ssrglo = SSRS()  # decoded R ssr 
        self.swift = swift()
        return
        

class MSG:
    # SSR msg structure head + nsat
    # one record or multiple records    
    def __init__(self):
        self.epoch = None
        self.type = None
        self.udi = None
        self.refd = None
        self.sync = None
        self.iod = None
        self.provid = None
        self.solid = None
        self.nsat = None
        self.prn= [] 
        self.iode = []
        self.dr = [] 
        self.dt = [] 
        self.dn = []
        self.dot_dr = []
        self.dot_dt = []
        self.dot_dn = []
        self.dc0 = []
        self.dc1 = []
        self.dc2 = []
        self.number = [] # in 1059
        self.track = []
        self.bias =[]
        self.iodcrc = [] # for BDS
        return
        
class Types:
    # multiple types, for one epo
    def __init__(self):
        self.msgs = []
        self.types = []
        
    def add_msg(self,msg):
        # add new msg, keep the old one
        self.msgs.append(msg)
        self.types.append(msg.type)
        
def orb_type(sys):
    if(sys == SYS_GPS):
        msg_type = 1057
    elif(sys == SYS_GLO):
        msg_type = 1063
    elif(sys == SYS_GAL):
        msg_type = 1240
    elif(sys == SYS_BDS):
        msg_type = 1258 
    return msg_type        
        
def clk_type(sys):
    if(sys == SYS_GPS):
        msg_type = 1058
    elif(sys == SYS_GLO):
        msg_type = 1064
    elif(sys == SYS_GAL):
        msg_type = 1241
    elif(sys == SYS_BDS):
        msg_type = 1259
    return msg_type
#------------------------------------------------------------------------------
class swift():
    def __init__(self):
        self.swiftatm = []
        self.swiftion = []
        self.swiftgrid = []
        self.swiftintegflag = []
        self.gpsssr = swift_ssr()
        self.bdsssr = swift_ssr()
        self.galssr = swift_ssr()
        return

class swift_atm(): #SBP 1534, 1532 head
    def __init__(self):
        self.tilesid = None
        self.tileid = None
        self.time = None
        self.udi = None
        self.atmiod = None
        self.tropQI = None
        self.grididx = None
        self.tropdelay = []
        self.tropdelaystd = None
        self.solid = None
        self.tropebmean = []
        self.tropebstd = []
        self.atm = []
        return

class swift_atm_prn(): #SBP 1534, 1532 prn data
    def __init__(self):
        self.svid = None
        self.sysid = None
        self.STECres = None
        self.STECstd = None
        self.STECebmean = None
        self.STECebstd = None
        self.STECebmeanC = None
        self.STECebstdC = None
        self.update = None
        return

class swift_ion(): #SBP 1533 head
    def __init__(self):
        self.time = None
        self.udi = None
        self.solid = None
        self.iodatm = None
        self.tilesid = None
        self.tileid = None
        self.ion = []
        return

class swift_ion_prn(): #SBP 1533 prn data
    def __init__(self): 
        self.sysid = None
        self.svid = None
        self.stecQT = None
        self.ionpolyC = []
        self.update = None 
        return

class swift_grid(): #SBP 1528
    def __init__(self):
        self.time = None
        self.udi = None
        self.solid = None
        self.iodatm = None
        self.tilesid = None
        self.tileid = None
        self.NWlat = None
        self.NWlon = None
        self.splat = None
        self.splon = None
        self.rows = None
        self.columns = None
        self.bitmark = None  
        return

class swift_integflag(): #SBP3001
    def __init__(self):
        self.obstime = None
        self.corrtime = None
        self.solid = None
        self.tilesid = None
        self.tileid = None
        self.chainid = None
        self.useG = None 
        self.useE = None
        self.useC = None
        self.usetropgp = None
        self.useionogp = None
        self.useionotilesatlos = None
        self.useionogpsatlos = None
        self.update = None
        return

class swift_ssr ():
    def __init__(self):
        self.epoch = []
        self.ssr = []
        return

class swift_ssr_sys():
    def __init__(self,sys):
        if(sys == SYS_GPS):
            self.sats = [swift_ssr_prn()] * 32
        elif(sys == SYS_GLO):
            self.sats = [swift_ssr_prn()] * 28
        elif(sys == SYS_GAL):
            self.sats = [swift_ssr_prn()] * 36
        elif(sys == SYS_BDS):
            self.sats = [swift_ssr_prn()] * 64
        return
    
class swift_ssr_prn():
    def __init__(self):
        self.codeCount = None
        self.sys_id = None
        self.svid = None
        self.t0 = [None]*6
        self.udi = [None]*6
        self.iod = [None]*6 # iod ssr [eph,clk,hrclk,ura,bias]
        self.iode = None
        self.iodp = None
        self.iodcrc = None #issue of data crc for bds/sbas
        self.ura = None
        self.refd = None #sat ref datum (0:ITRF, 1:regional)
        self.deph = [None]*3 #delta orbit (radial, along, cross) m
        self.ddeph = [None]*3 # delta orbit velocity m/s
        self.dclk = [None]*3 #delta clock (c0,c1,c2)
        self.hrclk = None #high-rate clock correction m
        self.cbias = [None]*61 #CGCODEC_MAX_NUM_CODE
        self.pbias = [None]*61 #CGCODEC_MAX_NUM_CODE
        self.stdpb = [None]*61 #CGCODEC_MAX_NUM_CODE 
        self.codeIndex = None
        self.yaw_ang = None
        self.yaw_rate = None
        return
        





