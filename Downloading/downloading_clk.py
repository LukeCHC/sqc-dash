# -*- coding: utf-8 -*-
"""
Created on Tue Aug 23 08:30:31 2022

@author: Zoe Chen
"""
import FTP
from TimeTrans.timeFormat import dayOfYear
from TimeTrans.timeFormat import gpsTime
from datetime import datetime as dt
import os
from TOOLS import decompress

class downloading_clk:
    def __init__(self,locDir,date):
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
            

    def clkF(self):
        IP   = 'http://navigation-office.esa.int'
        tarF ='ESA0MGNFIN_'+self.year +self.doy + '0000_01D_30S_CLK.CLK.gz'
        tarN ='ESA0MGNFIN_'+self.year +self.doy + '0000_01D_30S_CLK.CLK'
        if not os.path.exists(self.locDir + "/" + tarN):
            try:
                remotePath = '{}{}{}'.format(
                    '/products/gnss-products/', self.GPSWeek, '/')
                a = FTP.URLRun(self.locDir, IP, remotePath).url_download(tarF)
                if(a):
                    decompress.dGZIP(
                    self.locDir + "/" + tarF, self.locDir + "/" + tarN)
                    return self.locDir + "/" + tarN
                else:
                    return False
            except:
                return False
        return self.locDir + "/" + tarN
    
    
    def clkR(self):
        IP   = 'igs.ign.fr'
        tarF ='GFZ0MGXRAP_'+self.year +self.doy + '0000_01D_30S_CLK.CLK.gz'
        tarN ='GFZ0MGXRAP_'+self.year +self.doy + '0000_01D_30S_CLK.CLK'
        if not os.path.exists(self.locDir + "/" + tarN):
            try:
                remotePath = '{}{}{}'.format(
                    '/pub/igs/products/mgex/', self.GPSWeek, '/')
                a = FTP.FTPRun(self.locDir, IP, "", "", remotePath).ftp_download(tarF)
                if(a):
                    decompress.dGZIP(
                    self.locDir + "/" + tarF, self.locDir + "/" + tarN)
                    return self.locDir + "/" + tarN
                else:
                    return False
            except:
                return False
        return self.locDir + "/" + tarN