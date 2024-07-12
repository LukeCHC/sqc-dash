# -*- coding: utf-8 -*-
"""
Created on Tue Jun  7 08:47:43 2022

@author: Zoe Chen
"""
import time
from TimeTrans.timeFormat import gpsTime
from datetime import datetime as dt
from datetime import timedelta
from threading import Timer


def alarm(INTERVAL,SETALARM):
    ct = gpsTime()
    alarm_flag = False
    oldt0 = ct.GPSSOW
    First = True
    while True:
        if(oldt0 != ct.GPSSOW):
             First = True
        while First:
            t0 = ct.GPSSOWFLOAT % INTERVAL
            diff = t0 - SETALARM
            if( (diff >0) &  (diff <0.1)):
                alarm_flag = True
                First = False
                oldt0 = ct.GPSSOW
                #'Do something'
                print('   CT0',ct.GPSSOW,diff)
                break
            time.sleep(0.01)
            ct = gpsTime()
        time.sleep(0.01)
        ct = gpsTime()
    return alarm_flag


def alarm_v1(EYMD,INTERVAL,SETALARM):
    # Input: INTERVAL,SETALARM
    # Example: INTERVAL = 5,SETALARM = 1
    #          flag = true at 1s every 5 seconds
    ct = gpsTime()
    alarm_flag = False
    oldt0 = ct.GPSSOW
    First = True
    while ct.datetime < EYMD:
        if(oldt0 != ct.GPSSOW):
             First = True
        while First:
            t0 = ct.GPSSOWFLOAT % INTERVAL
            diff = t0 - SETALARM
            if( (diff >0) &  (diff <0.1)):
                alarm_flag = True
                First = False
                oldt0 = ct.GPSSOW
                print('   CT0',ct.GPSSOW,diff)
                break
            time.sleep(0.01)
            ct = gpsTime()
        time.sleep(0.01)
        ct = gpsTime()
    return alarm_flag


# Example
def hello():
    print("hello, world")
    
EYMD = dt.now() + timedelta(minutes = 2)
INTERVAL = 5
SETALARM = 1
CT = gpsTime()
while (CT.datetime < EYMD):
    ct = gpsTime()
    EYMD0 = ct + timedelta(seconds= INTERVAL)
    alarmflag = alarm(EYMD0.datetime,INTERVAL,SETALARM)
    if(alarmflag):
        print('CT1',gpsTime().GPSSOW)
        t = Timer(4,hello)
        t.start()
        #time.sleep(4) # processing time needed
        CT = gpsTime()
        
#Output
# CT1 207021
#    CT0 207021 0.0326540470123291
#    CT0 207026 0.00023102760314941406
# CT1 207026
#    CT0 207026 0.06254410743713379
#    CT0 207031 0.010157108306884766
# CT1 207031
#    CT0 207031 0.08839011192321777
#    CT0 207036 0.014087915420532227
# CT1 207036
#    CT0 207041 0.0026841163635253906
# CT1 207041
#    CT0 207046 0.0013461112976074219
# CT1 207046
#    CT0 207051 0.0003299713134765625
# CT1 207051
#    CT0 207056 0.014578104019165039

# Time.sleep(4)
# CT1 207131
#    CT0 207136 0.010411977767944336
#    CT0 207141 0.009500980377197266
# CT1 207141
#    CT0 207146 0.012152910232543945
#    CT0 207151 0.00430607795715332
# CT1 207151
#    CT0 207156 0.005305051803588867
#    CT0 207161 0.003961086273193359