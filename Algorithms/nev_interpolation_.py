# -*- coding: utf-8 -*-
"""
Created on Tue Aug 23 15:17:26 2022

@author: chcuk
"""

class OldInterpolation:
    def __init__(self):
       
        pass

    def nevCalc(self, winx, winy, xPoint):
        """
        Finds an interpolated value using Neville's algorithm.
        This function is best called by neville or nevSing
        Input
          winx: input x's in a list of size n
          winy: input y's in a list of size n
          x: the x value used for interpolation
        Output
          p[0]: the polynomial of degree n
        """
        n = len(winx)
        p = n*[0]
        for k in range(n):
            for i in range(n-k):
                if k == 0:
                    p[i] = winy[i]
                else:
                    p[i] = ((xPoint-winx[i+k])*p[i]+ \
                            (winx[i]-xPoint)*p[i+1])/ \
                            (winx[i]-winx[i+k])
        return p[0]    
    
    def nevSing(self,winx, winy, xPoint):
    
        x = [int(i.timestamp()) - 1658534400 for i in winx] #convert tt to int 
        poi = int(xPoint.timestamp()) - 1658534400 
        
        return self.nevCalc(x,winy, poi )
    
    def nevSingR(self,winx, winy, xPoint):
        #= x is not int 
        x = [i.timestamp() - 1658534400 for i in winx] #convert tt to int 
        poi = xPoint.timestamp() - 1658534400 
        return self.nevCalc(x,winy, poi)
            
    def neville(self, x, y, poi, order):
        """ 
        USED FOR MULTIPLE POI TO GENERATE ROLLING WINDOW
        x: list of pandas timetags (pd.to_datetime)
        poi: points of interpolation (list of timetags)
        """
        self.x = x
        self.y = y
        self.poi = poi
        """POI = points of interpolation"""
        
        if len(x) != len(y):
            raise Exception("len x and y mismatch")
            
        n = order//2 
        
        if not (x[n] < poi[0]) or not (x[-n] > poi[-1]):
            raise Exception("x values do not span far enough past POI") 
            
        x = [float(i.timestamp()) - 1658534400 for i in x] #convert tt to int 
        poi = [float(i.timestamp()) - 1658534400 for i in poi]
    
        yp = []
        i = 0 # poi
        j = 0 #x
        #loop creates rolling window 
        while i < len(poi):
            if x[j] <= poi[i] and poi[i] < x[j+1]:
                if x[j] != poi[i]:
                    if j+n+1 >= len(x):
                        raise Exception("x values do not span far enough past POI, losing accuracy")
                    winX = x[j-n:j+n+1]
                    winY = y[j-n:j+n+1]
                    yp.append(self.nevCalc(winX, winY, poi[i]))
                    i+=1
                else:
                    yp.append(y[j])
                    i+=1
            else:
                j+=1
    
        return yp

#%%

import time
from datetime import datetime, timedelta
import numpy as np
import cProfile


def test_old_interpolation():
    start_time_perf = time.time()
    
    # Create a much larger list of x and y values
    start_time_dt = datetime(2023, 1, 1, 12, 0, 0)
    x = [start_time_dt + timedelta(seconds=i) for i in range(200000)]
    y = [i**2 for i in range(200000)]
    
    # Create an instance of the OldInterpolation class
    interpolator = OldInterpolation()

    # Test nevSing method with a larger window
    win_x = [start_time_dt + timedelta(seconds=i) for i in range(1000, 1010)]
    win_y = [i**2 for i in range(1000, 1010)]
    x_point = start_time_dt + timedelta(seconds=1005)
    interpolated_value = interpolator.nevSing(win_x, win_y, x_point)
    assert round(interpolated_value, 2) == 1005**2

    # Test neville method with a much larger order and more POI
    poi = [start_time_dt + timedelta(seconds=i) for i in range(100, 190000)]
    order = 20  # Updated order
    interpolated_values = interpolator.neville(x, y, poi, order)
    expected_values = [i**2 for i in range(100, 190000)]
    np.testing.assert_allclose(interpolated_values, expected_values, rtol=1e-5)
    
    end_time_perf = time.time()
    print(f"Time taken for test: {end_time_perf - start_time_perf} seconds")

if __name__ == '__main__':
    # Run the test
    test_old_interpolation()
    # cProfile.run("test_old_interpolation()")





# start = pd.Timestamp('2022-07-23 00:00:00')
# end = pd.Timestamp('2022-07-23 23:45:00')
# x = pd.date_range(start,end,freq= "900s")
# y = [i*100 for i in range(len(x))]
# poi = pd.date_range(start,end,freq= "5s")
# poi = poi[1000:-1000]
# order = 11
# a = neville(x, y, poi, order) 
