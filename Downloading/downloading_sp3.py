# -*- coding: utf-8 -*-
"""
Created on Tue Aug 23 08:30:09 2022

@author: chcuk
"""
import FTP
from TimeTrans.timeFormat import gpsTime,dayOfYear
from datetime import datetime as dt
import os
from TOOLS import decompress

class downloading_sp3:
    def __init__(self, locDir,date):
        self.locDir = locDir
        if type(date) == dt:
             gpsT = gpsTime(date)
             self.year = "%04d" % gpsT.datetime.year
             self.month = "%02d" % gpsT.datetime.month
             self.day = "%02d" % gpsT.datetime.day
             self.doy = "%03d" % dayOfYear(date)
             self.GPSWeek = "%04d" % gpsT.GPSFullWeek
             self.dow = "%d" % gpsT.GPSDOW
        else:
            print('date should be datetime')
                 

    def sp3R(self):
       
        IP = "igs.ign.fr"
        tarF = "{}{}{}{}".format(
            "GFZ0MGXRAP_", self.year, self.doy, "0000_01D_05M_ORB.SP3.gz"
        )
       
        tarN = "{}{}{}{}".format(
            "GFZ0MGXRAP_", self.year, self.doy, "0000_01D_05M_ORB.SP3"
        )
        if not os.path.exists(self.locDir + "/" + tarN):
            remotePath = "{}{}{}".format("/pub/igs/products/mgex/", self.GPSWeek, "/")
            a = FTP.FTPRun(self.locDir, IP, "", "", remotePath).ftp_download(tarF)
            decompress.dGZIP(
                self.locDir + "/" + tarF, self.locDir + "/" + tarN
            )
           
            bIP = "gdc.cddis.eosdis.nasa.gov"
            if not a:
                try: 
                    remotePath = "{}{}{}".format("/pub/gps/products/", self.GPSWeek, "/")
                    tarF = f"igr{self.GPSWeek}{self.dow}.sp3.Z"
                    FTP.FTPRun(self.locDir, bIP, "", "", remotePath).ftps_download(tarF)
                    decompress.dGZIP(
                        self.locDir + "/" + tarF, self.locDir + "/" + tarN
                    )
                    return self.locDir + "/" + tarN
                except:
                    return False
            else: return self.locDir + "/" + tarN
        else: return self.locDir + "/" + tarN
    
    def sp3F(self):
        IP = "http://navigation-office.esa.int"
        tarF = "{}{}{}{}".format(
            "ESA0MGNFIN_", self.year, self.doy, "0000_01D_05M_ORB.SP3.gz"
        )
        tarN = "{}{}{}{}".format(
            "ESA0MGNFIN_", self.year, self.doy, "0000_01D_05M_ORB.SP3"
        )
        if not os.path.exists(self.locDir + "/" + tarN):
            remotePath = "{}{}{}".format("/products/gnss-products/", self.GPSWeek, "/")
            a = FTP.URLRun(self.locDir, IP, remotePath).url_download(tarF)
            decompress.dGZIP(
                self.locDir + "/" + tarF, self.locDir + "/" + tarN
            )
            bIP = "gdc.cddis.eosdis.nasa.gov"
        
            if not a:
                try:
                    remotePath = "{}{}{}".format("/pub/gps/products/mgex/", self.GPSWeek, "/")
                    FTP.FTPRun(self.locDir, bIP, "", "", remotePath).ftps_download(tarF)
                    decompress.dGZIP(
                        self.locDir + "/" + tarF, self.locDir + "/" + tarN
                    )
                    return self.locDir + "/" + tarN
                except:
                    return False
            else: return self.locDir + "/" + tarN
        else: return self.locDir + "/" + tarN    


#dates = dt(2021,3,19) 
#IFP = r"C:\Work\test"  
#a = downloading_sp3(IFP,dates).sp3F()
#b = downloading_sp3(IFP,dates).sp3R()           