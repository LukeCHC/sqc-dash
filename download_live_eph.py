# download eph from chc stream
from RTCM3_decode.rtcm3_reader import decoderaw, rtcm3
from RTCM3_decode.EPH import ephData
from datetime import datetime
import socket
import sys
import time

fixed_data_len = 4096 # downloading msg lenth every time
EPHIP = '18.170.8.65'
EPHPORT = 10011

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

class DownloadAndDecodeChcEph:
    def __init__(self,EPHIP,EPHPORT):
        self.EPHIP = EPHIP
        self.EPHPORT = EPHPORT
        self.system ='G'
        self.rtcmeph = rtcm3()
        self.ephUser = ephData.ephUser() # Multiple IODE for each sat
        self.tcp     = tcprecv_data(self.EPHIP,self.EPHPORT)
        self.tcp.connect_tcp()

    def run(self):
        msgEPH = self.tcp.run(sec=5)#
        decoded_data =  decoderaw(self.rtcmeph,msgEPH) 
        return decoded_data
    
if __name__ == '__main__':
    downloader = DownloadAndDecodeChcEph(EPHIP, EPHPORT)
    decoded_data = downloader.run()