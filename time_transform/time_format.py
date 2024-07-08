# -*- coding: utf-8 -*-
"""
Created on Thu Apr 28 13:48:17 2022
# 2022Aug29 GPSFullWeek added in GpsTime
# 2022Jun21 change dt.now() to dt.utcnow()
@author: chcuk
"""
from datetime import datetime as dt
from datetime import timedelta


def str2dt(t):
    # input is float of timetag
    t_str = str(t)
    yea = int(t_str[:4])
    mon = int(t_str[4:6])
    day = int(t_str[6:8])
    hour = int(t_str[8:10])
    mins = int(t_str[10:12])
    secs = int(t_str[12:14])
    return dt(yea, mon, day, hour, mins, secs)
    
def strt2dt(strt,formatstr):
    # used for strt with any format
    return dt.strptime(strt,formatstr)
# Example:
# strt = '2022-08-16-01-00-00'
# formatstr = '%Y-%m-%d-%H-%M-%S'
# out = datetime.datetime(2022, 8, 16, 1, 0)   
    
def float2dt(fltt):
    fmt =  '%Y%m%d%H%M%S.0'
    return dt.strptime(str(fltt),fmt)   
# Example:
# fltt = 20221016000000.0
# formatstr = '%Y-%m-%d-%H-%M-%S'
# out = datetime.datetime(2022, 8, 16, 1, 0)    


def dt2float(dt):
    return float(
        "{}{:>02d}{:>02d}{:>02d}{:>02d}{:>02d}".format(
            dt.year, dt.month, dt.day, 
            dt.hour, dt.minute, dt.second
        ))
        
def dt2ymd(dt):
    return int(
        "{}{:>02d}{:>02d}".format(
            dt.year, dt.month, dt.day
        ))
        
def dt2ymdhms():
    return dt.now().strftime('%Y-%m-%d %H:%M:%S')

class ymd:
    def __init__(self, inputTime):
        self.year = inputTime.year
        self.month = inputTime.month
        self.day = inputTime.day
        self.hour = inputTime.hour
        self.minute = inputTime.minute
        self.second = inputTime.second
        self.microsecond = inputTime.microsecond
        self.datetime = inputTime

    def __sub__(self, ymd2):
        "Timedelta between 2 datetimes"
        tDelta = self.datetime - ymd2.datetime
        return tDelta

    def __add__(self, tDelta):
        newT = self.datetime + tDelta
        return ymd(newT)


class ydoy:
    def __init__(self, datetime):
        self.year = datetime.year
        year = datetime.year
        month = datetime.month
        day = datetime.day
        months = [0, 31, 59, 90, 120, 151, 181, 212, 243, 273, 304, 334]
        if 0 < month <= 12:
            sums = months[month - 1]
        else:
            print("month error")
        sums += day
        leap = 0
        if (year % 400 == 0) or ((year % 4) == 0) and (year % 100 != 0):
            leap = 1
        if (leap == 1) and (month > 2):
            sums += 1
        self.doy = sums
        self.datetime = datetime

    def __sub__(self, ydoy2):
        tdelta = self.datetime - ydoy2.datetime
        return tdelta

    def __add__(self, tDelta):
        newT = self.datetime + tDelta
        return ydoy(newT)


class utcTime:
    def __init__(self, inputTime=None):
        if type(inputTime) == dt:
            self.datetime = inputTime
        elif inputTime is None:
            #self.datetime = dt.now()
            self.datetime = dt.utcnow()

    def UTC2GPS(self):
        #y = self.datetime.year
        #m = self.datetime.month
        #leapSeconds = utcTime().get_gpsls(y, m)
        #newT = self.datetime + timedelta(seconds=leapSeconds)
        lenls = len(ls)
        for i in range(lenls):
            if(self.datetime > ls[i][0]):
                leapSeconds = ls[i][1]
                newT = self.datetime + timedelta(seconds=leapSeconds)
                return GpsTime(newT)
        #newT = self.datetime + timedelta(seconds=leapSeconds)
        return GpsTime(newT)

    def UTC2BDS(self):
        y = self.datetime.year
        m = self.datetime.month
        leapSeconds = utcTime().get_bdsls(y, m)
        newT = self.datetime + timedelta(seconds=leapSeconds)
        return BdsTime(newT)

    def UTC2GLO(self):
        newT = self.datetime + timedelta(hours=3)
        return GloTime(newT)

    def UTC2GAL(self):
        return self.UTC2GPS().GPS2GAL()

    def __str__(self,):
        return "{}".format(self.datetime)

    def __sub__(self, gpst2):
        tdelta = self.datetime - gpst2.datetime
        return tdelta

    def __add__(self, tDelta):
        newT = self.datetime + tDelta
        return GpsTime(newT)

    def __le__(self, gpst2):
        t1 = self.datetime
        t2 = gpst2.datetime
        return t1 <= t2

    def __lt__(self, gpst2):
        t1 = self.datetime
        t2 = gpst2.datetime
        return t1 < t2

    def __ge__(self, gpst2):
        t1 = self.datetime
        t2 = gpst2.datetime
        return t1 >= t2

    def __gt__(self, gpst2):
        t1 = self.datetime
        t2 = gpst2.datetime
        return t1 > t2
    
    def get_gpsls(self, year, month):
        #Function to get leap seconds since 1999. After 31st of December 1998
        #the leap seconds were 14. 
        #The function covers the updates after that time.
        #Ref:https://en.wikipedia.org/wiki/Leap_second
        if (year > 2005) & (year < 2009):
            ls = 14
        elif (year >= 2009) & (year < 2012):
            ls = 15
        elif year == 2012:
            if month < 7:
                ls = 15
            else:
                ls = 16
        elif (year > 2012) & (year < 2015):
            ls = 16
        elif year == 2015:
            if month < 7:
                ls = 16
            else:
                ls = 17
        elif year == 2016:
            if month < 7:
                ls = 17
            else:
                ls = 18
        elif year > 2016:
            ls = 18
        else:
            ls = 14
        return ls
    
    def get_bdsls(self, year, month):
        """
            BeiDou Time (BDT) is a continuous time scale starting at 0h UTC on 
            January 1st, 2006 and is synchronised with UTC within 100 ns<
            (modulo one second)
        """
        if (year > 2005) & (year < 2009):
            ls = 0
        elif (year >= 2009) & (year < 2012):
            ls = 1
        elif year == 2012:
            if month < 7:
                ls = 1
            else:
                ls = 2
        elif (year > 2012) & (year < 2015):
            ls = 2
        elif year == 2015:
            if month < 7:
                ls = 2
            else:
                ls = 3
        elif year == 2016:
            if month < 7:
                ls = 3
            else:
                ls = 4
        elif year > 2016:
            ls = 4
        else:
            ls = 0
        return ls


class GpsTime:
    # input datetime object must be GPS system time
    def __init__(self, inputTime=None):
        self.gps0 = dt(1980, 1, 6, 0, 0, 0)
        if type(inputTime) == list:
            if len(inputTime) == 3:
                GPSWeek0 = inputTime[0]
                # I GPSSOW0 can be float, can be negative
                #         can be larger than 85400
                GPSSOW0= inputTime[1]
                Rollover0 = inputTime[2]
                totalSec = (GPSWeek0 + Rollover0 * 1024) * 604800 + GPSSOW0
                self.datetime = self.gps0 + timedelta(seconds=totalSec)
            else:
                print("List length != 3")
        elif type(inputTime) == dt:
            self.datetime = inputTime
        elif inputTime is None:
            self.datetime = utcTime().UTC2GPS().datetime
            
        time_delta_s = (self.datetime - self.gps0).total_seconds()
        time_delta_d = (self.datetime - self.gps0).days
        self.GPSFullWeek = int(time_delta_d // 7)
        self.GPSDOW = int(time_delta_d % 7)
        tmp = time_delta_s - self.GPSFullWeek * 7 * 86400
        self.GPSSOW = int(tmp)
        self.GPSSOWFLOAT = tmp  
        self.Rollover = int(self.GPSFullWeek // 1024)
        self.GPSWeek = int(self.GPSFullWeek % 1024)

    def __str__(self,):
        return "{}".format(self.datetime)

    def __sub__(self, gpst2):
        tdelta = self.datetime - gpst2.datetime
        return tdelta

    def __add__(self, tDelta):
        newT = self.datetime + tDelta
        return GpsTime(newT)

    def __le__(self, gpst2):
        t1 = self.datetime
        t2 = gpst2.datetime
        return t1 <= t2

    def __lt__(self, gpst2):
        t1 = self.datetime
        t2 = gpst2.datetime
        return t1 < t2

    def __ge__(self, gpst2):
        t1 = self.datetime
        t2 = gpst2.datetime
        return t1 >= t2

    def __gt__(self, gpst2):
        t1 = self.datetime
        t2 = gpst2.datetime
        return t1 > t2
    
    def __eq__(self,gpst2):
        t1 = self
        t2 = gpst2
        
        if type(t1) != GpsTime:
            if not type(t1) == dt:
                t1 = t1.datetime
            else: print('Warning: not GpsTime object!')
        else: t1 = t1.datetime
            
        if type(t2) == GpsTime:
            t2 = t2.datetime
            
        elif type(t2) == GloTime:
            t2 = t2.GLO2GPS().datetime
            
        elif type(t2) == BdsTime:
            t2 = t2.BDS2GPS().datetime
            
        elif type(t2) == GalTime:
            t2 = t2.GAL2GPS().datetime
            
        return t1 == t2

    def GPS2UTC(self):
        # y = self.datetime.year
        # m = self.datetime.month
        # leapSeconds = utcTime().get_gpsls(y, m)
        # newT = self.datetime + timedelta(seconds=-leapSeconds)
        lenls = len(gpsls)
        for i in range(lenls):
            if(self.datetime > gpsls[i][0]):
                leapSeconds = gpsls[i][1]
                newT = self.datetime + timedelta(seconds=-leapSeconds)
                return utcTime(newT)
        return utcTime(newT)

    def GPS2BDS(self,):
        # S1 BDS total seconds from the begin of BDS time
        #     BDS week * secPerWeek + sow
        # S2 total seconds from GPS begin time to BDS begin time
        # GPS start starts at 0h UTC (midnight) of January 5th to 6th 1980 (6. 0).
        #     GPS week(1356), sow(14) at the begining time of BDS (2006 Jan 01 0h UTC)
        #     totalsecdiffGB = weekDif * secPerWeek + 14
        #     Note 14 also can be calculated by secLeapGPS - secLeapBDS
        # S3 total seconds (S1 + S2)
        #    BDS week * secPerWeek + sow + weekDif * secPerWeek + 14

        diff = self.datetime - GpsTime([1356, 14, 0]).datetime
        totalSecs = diff.total_seconds()
        totalDays = diff.days

        BDSWeek = int(totalDays // 7)
        BDSSOW = totalSecs - BDSWeek * 7 * 86400
        Rollover = int(BDSWeek // 1024)
        BDSWeek = BDSWeek - (Rollover * 1024)

        return BdsTime([BDSWeek, BDSSOW, Rollover])

    def GPS2GAL(self):
        diff = self.datetime - GpsTime(dt(1999, 8, 22, 0, 0, 0)).datetime
        totalSecs = diff.total_seconds()
        totalDays = diff.days

        GALWeek = int(totalDays // 7)
        GALSOW = totalSecs - GALWeek * 7 * 86400
        Rollover = int(GALWeek // 1024)
        GALWeek = GALWeek - (Rollover * 1024)

        return GalTime([GALWeek, GALSOW, Rollover])

    def GPS2GLO(self):
        temp = self.GPS2UTC().datetime
        return GloTime(temp + timedelta(hours=3))
    
    def fullweek(self,week,inputTime = None):
        # I: datetime in GPS, for offline
        # I: Week, 0-1023
        # O: adjusted gps week number with rollover
        fullweek = week + self.Rollover*1024
        return fullweek 
    
    def adjweek(self,sow,inputTime= None):
        # Ref: RTKLIB_2.4.2\src\rtcm3.c\adjweek
        #     inputTime: datetime in GPS, for offline
        # adjust weekly rollover of GPS time
        #= without knowing the week number, 
        #= return full gpsT based on the sow and current time
        #= assume input sow is very close to the current time
        if(inputTime is None):
            ct = self.datetime
        else:
            ct = inputTime
        gpst = GpsTime(ct)
        sowct = gpst.GPSSOW
        if(sow < sowct -302400.0):
            sow += 604800
        elif (sow > sow +302400):
            sow -= 604800
        newT = GpsTime([gpst.GPSWeek,sow,gpst.Rollover])        
        return newT


class BdsTime:
    # input datetime object must be BDS system time
    def __init__(self, inputTime=None):

        self.bds0 = dt(2006, 1, 1, 0, 0, 0)
        if type(inputTime) == dt:
            self.datetime = inputTime                        
        elif type(inputTime) == list:
            if len(inputTime) == 3:
                BDSWeek0 = inputTime[0]
                BDSSOW0 = inputTime[1]
                Rollover0 = inputTime[2]
                bds0 = dt(2006, 1, 1, 0, 0, 0)
                totalSec = (BDSWeek0 + Rollover0 * 1024) * 604800 + BDSSOW0
                self.datetime = bds0 + timedelta(seconds=totalSec)                       
            else:
                print("List length != 3")
        elif inputTime is None:
            #self.datetime = dt.now()
            #self.datetime = dt.utcnow()
            t0 = dt.utcnow()
            ls = utcTime().get_bdsls(t0.year,t0.month)
            self.datetime = t0 + timedelta(seconds = ls)
            #self.datetime = utcTime().UTC2BDS()
        time_delta_s = (self.datetime - self.bds0).total_seconds()
        time_delta_d = (self.datetime - self.bds0).days
        self.BDSWeek = int(time_delta_d // 7)
        self.BDSDOW = int(time_delta_d % 7)
        tmp = time_delta_s - self.BDSWeek * 7 * 86400
        self.BDSSOW = int(tmp)
        self.BDSSOWFLOAT = tmp
        self.Rollover = int(self.BDSWeek // 1024)
        self.BDSWeek = int(self.BDSWeek % 1024)

    def BDS2UTC(self):
        y = self.datetime.year
        m = self.datetime.month
        leapSeconds = utcTime().get_bdsls(y, m)
        newT = self.datetime + timedelta(seconds=-leapSeconds)
        return utcTime(newT)

    

    def BDS2GPS(self,):
        # S1 BDS total seconds from the begin of BDS time
        #     BDS week * secPerWeek + sow
        # S2 total seconds from GPS begin time to BDS begin time
        # GPS start starts at 0h UTC (midnight) of January 5th to 6th 1980 (6. 0).
        #     GPS week(1356), sow(14) at the begining time of BDS (2006 Jan 01 0h UTC)
        #     totalsecdiffGB = weekDif * secPerWeek + 14
        #     Note 14 also can be calculated by secLeapGPS - secLeapBDS
        # S3 total seconds (S1 + S2)
        #    BDS week * secPerWeek + sow + weekDif * secPerWeek + 14
        BdsTime0inGPS = GpsTime([1356, 14, 0])  # start of bds time
        bdsWeek = self.BDSWeek
        bdsSOW = self.BDSSOW
        bdsWeek = bdsWeek + self.Rollover * 1024
        secPerWeek = 604800
        totalSecs = bdsWeek * secPerWeek + bdsSOW
        newGpsTime = BdsTime0inGPS + timedelta(seconds=totalSecs)
        return newGpsTime

    def __str__(self,):
        return "{}".format(self.datetime)

    def __sub__(self, gpst2):
        tdelta = self.datetime - gpst2.datetime
        return tdelta

    def __add__(self, tDelta):
        newT = self.datetime + tDelta
        return BdsTime(newT)

    def __le__(self, gpst2):
        t1 = self.datetime
        t2 = gpst2.datetime
        return t1 <= t2

    def __lt__(self, gpst2):
        t1 = self.datetime
        t2 = gpst2.datetime
        return t1 < t2

    def __ge__(self, gpst2):
        t1 = self.datetime
        t2 = gpst2.datetime
        return t1 >= t2

    def __gt__(self, gpst2):
        t1 = self.datetime
        t2 = gpst2.datetime
        return t1 > t2
    
    def __eq__(self,gpst2):
        t1 = self
        t2 = gpst2
        
        if type(t1) != BdsTime:
            if not type(t1) == dt:
                t1 = t1.datetime
            else: print('Warning: not BdsTime object!')
        else: t1 = t1.datetime
            
        if type(t2) == GpsTime:
            t2 = t2.GPS2BDS().datetime
            
        elif type(t2) == GloTime:
            t2 = t2.GLO2GPS().GPS2BDS().datetime
            
        elif type(t2) == BdsTime:
            t2 = t2.datetime
            
        elif type(t2) == GalTime:
            t2 = t2.GAL2GPS().GPS2BDS().datetime
            
        return t1 == t2

    def adjBDSweek(self,week):
        # Ref: RTKLIB_2.4.2\src\rtcm3.c\adjbdtweek
        # add 1024 if Rollover is 1
        weekct = self.BDSWeek + self.Rollover * 1024
        if(weekct < 1):
            weekct = 1 # use 2006/1/1 if time is earlier than 2006/1/1
        else:
            week = week + int((weekct-week + 512)/1024)*1024
            #week = week + self.Rollover * 1024
        return week
    
    def adjweek(self,sow,inputTime=None):
        # Ref: RTKLIB_2.4.2\src\rtcm3.c\adjweek
        #     inputTime: datetime in GPS, for offline
        #= return new full gpsT based on sow and current time
        #= assume sow is close to the current time
        if inputTime is None:
            bdst = BdsTime(self.datetime)
        else:
            bdst = GpsTime(inputTime).GPS2BDS()
        # bdst = BdsTime(ct)
        sowct = bdst.BDSSOW
        if(sow < sowct -302400.0):
            sow += 604800
        elif (sow > sow +302400):
            sow -= 604800
        newT = BdsTime([bdst.BDSWeek,sow,bdst.Rollover]).BDS2GPS()        
        return newT

class GalTime:
    # input datetime object must be GAL system time
    def __init__(self, inputTime=None):
        self.gal0 = dt(1999, 8, 21, 23, 59, 47)
        if inputTime == None:
            #self.datetime = dt.now()   # local time
            #self.datetime = dt.utcnow() # utc time
            self.datetime = utcTime().UTC2GAL().datetime # GAL time
        elif type(inputTime) == list:
            if len(inputTime) == 3:
                GALWeek0 = inputTime[0]
                GALSOW0 = inputTime[1]
                Rollover0 = inputTime[2]
                totalSec = (GALWeek0 + Rollover0 * 1024) * 604800 + GALSOW0
                self.datetime = self.gal0 + timedelta(seconds=totalSec)
            else:
                print("List length != 3")
        elif type(inputTime) == dt:
            self.datetime = inputTime            
        time_delta_s = (self.datetime - self.gal0).total_seconds()
        time_delta_d = (self.datetime - self.gal0).days
        self.GALWeek = int(time_delta_d // 7)
        self.GALDOW = int(time_delta_d % 7)
        tmp = time_delta_s - self.GALWeek * 7 * 86400
        self.GALSOW = int(tmp)
        self.GALSOWFLOAT = tmp
        self.Rollover = int(self.GALWeek // 1024)
        self.GALWeek = int(self.GALWeek % 1024)


    def GAL2UTC(self):
        return self.GAL2GPS().GPS2UTC()

    def GAL2GPS(self):
        gal0 = GpsTime(dt(1999, 8, 21, 23, 59, 47))
        secDifGPS2GST = (((self.Rollover*1024) +self.GALWeek) * 604800) + self.GALSOW + 13
        newT = gal0.datetime + timedelta(seconds=secDifGPS2GST)
        return GpsTime(newT)

    def __str__(self,):
        return "{}".format(self.datetime)

    def __sub__(self, gpst2):
        tdelta = self.datetime - gpst2.datetime
        return tdelta

    def __add__(self, tDelta):
        newT = self.datetime + tDelta
        return GalTime(newT)

    def __le__(self, gpst2):
        t1 = self.datetime
        t2 = gpst2.datetime
        return t1 <= t2

    def __lt__(self, gpst2):
        t1 = self.datetime
        t2 = gpst2.datetime
        return t1 < t2

    def __ge__(self, gpst2):
        t1 = self.datetime
        t2 = gpst2.datetime
        return t1 >= t2

    def __gt__(self, gpst2):
        t1 = self.datetime
        t2 = gpst2.datetime
        return t1 > t2
    
    def __eq__(self,gpst2):
        t1 = self
        t2 = gpst2
        
        if type(t1) != GalTime:
            if not type(t1) == dt:
                t1 = t1.datetime
            else: print('Warning: not GalTime object!')
        else: t1 = t1.datetime
            
        if type(t2) == GpsTime:
            t2 = t2.GPS2GAL().datetime
            
        elif type(t2) == GloTime:
            t2 = t2.GLO2GPS().GPS2GAL().datetime
            
        elif type(t2) == BdsTime:
            t2 = t2.BDS2GPS().GPS2GAL().datetime
            
        elif type(t2) == GalTime:
            t2 = t2.datetime
            
        return t1 == t2

    def adjweek(self,sow,inputTime=None):
        # Ref: RTKLIB_2.4.2\src\rtcm3.c\adjweek
        #     inputTime: datetime in GPS, for offline
        # get full GpsTime based on sow and current date
        # assume sow is very close to the current second
        # ct = curent time
        if inputTime is None:        
            ct = self.datetime
        else:
            ct = inputTime
        gpst = GpsTime(ct)
        sowct = gpst.GPSSOW
        if(sow < sowct -302400.0):
            sow += 604800
        elif (sow > sow +302400):
            sow -= 604800
        newT = GpsTime([gpst.GPSWeek,sow,gpst.Rollover])        
        return newT


class GloTime:
    def __init__(self, inputTime=None):
        # the input time is GLONASS time (MOSCOW)
        # The first year of the first current four-year interval corresponds
        # to 1996
        self.gloref = dt(1996, 1, 1, 0, 0, 0)  
        if type(inputTime) == dt:
            self.datetime = inputTime
        elif type(inputTime) == list:
            if len(inputTime) == 3:
                period = inputTime[0]  # start from 1996
                dop = inputTime[1]
                sod = inputTime[2]
                # valid until 2100 pls update :D
                totalSec = (((4 * 365) + 1) * (period - 1) + (dop - 1)) * 86400 + sod
                self.datetime = self.gloref + timedelta(seconds=totalSec)
        elif inputTime is None:
            #self.datetime = dt.now() + timedelta(hours = 3)
            self.datetime = dt.utcnow() + timedelta(hours = 3)
        diff = self.datetime - self.gloref
        # 1461 days in each period
        self.Period = (diff.days // 1461) + 1 # start from 1
        self.DOP = (diff.days - (self.Period-1) *1461) + 1 # start from 1
        self.SOD = diff.seconds 

    def GLO2UTC(self):
        newT = self.datetime + timedelta(hours=-3)
        return utcTime(newT)

    def GLO2GPS(self):
        y = self.datetime.year
        m = self.datetime.month
        leapSeconds = utcTime().get_gpsls(y, m)
        newT = self.datetime + timedelta(seconds=leapSeconds, hours=-3)
        return GpsTime(newT)

    def __str__(self,):
        return "{}".format(self.datetime)

    def __sub__(self, gpst2):
        tdelta = self.datetime - gpst2.datetime
        return tdelta

    def __add__(self, tDelta):
        newT = self.datetime + tDelta
        return GloTime(newT)

    def __le__(self, gpst2):
        t1 = self.datetime
        t2 = gpst2.datetime
        return t1 <= t2

    def __lt__(self, gpst2):
        t1 = self.datetime
        t2 = gpst2.datetime
        return t1 < t2

    def __ge__(self, gpst2):
        t1 = self.datetime
        t2 = gpst2.datetime
        return t1 >= t2

    def __gt__(self, gpst2):
        t1 = self.datetime
        t2 = gpst2.datetime
        return t1 > t2
    
    def __eq__(self,gpst2):
        t1 = self
        t2 = gpst2
        
        if type(t1) != GloTime:
            if not type(t1) == dt:
                t1 = t1.datetime
            else: print('Warning: not GloTime object!')
        else: t1 = t1.datetime
            
        if type(t2) == GpsTime:
            t2 = t2.GPS2GLO().datetime
            
        elif type(t2) == GloTime:
            t2 = t2.datetime
            
        elif type(t2) == BdsTime:
            t2 = t2.BDS2GPS().GPS2GLO().datetime
            
        elif type(t2) == GalTime:
            t2 = t2.GAL2GPS().GPS2GLO().datetime
            
        return t1 == t2

    def adjday(self,sod,inputTime=None):
        # Ref:  \RTKLIB-rtklib_2.4.3\src\rtkcmn.c\adjday_glot
        # transfer sod to GPS Time based on current time
        # In: sod: second of day, GLONASS time
        #     inputTime: datetime in GPS, for offline
        # Out: newT: GpsTime
        # S1: UTC -> glo.Period, glo.DOP,glo.SOD
        # S2: Compare SOD with glo.SOD, get SOD2, check day rollover
        # S3: t3 = GloTime(glo.Period,glo.DOP,SOD2)
        # S4: transfer t3 to gps

        if(inputTime is None):
            glot = GloTime(self.datetime) # GloTime
        else:
            glot = GpsTime(inputTime).GPS2GLO()
        sodct = glot.SOD
        #sowct = int(glot.GLOSOW)
        
        #week = glot.GLOWeek  # glonass time week
        #= sowct = sow_ndays + sodct 
        #=       = ndays*86400 + sodct
        #= ndays = sowct//86400 
        #sodct = int(sowct)%86400  # also sodct = sowct - ndays* 86400
        #sow_ndays = sowct - sodct  # also sow = ndays * 86400
        # Note: assume SODCT is close to SOD
        if(sod < sodct -43200):
            # sodct > 43200
            # sod < 43200
            # |---   |    .SODCT.|.SOD.|...   |
            # 0    43200       86400               
            sod += 86400
        elif(sod > sodct + 43200):
            # sodct < 43200
            # sod > 43200
            sod -= 86400
        newT = GloTime([glot.Period,glot.DOP,sod])
        newgpsT = newT.GLO2GPS()   
        return newgpsT


def mjd(inputTime):
    # inputTime is UTCTime
    mjd0 = dt(1858, 11, 17, 0, 0, 0)
    temp = inputTime - mjd0
    days, seconds = temp.days, temp.seconds
    MJD = days + seconds // 86400
    return MJD

def mjdR(inputTime):
    # inputTime is UTCTime
    #= MJD is real, not integer
    mjd0 = dt(1858, 11, 17, 0, 0, 0)
    temp = inputTime - mjd0
    days, seconds = temp.days, temp.seconds
    MJD = days + seconds / 86400
    return MJD

def jd2MJD(jd):
    mjd = jd - 2400000.5
    return mjd


def mjd2JD(MJD):
    JD = MJD + 2400000.5
    return JD


def dayOfYear(inputTime):
    """
    Parameters
    ----------
    date : datetime.datetime
        date in datetime format.

    Returns
    -------
    sum : int
        day of year.
    """
    year = inputTime.year
    month = inputTime.month
    day = inputTime.day
    months = [0, 31, 59, 90, 120, 151, 181, 212, 243, 273, 304, 334]
    if 0 < month <= 12:
        doy = months[month - 1]
    else:
        print("month error")
    doy += day
    leap = 0
    if (year % 400 == 0) or ((year % 4) == 0) and (year % 100 != 0):
        leap = 1
    if (leap == 1) and (month > 2):
        doy += 1
    return doy

#/* leap seconds (y,m,d,h,m,s,utc-gpst) */
ls=[
    [dt(2017,1,1,0,0,0),18],
    [dt(2015,7,1,0,0,0),17],
    [dt(2012,7,1,0,0,0),16],
    [dt(2009,1,1,0,0,0),15],
    [dt(2006,1,1,0,0,0),14],
    [dt(1999,1,1,0,0,0),13],
    [dt(1997,7,1,0,0,0),12],
    [dt(1996,1,1,0,0,0),11],
    [dt(1994,7,1,0,0,0),10],
    [dt(1993,7,1,0,0,0), 9],
    [dt(1992,7,1,0,0,0), 8],
    [dt(1991,1,1,0,0,0), 7],
    [dt(1990,1,1,0,0,0), 6],
    [dt(1988,1,1,0,0,0), 5],
    [dt(1985,7,1,0,0,0), 4],
    [dt(1983,7,1,0,0,0), 3],
    [dt(1982,7,1,0,0,0), 2],
    [dt(1981,7,1,0,0,0), 1],
    ]   

gpsls=[
    [dt(2017,1,1,0,0,0)+timedelta(seconds = 18),18],
    [dt(2015,7,1,0,0,0)+timedelta(seconds = 17),17],
    [dt(2012,7,1,0,0,0)+timedelta(seconds = 16),16],
    [dt(2009,1,1,0,0,0)+timedelta(seconds = 15),15],
    [dt(2006,1,1,0,0,0)+timedelta(seconds = 14),14],
    [dt(1999,1,1,0,0,0)+timedelta(seconds = 13),13],
    [dt(1997,7,1,0,0,0)+timedelta(seconds = 12),12],
    [dt(1996,1,1,0,0,0)+timedelta(seconds = 11),11],
    [dt(1994,7,1,0,0,0)+timedelta(seconds = 10),10],
    [dt(1993,7,1,0,0,0)+timedelta(seconds = 9), 9],
    [dt(1992,7,1,0,0,0)+timedelta(seconds = 8), 8],
    [dt(1991,1,1,0,0,0)+timedelta(seconds = 7), 7],
    [dt(1990,1,1,0,0,0)+timedelta(seconds = 6), 6],
    [dt(1988,1,1,0,0,0)+timedelta(seconds = 5), 5],
    [dt(1985,7,1,0,0,0)+timedelta(seconds = 4), 4],
    [dt(1983,7,1,0,0,0)+timedelta(seconds = 3), 3],
    [dt(1982,7,1,0,0,0)+timedelta(seconds = 2), 2],
    [dt(1981,7,1,0,0,0)+timedelta(seconds = 1), 1],
    ]   

def gpsls_from_GpsTime(inputTime):
    # inputTime is GpsTime
    # y = self.datetime.year
    # m = self.datetime.month
    # leapSeconds = utcTime().get_gpsls(y, m)
    lenls = len(gpsls)
    for i in range(lenls):
        if(inputTime > gpsls[i][0]):
            leapseconds = gpsls[i][1]
            return
    return leapseconds