# -*- coding: utf-8 -*-
"""
Created on Thu Nov 30 14:18:06 2023

@author: chcuk
"""

import numpy as np
import pandas as pd


class ECEF:
    # number of cols in position array
    _N_COLUMNS = 3 # avoids magic numbers, not necessary but good practice
    
    def __init__(self, position, velocity=None):
        """
        Initialize the ECEF object with position and optional velocity.

        Args:
            position: Can be a list, list of lists, tuple, numpy array, ECEF object, or LLA object.
                      Should represent the position in ECEF coordinates (nx3 array).
            velocity: Optional. If provided, should match the shape of the position array.
                      Represents the velocity in ECEF coordinates.
        """
        # Convert and validate position
        self.position = self._convert_input(position)
        self._validate_input(self.position, 'position')

        # Convert and validate velocity if provided
        if velocity is not None:
            self.velocity = self._convert_input(velocity)
            self._validate_input(self.velocity, 'velocity', self.position.shape)
        else:
            # If no velocity is provided, default to zero velocity
            self.velocity = np.zeros_like(self.position)

        # Allows us to retrieve specific values
        self.x, self.y, self.z = self.position.T

        # A parameter to keep track of how many positions in the object
        self.size = self.position.shape[0]

    def _convert_input(self, position):
        """
        Convert various input types to a uniform numpy array format.

        Args:
            position: The input data to be converted.

        Returns:
            numpy.ndarray: The converted numpy array.
        """
        if isinstance(position, (list, tuple)):
            return np.array(position).reshape(-1,3).astype(np.float64)
        elif isinstance(position, np.ndarray):
            position = position.astype(np.float64)
            # Make sure array is 2d
            if position.ndim == 1:
                position = position.reshape(1, self._N_COLUMNS)
            return position
        elif isinstance(position, ECEF):
            return position.position
        elif isinstance(position, pd.DataFrame):
            position = position.to_numpy().astype(np.float64)
            return position
        # elif isinstance(position, LLA):
        #     return position.lla2ecef()  # Assuming LLA class has a method lla2ecef
        else:
            raise TypeError("Unsupported input type for position or velocity")

    def _validate_input(self, array, name, expected_shape=None):
        """
        Validate the input arrays for position and velocity.

        Args:
            array: The array to validate.
            name: Name of the array (for error messages).
            expected_shape: The expected shape of the array, used to
                            make sure velocity array shape matches position array.

        Raises:
            ValueError: If the array doesn't meet the expected conditions.
        """
        if not isinstance(array, np.ndarray):
            raise TypeError(f"The {name} must be a numpy array")

        if expected_shape and array.shape != expected_shape:
            raise ValueError(f"The shape of {name} must match the position shape: {expected_shape}")

        if array.ndim != 2 or array.shape[1] != 3:
            raise ValueError(f"The {name} must be an nx3 array")
            
    def distance_to_point(self, point):
        """
        Calculate distances from each position in the ECEF object to a single point.

        Args:
            point (ECEF): An ECEF object with a single position.

        Returns:
            numpy.ndarray: Distances from each position to the point.
        """
        if not isinstance(point, ECEF) or point.size != 1:
            raise ValueError("Point must be an ECEF object with a single position")

        return np.linalg.norm(self.position - point.position, axis=1)

    def distance_pairwise(self, target_ecef):
        """
        Calculate distances between corresponding positions of two ECEF objects.
    
        Args:
            other (ECEF): Another ECEF object with the same number of positions.
    
        Returns:
            numpy.ndarray: Distances between corresponding positions.
        """
        if not isinstance(target_ecef, ECEF) or self.size != target_ecef.size:
            raise ValueError("Both ECEF objects must have the same number of positions")
    
        return np.linalg.norm(self.position - target_ecef.position, axis=1)
    
    def ecef2lla(self):
        """
        Convert ECEF positions to LLA (Latitude, Longitude, Altitude)
        Source: https://uk.mathworks.com/help/aeroblks/ecefpositiontolla.html
        
        lat = beta, lon = mu
        
        if x = 0: lon = 0
        if y = 0: lat = +/- pi/2
        
        Returns:
            LLA object containing transformed positions
        """
        # Local import to prevent circular imports
        from Coord import LLA
        
        # Constants
        semi_major = 6378137.0  # Semi-major axis in meters
        semi_minor = 6356752.3142  # Semi-minor axis in meters
        F = (semi_major - semi_minor) / semi_major  # Flattening 
        EARTH_RADIUS = 6378137  # meters
        E1_SQ = 1 - (1 - F)**2 #square_of_first_eccentricity
        
        # Not sure what s stands for, 
        s = np.sqrt(self.x ** 2 + self.y ** 2)
        
        # Initial guess of latitude
       
        beta0 =np.arctan2(self.z, (1 - F) * s)
        # ^^^^^ we use arctan2 as the defined range for arctan 
        # is only -90 to 90 compared to -180 to 180
        
        
        # initiate these temp arrays to pass first recursion check
        mu0 = np.zeros_like(beta0)
        mu1= np.ones_like(beta0)
        
        # Iteratively solve for mu and beta until convergence
        k = 0
        while np.abs(mu1 - mu0).mean() > 1e-9:
            k+=1 
            mu0 = self._calc_mu(beta0, E1_SQ, EARTH_RADIUS, F, s)
            beta1 = self._calc_beta(mu0, F)
            mu1 = self._calc_mu(beta1, E1_SQ, EARTH_RADIUS, F, s)
            beta0 = beta1
        
        # Next to calculat Altitude
        # Radius of curvature in the vertical prime
        N = EARTH_RADIUS / np.sqrt(1 - E1_SQ * np.sin(mu1) ** 2)
        
        # Height equals
        h = s * np.cos(mu1) + (self.z + E1_SQ * N * np.sin(mu1)) * np.sin(mu1) - N
        
        # lon_r = np.arctan(self.y / self.x)
        lon_r = np.arctan2(self.y , self.x)
        lat_r = mu1
        alt_m = h
        
        rtn_arr = np.vstack((lat_r, lon_r, alt_m)).T
        
        return LLA(rtn_arr, 'R')

    # Private helper functions for ecef2lla
    def _calc_beta(self, mu, F):
        return np.arctan(
            ((1-F) * np.sin(mu)) /np.cos(mu)
            )
        
    def _calc_mu(self, beta, E1_SQ, R, F, s):
        return np.arctan((self.z + 
                         (E1_SQ * (1-F) / (1 - E1_SQ) * 
                          R * np.sin(beta)**3)) / 
                        (s - E1_SQ * R * np.cos(beta)**3))    
    
    
    def calculate_azel(self, target):
        """
        Calculate the azimuth and elevation of a target satellite observed
        from self.position
        
        Args:
            target(ECEF or LLA): Class objects containing one or multiple satellite positions
        Returns:
            azel(np.array):2d array, column 0 contains az, column 1 el, both in degrees
        
        """
        # Convert observer's position from ECEF to LLA
        obs_lla = self.ecef2lla()
        
        # Calculation is done within LLA class
        azel = obs_lla.calculate_azel(target)
        
        return azel
    
    def ecef2enu(self, lat_ref, lon_ref, alt_ref):
        """
        Transform ECEF coordinates to ENU coordinates relative to a reference point.
        This is a local coordinate system where the reference point is the new origin.
        Args:
            lat_ref(float): lat position of new local origin, in radians
            lon_ref(float): lon position of new local origin, in radians
            lon_ref(float): alt position of new local origin, in metres
            
        source: https://gssc.esa.int/navipedia/index.php/Transformations_between_ECEF_and_ENU_coordinates
        also used chatgpt to help get correct answer
        """
        # Importing here avoids circular imports
        from Coord import ENU
        from Coord import LLA
        
        ref_point = LLA([lat_ref, lon_ref,alt_ref], 'R')
        
        # Convert reference latitude, longitude, and altitude to ECEF coordinates
        ecef_ref = ref_point.lla2ecef()
        
        # Compute the difference vector (get difference in each direction)
        delta = self.position - ecef_ref.position #ecef.distance_to_point(ecef_ref) 
    
        # Compute the transformation matrix from ECEF to ENU
        R = np.array([[-np.sin(lon_ref), np.cos(lon_ref), 0],
                      [-np.cos(lon_ref)*np.sin(lat_ref), -np.sin(lon_ref)*np.sin(lat_ref), np.cos(lat_ref)],
                      [np.cos(lon_ref)*np.cos(lat_ref), np.sin(lon_ref)*np.cos(lat_ref), np.sin(lat_ref)]])
    
        # Apply the transformation matrix to the difference vector
        e,n,u = R.dot(delta.T)
        
        return ENU([e,n,u], ref_point)
    
    
    
    def _is_degrees(self, value):
        # Check if the value is within the typical range of latitudes/longitudes in degrees
        # Returns true if any value in the input series is larger than 2pi
        return np.abs(value).max() > 2 * np.pi
    
    

#%%


    
if __name__ =='__main__':

    # test different input types
    position_list = [1,1,1]
    position_list_of_lists = [[1,1,1], [2,2,2], [3,3,3]]
    position_arr = np.array([[1,1,1],
                             [2,2,2]])

    ECEF(position_list)
    ECEF(position_list_of_lists)
    ECEF(position_arr)
    
    ecef1 = ECEF([[0, 0, 0], [1, 1, 1], [2, 2, 2]])
    ecef2 = ECEF([[1, 1, 1], [2, 2, 2], [3, 3, 3]])
    ecef_single_point = ECEF([[1, 1, 1]])
    
    # Test distance to a single point
    print("Distance to a Single Point:", ecef1.distance_to_point(ecef_single_point))
    
    # Test pairwise distances
    print("Pairwise Distances:", ecef1.distance_pairwise(ecef2))
    
    # Test lla calculation
    lla = ecef2.ecef2lla() # Height calculation is wrong, lat long correct
    print(lla.position)

    # Test enu conversion
    enu = ecef2.ecef2enu(observer_lat= 0, observer_lon= 0)
    print(enu.position)
    enu2ecef = enu.enu2ecef()
    print(ecef2.position)
    print(enu.position)
    