
from datetime import datetime
import numpy as np

class swasChkData:
    def __init__(self):
        
        # "Date", "Time",
        # "sys", "prn",
        # "lRaw", "snr", "pRaw",
        # "dop", "lMod", "y",
        # "dants", "dantr", "phw",
        # "zwd", "m_w", "m_h",
        # "zhd", "dtrp", "az", "el"
        
        #= time, sys,prn
        #= y,xs,ys,zs
        #= xr,yr,zr,r
        #= cdtr,cdts,rel,dtrp
        #= cdion,dcb,bias,res
        #= dr1,dr2,dr3,rdis
        #= rRot,fixFlag,refFlag
        self.date    = 0
        self.time     = 1
        self.sys     = 2
        self.prn       = 3
        self.lRaw      = 4
        self.snr      = 5
        self.pRaw     = 6
        self.dop      = 7
        self.lMod      = 8
        self.y      = 9
        self.dants       = 10
        self.dantr    = 11
        self.phw    = 12
        self.zwd     = 13
        self.m_w    = 14
        self.m_h   = 15
        self.zhd     = 16
        self.dtrp    = 17
        self.az     = 18
        self.el     = 19
        
    
def read_swasChk(filein):
    flag = 1
    file = open(filein,'r')
    swasout = swasChkData()
    CHKArr = []
    while flag:
        l = file.readline().strip('\n').split()
        if not l:
            file.close()
            flag = 0
        elif l[0][0:4] == 'chk1':
            date = l[0][4:]
            hms = l[1]
            a = date +' ' + hms
            time = datetime.strptime(a,"%Y/%m/%d %H:%M:%S.00")
            #= time, sys,prn
            #= y,xs,ys,zs
            #= xr,yr,zr,r
            #= cdtr,cdts,rel,dtrp
            #= cdion,dcb,bias,res
            #= dr1,dr2,dr3,rdis
            #= rRot,fixFlag,refFlag
            CHKArr.append([time,int(l[2]),int(l[3]),
                            float(l[4]),float(l[5]),float(l[6]),float(l[7])
                            ,float(l[8]),float(l[9]),float(l[10]),float(l[11])
                            ,float(l[12]),float(l[13]),float(l[14]),float(l[15]),
                            float(l[16]),float(l[17]),float(l[18]),float(l[19])
                            ])    
      
    CHKArr = np.vstack(CHKArr)
    swasout.CHK = CHKArr
    return swasout           
        
