# -*- coding: utf-8 -*-
"""
Created on Thu Oct  5 12:04:50 2023

@author: chcuk
"""

from typing import List, Union, Optional
from datetime import datetime
import numpy as np
from numba import jit


"""

- I used chatGPT to try and improve the efficiency of the old interpolation class.
- This code is imo much clearer but does run a little slower.
- This code makes use of the jit decorator which speeds up numerical calculations.


- The @jit decorator is from the Numba library and serves as a Just-In-Time (JIT) compiler.
- It compiles the annotated Python function to native machine code using the LLVM compiler library.
- Using @jit can result in significantly faster execution times, particularly for numerical and loop-heavy operations.
"""

class NevilleInterpolation:
    def __init__(self, x: Optional[List[Union[datetime, float]]] = None, y: Optional[List[float]] = None):
        """
        Initialize Interpolation class with optional x and y data points.
        """
        if len(x):
            self.x = np.array([i.timestamp() if isinstance(i, datetime) else i for i in x])
        else:
            self.x = None
        self.y = np.array(y) if len(y) else None
        
    def single_point(self, win_x: List[Union[datetime, float]], win_y: List[float], x_point: Union[datetime, float]) -> float:
        """
        Interpolate a single point using Neville's algorithm.
        """
        x = np.array([i.timestamp() if isinstance(i, datetime) else i for i in win_x])
        poi = x_point.timestamp() if isinstance(x_point, datetime) else x_point
        n = len(x)
        p = np.zeros(n)
        return optimized_nev_calc(x, np.array(win_y), poi, p)

    def multiple_points(self, poi: List[Union[datetime, float]], order: int) -> List[float]:
       """
       Interpolate multiple points using a rolling window approach.
       """
       n = order // 2
       poi_array = np.array([i.timestamp() if isinstance(i, datetime) else i for i in poi])
       # p = np.zeros(order+1)  # Preallocated array for temporary storage
       return np.array(multiple_points_optimized(self.x, self.y, poi_array, order, n))

#issues calling jit inside the class so we leave it outside

@jit(nopython=True)
def multiple_points_optimized( x, y, poi_array, order, n):
    """
    Perform interpolation for multiple points using a rolling-window approach.
    """
    
    # Initialize result array to store interpolated values
    result = np.zeros(len(poi_array))
    j = 0  # Initialize index for traversing x array
    for idx, i in enumerate(poi_array):  # Iterate through points of interest
        while not (x[j] <= i < x[j + 1]):
            j += 1
            
        # Extract window of x and y values around the point of interest
        win_x = x[j - n:j + n + 1]
        win_y = y[j - n:j + n + 1]
        
        # Initialize a preallocated array for temporary storage
        p = np.zeros(len(win_x))    
        
        # Perform interpolation for the current point and store the result
        result[idx] = optimized_nev_calc(win_x, win_y, i, p)  # Assuming this function is already optimized
        
    return result

@jit(nopython=True)
def optimized_nev_calc(win_x: np.ndarray, win_y: np.ndarray, x_point: float, p: np.ndarray) -> float:
    """
    Private function to calculate Neville's interpolation for a single point.
    """
    n = len(win_x)
    for k in range(n):
        for i in range(n - k):
            if k == 0:
                p[i] = win_y[i]
            else:
                # comments for debugging
                # print("Current index i:", i, "Current index k:", k)
                # print("All win_x values:", win_x)
                # print("win_x[i + k]: ", win_x[i + k], "win_x[i]: ", win_x[i])
                p[i] = ((x_point - win_x[i + k]) * p[i] + (win_x[i] - x_point) * p[i + 1]) / (win_x[i] - win_x[i + k])
    return p[0]

    
#%%

import time
from datetime import datetime, timedelta
import numpy as np
from typing import List, Union, Optional
# import cProfile
# Assuming the NevilleInterpolation class is imported or defined above

def test_new_interpolation():
    start_time_perf = time.time()
    
    # # Create a much larger list of x and y values
    start_time_dt = datetime(2023, 1, 1, 12, 0, 0)
    x = [start_time_dt + timedelta(seconds=i) for i in range(200000)]
    y = [i**2 for i in range(200000)]
    
    # # Create an instance of the NevilleInterpolation class
    interpolator = NevilleInterpolation(x, y)

    # Test single_point method with a larger window
    win_x = [start_time_dt + timedelta(seconds=i) for i in range(1000, 1010)]
    win_y = [i**2 for i in range(1000, 1010)]
    x_point = start_time_dt + timedelta(seconds=1005)
    interpolated_value = interpolator.single_point(win_x, win_y, x_point)
    assert round(interpolated_value, 2) == 1005**2

    # Test multiple_points method with a much larger order and more POI
    poi = [start_time_dt + timedelta(seconds=i) for i in range(100, 190000)]
    order = 20  # Updated order
    interpolated_values = interpolator.multiple_points(poi, order)
    expected_values = [i**2 for i in range(100, 190000)]
    np.testing.assert_allclose(interpolated_values, expected_values, rtol=1e-5)
    
    end_time_perf = time.time()
    print(f"Time taken for test: {end_time_perf - start_time_perf} seconds")

if __name__ == '__main__':
    # Run the test
    test_new_interpolation()
    # cProfile.run("test_new_interpolation()")
    # cProfile.run("test_new_interpolation()",  filename='C:/Users/chcuk/Work/Projects/I2GV2/test/profiler.pstats')

