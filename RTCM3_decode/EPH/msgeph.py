# -*- coding: utf-8 -*-
"""
Created on Tue Dec 14 09:13:49 2021
@author: Zoe Chen
2022Sep22: download msg and check eph update flag every 5 seconds
           update eph if eph update flag is 1 and msg length > 100
2022Jan12: Download eph, save eph to sharedssr, 
2021Dec19: eph adding updated
"""
fixed_data_len = 4096 # downloading msg lenth every time
import sys
import socket
import time
sys.dont_write_bytecode = True
import logging
from EPH import ephData
from TimeTrans.timeFormat import gpsTime,utcTime,str2dt
#from RTCM3.rtcm3 import decoderaw
from rtcm3_reader import decoderaw, rtcm3
from common import SYS_GPS,SYS_BDS,SYS_GLO,SYS_GAL

#EPHip = LOCALIP
#EPHport = 10011

class tcprecv_data:
    def __init__(self,IP,PORT):
        self.IP = IP
        self.PORT = PORT
        self.tcp = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        
    def connect_tcp(self):
        try:
            self.tcp.connect((self.IP, self.PORT))
        except:
            print ('Warning tcp is down from', self.IP,self.PORT)
        return
    
    def recv(self,sec):
        msg = b'' 
        tstart = time.perf_counter()
        try:
            while True:
                #self.tcp.settimeout(1.0)
                data = self.tcp.recv(fixed_data_len)
                msg += data
                tend = time.perf_counter()
                tdiff = tend - tstart
                # sec =1 for corrections
                # sec = 4 for EPH
                if(tdiff > sec): 
                    #tstart = time.perf_counter()
                    break

        except KeyboardInterrupt:
            sys.exit()
        return msg

    def run(self,sec):
    # input: tcp, connected
    # Output: msg from data_downloading in 1 sec     
        msg = b'' 
        try:
            msg = self.recv(sec)
        except KeyboardInterrupt:
            sys.exit()

        return msg
    
    def reconnect(self,sec):
        msg = b'' 
        try:
            self.tcp.close()
            self.connect_tcp()
            msg = self.recv(sec)

        except KeyboardInterrupt:
            sys.exit()
        return msg


class EPH_process:
    def __init__(self,EPHIP,EPHPORT):
        self.EPHIP = EPHIP
        self.EPHPORT = EPHPORT
        self.system ='G'
        self.rtcmeph = rtcm3()
        self.ephUser = ephData.ephUser() # Multiple IODE for each sat
        self.tcp     = tcprecv_data(self.EPHIP,self.EPHPORT)
        self.tcp.connect_tcp()
       
    def run(self,eymd):
        ctymd = gpsTime()
        while (ctymd.datetime < eymd):
            try:
                msgEPH = self.tcp.run(sec=5)#
            except:
                msgEPH = bytearray()
                
            try:
                logging.info('msgEPH length: {}'.format(len(msgEPH)))
                if(len(msgEPH) > 100):                           
                    ret =  decoderaw(self.rtcmeph,msgEPH) #ephdata in ret[1]
                        
            except:
                pass
            ctymd = gpsTime()            
        return 

def input_time(inputtime):
    eymdt1 = inputtime.split("-")
    eymdt2 = ''.join(eymdt1)
    eymd = utcTime(str2dt(str(eymdt2))).UTC2GPS().datetime
    return eymd

EPHIP = '18.170.8.65'
EPHPORT = 10011
eymd = input_time("2024-04-18-21-43-00") # "2024-04-18-21-43-00"
ephrun = EPH_process(EPHIP, EPHPORT)
ephrun.run(eymd)
