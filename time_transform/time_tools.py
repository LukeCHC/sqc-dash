from datetime import datetime as dt
from datetime import timedelta

class timeTool:
    secondsPerDay = 86400
    secondsPerWeek = 604800
    
    def inRangeOf (tCalc, stTime, endTime, mode=None):
        
        parsedArgs = [tCalc, stTime, endTime]
        if list(map(type, parsedArgs)).count(dt) != len(parsedArgs):
            raise TypeError('only Datetime objects are expected')
        
        if mode == None:
            mode = 0       
        
        if (endTime < stTime):
            temp = stTime
            stTime = endTime
            endTime = temp            
        
        if mode == 0:
            if tCalc > stTime and tCalc < endTime:                
                return True
            else: 
                return False
            
        elif mode == 1:
            if tCalc >= stTime and tCalc <= endTime:                
                return True
            else: 
                return False
        
def sliceDaily(stTime, endTime):
    
    stEpoch = dt(stTime.year, stTime.month, stTime.day, 0, 0, 0)
    endEpoch = dt(
    endTime.year, endTime.month, endTime.day, 0, 0, 0
    ) + timedelta(days=1)
    
    nDays = (endEpoch - stEpoch).days
    
    calcRange = []
    
    for i in range(nDays):
 
        todayRange = [
            stEpoch + timedelta(days=i),
            stEpoch + timedelta(days=i + 1, seconds=-1),
        ]
        
        if i == 0:  # find calculation period daily
            if nDays == 1:
                startCalc = stTime
                endCalc = endTime
            else:
                startCalc = stTime
                endCalc = todayRange[1]
        else:
            startCalc = todayRange[0]
            if i == nDays - 1:
                endCalc = endTime
            else:
                endCalc = todayRange[1]

        calcRange.append([startCalc, endCalc])
    
    return calcRange
        
def doy2ymd(year,doy):
    if(year < 100):
        ymd = dt(2000 + year,1,1)+ timedelta(days = doy-1)
    #elif(year>2000):
    else:
        ymd = dt(year,1,1)+ timedelta(days = doy-1)
    return ymd    
            
            
            
                
        
        
    
    
    