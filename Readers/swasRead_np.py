
from datetime import datetime
import numpy as np

class swasdata:
    def __init__(self):
        #= time, sys,prn
        #= y,xs,ys,zs
        #= xr,yr,zr,r
        #= cdtr,cdts,rel,dtrp
        #= cdion,dcb,bias,res
        #= dr1,dr2,dr3,rdis
        #= rRot,fixFlag,refFlag
        self.time    = 0
        self.sys     = 1
        self.prn     = 2
        self.y       = 3
        self.xs      = 4
        self.ys      = 5
        self.zs      = 6
        self.xr      = 7
        self.yr      = 8
        self.zr      = 9
        self.r       = 10
        self.cdtr    = 11
        self.cdts    = 12
        self.rel     = 13
        self.dtrp    = 14
        self.cdion   = 15
        self.dcb     = 16
        self.bias    = 17
        self.res     = 18
        self.dr1     = 19
        self.dr2     = 20
        self.dr3     = 21
        self.rdis    = 22
        self.rRot    = 23
        self.fixFlag = 24
        self.refFlag = 25
        self.FIX1    = None
        self.FIX2    = None
        
    
def read_swas(filein):
    flag = 1
    file = open(filein,'r')
    swasout = swasdata()
    FIX1Arr = []
    FIX2Arr = []
    while flag:
        l = file.readline().strip('\n').split()
        if not l:
            file.close()
            flag = 0
        elif l[0][0:4] == 'FIX1':
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
            FIX1Arr.append([time,int(l[2]),int(l[3]),
                            float(l[4]),float(l[5]),float(l[6]),float(l[7])
                            ,float(l[8]),float(l[9]),float(l[10]),float(l[11])
                            ,float(l[12]),float(l[13]),float(l[14]),float(l[15]),
                            float(l[16]),float(l[17]),float(l[18]),float(l[19]),
                            float(l[20]),float(l[21]),float(l[22]),float(l[23]),
                            float(l[24]),int(l[25]),int(l[26])
                            ])    
        elif l[0][0:4] == 'FIX2':
            date = l[0][4:]
            hms = l[1]
            a = date +' ' + hms
            time = datetime.strptime(a,"%Y/%m/%d %H:%M:%S.00")
            FIX2Arr.append([time,int(l[2]),int(l[3]),
                            float(l[4]),float(l[5]),float(l[6]),
                            float(l[7]),float(l[8]),float(l[9]),
                            float(l[10]),float(l[11]),float(l[12]),
                            float(l[13]),float(l[14]),float(l[15]),
                            float(l[16]),float(l[17]),float(l[18]),
                            float(l[19]),float(l[20]),float(l[21]),
                            float(l[22]),float(l[23]),float(l[24]),
                            int(l[25]),int(l[26])
                            ])    
    FIX1Arr = np.vstack(FIX1Arr)
    FIX2Arr = np.vstack(FIX2Arr)
    swasout.FIX1 = FIX1Arr
    swasout.FIX2 = FIX2Arr    
    return swasout           
        