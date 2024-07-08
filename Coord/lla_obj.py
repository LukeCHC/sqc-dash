# -*- coding: utf-8 -*-
"""
Created on Fri Dec  1 10:58:47 2023

@author: chcuk
"""

import numpy as np


class LLA:
    # Number of columns in position array
    _N_COLUMNS = 3 # avoids magic numbers, not necessary but good practice
    
    def __init__(self, position, unit='degrees', logger= None):
        """
        Initialize the LLA object with position in either degrees or radians.
        Latitude, Longitude, Altitude.

        Args:
            position: Can be a list, list of lists, tuple, numpy array, LLA object, or ECEF object.
                      Represents the position in LLA coordinates (latitude, longitude, altitude).
            unit: The unit of the input position ('degrees' or 'radians'). Defaults to 'degrees'.
            logger: SimpleLogger object for logging messages. Defaults to None.
        """
        self.position = self._convert_input(position, unit)
        self._validate_input(self.position)
        self.size = self.position.shape[0]

        self.logger = logger
    
    def _log(self, message):
        if self.logger:
            self.logger.write_log(message)
        else:
            print(message)
        
    def _convert_input(self, position, unit):
        """
        Convert various input types to a uniform numpy array format and handle unit conversion.

        Args:
            position: The input position data.
            unit: The unit of the input position ('degrees' or 'radians').

        Returns:
            numpy.ndarray: The converted position in radians.
        """
        # Convert to numpy array and reshape
        if isinstance(position, (list, tuple)):
            position = np.array(position, dtype=np.float64).reshape(-1, self._N_COLUMNS)
        elif isinstance(position, np.ndarray):
            # Ensure the array is of float type
            position = position.astype(np.float64)
            # Make sure array is 2d
            if position.ndim == 1:
                position = position.reshape(1, self._N_COLUMNS).squeeze() # squeeze to small shape
        elif isinstance(position, LLA):
            position = position.position
        # elif isinstance(position, ECEF):
        #     position = position.ecef2lla().position 
        else:
            raise TypeError("Unsupported input type for position")
            
        # Convert input unit to lower and remove whitespace
        unit_str = unit.lower().strip()

        # if degrees, convert lat lon to rads
        if unit_str in ['degrees', 'deg', 'd']:
            lat_degrees = position[:, 0]
            lat_rads = np.radians(lat_degrees)
            # Normalize latitude to be within -pi/2 to pi/2
            position[:, 0] = np.mod(lat_rads + np.pi, 2 * np.pi) - np.pi
            position[:, 0] = np.where(position[:, 0] > np.pi/2, np.pi - position[:, 0], position[:, 0])
            position[:, 0] = np.where(position[:, 0] < -np.pi/2, -np.pi - position[:, 0], position[:, 0])

            lon_degrees = position[:, 1]
            lon_rads = np.radians(lon_degrees)
            # Normalize longitude to be within -pi to pi
            position[:, 1] = np.mod(lon_rads + np.pi, 2 * np.pi) - np.pi
            

        elif unit_str in ['radians','rad','r']:
            pass
        
        else:
            raise TypeError("Invalid unit. Expected 'degrees', 'deg', 'd', 'radians', 'rad', or 'r'") 
        return position
    
    def _validate_input(self, position):
        """
        Validate the input position array.

        Args:
            position: The position array to validate.

        Raises:
            ValueError: If the array doesn't meet the expected conditions.
        """
        if position.shape[1] != 3:
            raise ValueError("Position must be an nx3 array")

        if np.any(position[:, 0] < -np.pi/2) or np.any(position[:, 0] > np.pi/2):
            raise ValueError("Latitude values must be within the range -90 to 90 degrees")

        if np.any(position[:, 1] < -np.pi) or np.any(position[:, 1] > np.pi):
            raise ValueError("Longitude values must be within the range -180 to 180 degrees")
            
    def distance_to_point(self, point):
        """
        Calculate distances from each position in the LLA object to a single point.

        Args:
            point (LLA): An ECEF object with a single position.

        Returns:
            numpy.ndarray: Distances from each position to the point.
        """
        if not isinstance(point, LLA) or point.size != 1:
            raise ValueError("Point must be an LLA object with a single position")

        lat_diff = (self.lat_d - point.lat_d) * 3600 * 30.8667
        lon_diff = [(self.lon_d[i] - point.lon_d[i]) * 3600 * 30.8667 * np.cos(self.lat_r[i]) for i in range(len(self.lon_d))]
        alt_diff = self.alt_m - point.alt_m

        diff_arr = np.column_stack([lat_diff, lon_diff, alt_diff])
        
        return np.linalg.norm(diff_arr, axis=1)

            
    def lla2ecef(self):
        """
        Convert LLA positions to ECEF (earth centered earth fixed x,y,z)
        Source: https://uk.mathworks.com/help/aeroblks/llatoecefposition.html
        
        Returns:
            ECEF object containing transformed positions
        """
        from Coord import ECEF
        # constants 
        EARTH_RADIUS = 6378137.0  # Equatorial radius in meters
        semi_major = 6378137.0  # Semi-major axis in meters
        semi_minor = 6356752.3142  # Semi-minor axis in meters
        F = (semi_major - semi_minor) / semi_major  # Flattening 
        # E1_SQ = 1 - (1 - F)**2 # Square_of_first_eccentricity
        
        # Calculate geocentric latitude
        geocent_lat = np.arctan((1 - F)**2 * np.tan(self.lat_r)).reshape(-1,1)
        
        r_s = np.sqrt(
            EARTH_RADIUS**2 / ( 
                1 + (1 / (
                    1-F)**2 -1) * np.sin(geocent_lat)**2)
                    ).reshape(-1,1)
        
        x = r_s * np.cos(geocent_lat) *np.cos(self.lon_r) + self.alt_m *np.cos(self.lat_r) * np.cos(self.lon_r)
        y = r_s * np.cos(geocent_lat) *np.sin(self.lon_r) + self.alt_m *np.cos(self.lat_r) * np.sin(self.lon_r)
        z = r_s*np.sin(geocent_lat) + self.alt_m * np.sin(self.lat_r)
        
        rtn_arr = np.column_stack([x,y,z])
        
        return ECEF(rtn_arr)
            
    def calculate_azel(self, target):
        """
        Calculate the azimuth and elevation of a target satellite observed self.alt_m.shape
        from self.position
        
        """
        
        if self.size < 1:
            raise("This function is only designed for one observer position")
        
        from Coord.azel_calculation import AltAzimuthRange
        from Coord import ECEF
        
        
        # set observer coords, use .item() to get scalar value, prevents crash at observer initialisation
        lat_obs_deg, lon_obs_deg, alt_obs_m = self.lat_d.item(), self.lon_d.item(), self.alt_m.item()
        
        if isinstance(target, ECEF):
            target = target.ecef2lla()
        
        # Determine the format of the target and convert to LLA if necessary
        if isinstance(target, LLA):
            lat_tar_deg, lon_tar_deg, alt_tar_m = target.lat_d, target.lon_d, target.alt_m
        
        else:
            raise ValueError("Input format of target is not recognised, must be ECEF or LLA object")
        
        # Initialize the azimuth-elevation calculator
        
        observer = np.array((lat_obs_deg, lon_obs_deg, alt_obs_m))
        targets = np.column_stack((lat_tar_deg, lon_tar_deg, alt_tar_m))
        
        azel = AltAzimuthRange(observer, targets)

        # Calculate the azimuth and elevation
        
        azeldist_arr = azel.calculate()
        
        azel_arr = azeldist_arr[:, :2]
    
        return azel_arr
    
    
    @property
    def lat_d(self):
        lat_degrees = np.degrees(self.position[:, 0]).reshape(-1, 1)
        # Normalize latitude to be within -180 to 180
        lat = np.mod(lat_degrees + 180, 360) - 180
        # For latitudes beyond the poles, adjust to reflect the correct hemisphere
        lat = np.where(lat > 90, 180 - lat, lat)
        lat = np.where(lat < -90, -180 - lat, lat)
        return lat

    @property
    def lon_d(self):
        return np.degrees(self.position[:, 1]).reshape(-1,1)

    @property
    def lat_r(self):
        return self.position[:, 0].reshape(-1,1)

    @property
    def lon_r(self):
        return self.position[:, 1].reshape(-1,1)
    
    @property
    def alt_m(self):
        return self.position[:, 2].reshape(-1,1)
    
    
    

#%%

def test():
    position = [[0, 0, 0], [90, 180, 1000]]  # Can be a list of lists, numpy array, etc.
    lla_obj = LLA(position, unit='degrees')
    print(lla_obj.lla2ecef().position)
    
    return 

if __name__ == '__main__':
    test()
    
