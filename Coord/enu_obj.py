# -*- coding: utf-8 -*-
"""
Created on Fri Dec  1 10:57:14 2023

@author: chcuk
"""
import numpy as np

from Coord.lla_obj import LLA
from Coord.ecef_obj import ECEF

class ENU:
    def __init__(self, position, reference_point, reference_type='LLA'):
        """
        Initialize the ENU object with position relative to a reference point.

        Args:
            position: Relative position in ENU coordinates (East, North, Up).
                      Can be a list, list of lists, tuple, numpy array.
            reference_point: The reference point in LLA or ECEF coordinates.
            reference_type: Type of the reference point ('LLA' or 'ECEF').
        """
        self.position = self._convert_input(position)
        self.reference_point = self._convert_reference_point(reference_point, reference_type)
        self._validate_input(self.position)

        # Additional methods for conversion between ENU and LLA/ECEF

    def _convert_input(self, input_data):
        """
        Convert position data input to a uniform numpy array format.

        Args:
            input_data: The input position data.

        Returns:
            numpy.ndarray: The converted position array.
        """
        if isinstance(input_data, (list, tuple)):
            return np.array(input_data, dtype=np.float64).reshape(-1, 3)
        elif isinstance(input_data, np.ndarray):
            return input_data.astype(np.float64).reshape(-1, 3)
        elif isinstance(input_data, ENU):
            return input_data.position
        else:
            raise TypeError("Unsupported input type for position")

    def _convert_reference_point(self, reference_point, reference_type):
        """
        Convert the reference point to LLA format.

        Args:
            reference_point: The reference point data.
            reference_type: The type of the reference point ('LLA' or 'ECEF').

        Returns:
            numpy.ndarray: The reference point in LLA format.
        """
        if reference_type == 'LLA':
            if isinstance(reference_point, (list, tuple)):
                return np.array(reference_point, dtype=np.float64).reshape(-1, 3)
            elif isinstance(reference_point, np.ndarray):
                return LLA(reference_point.astype(np.float64).reshape(-1, 3), 'R')
            # Additional handling if the reference_point is an LLA object
            elif isinstance(reference_point, LLA):
                return LLA(reference_point.position,'R')
            else:
                raise TypeError("Unsupported input type for LLA reference point")
        elif reference_type == 'ECEF':
            # Placeholder for ECEF to LLA conversion logic
            # return convert_ecef_to_lla(reference_point)
            pass
        else:
            raise ValueError("Reference type must be 'LLA' or 'ECEF'")

    def _validate_input(self, position):
        """
        Validate the input position array.

        Args:
            position: The position array to validate.

        Raises:
            ValueError: If the array doesn't meet the expected conditions.
        """
        if position.ndim != 2 or position.shape[1] != 3:
            raise ValueError("Position must be an nx3 array")

    def enu2ecef(self):
        """Transform ENU coordinates to ECEF coordinates relative to a reference point."""
        # Convert reference latitude, longitude, and altitude to ECEF coordinates
        ecef_ref = self.reference_point.lla2ecef()
        
        # squeeze returns smallest dimension possible
        lat_ref = self.reference_point.lat_r.squeeze()
        lon_ref = self.reference_point.lon_r.squeeze()
        
        # Compute the transformation matrix from ENU to ECEF
        # The matrix is the inverse of the ECEF to ENU transformation matrix
        # Since the original matrix is orthogonal, the inverse is equal to the transpose
        R = np.array([[-np.sin(lon_ref), np.cos(lon_ref), 0],
                      [-np.cos(lon_ref)*np.sin(lat_ref), -np.sin(lon_ref)*np.sin(lat_ref), np.cos(lat_ref)],
                      [np.cos(lon_ref)*np.cos(lat_ref), np.sin(lon_ref)*np.cos(lat_ref), np.sin(lat_ref)]])
    
        # Apply the transformation matrix to the ENU coordinates
        # We transpose R since we are converting from ENU back to ECEF
        ecef = ecef_ref.position + np.dot(self.position, R)
        
        return ECEF(ecef)

    def enu2ecef_old(self):
        """
        Convert ENU coordinates to ECEF coordinates using the reference point in LLA format.
        """
        # First, convert the reference point to ECEF if it's not already
        reference_ecef = self._convert_reference_to_ecef(self.reference_point)

        # Calculate the rotation matrix using the reference latitude and longitude
        rotation_matrix = self._calc_ecef_rotation_matrix(self.reference_point)

        # Apply the rotation matrix to the ENU positions to get ECEF relative positions
        relative_ecef_positions = rotation_matrix @ self.position.T

        # Add the reference ECEF position to get absolute ECEF positions
        absolute_ecef_positions = relative_ecef_positions.T + reference_ecef

        return absolute_ecef_positions

    def _calc_ecef_rotation_matrix(self, reference_lla):
        """
        Calculate the rotation matrix for the conversion from ENU to ECEF coordinates.
        """
        lat, lon, _ = reference_lla

        # Convert latitude and longitude to radians if they are in degrees
        lat_r = np.radians(lat) if self._is_degrees(lat) else lat
        lon_r = np.radians(lon) if self._is_degrees(lon) else lon

        # Calculate the sine and cosine of latitude and longitude
        sin_lat = np.sin(lat_r)
        cos_lat = np.cos(lat_r)
        sin_lon = np.sin(lon_r)
        cos_lon = np.cos(lon_r)

        # Define the rotation matrix (inverse of the ECEF to ENU rotation matrix)
        rotation_matrix = np.array([
            [-sin_lon, -cos_lon * sin_lat, cos_lon * cos_lat],
            [cos_lon, -sin_lon * sin_lat, sin_lon * cos_lat],
            [0, cos_lat, sin_lat]
        ])

        return rotation_matrix

    def _convert_reference_to_ecef(self, reference_lla):
        """
        Convert the reference point from LLA to ECEF coordinates.
        """
        # Placeholder for LLA to ECEF conversion logic
        # return convert_lla_to_ecef(reference_lla)
        pass

    def _is_degrees(self, value):
        # Check if the value is within the typical range of latitudes/longitudes in degrees
        return np.abs(value).max() > 2 * np.pi

#%%

if __name__ == '__main__':
    position = [[100, 200, 50], [150, 250, 60]]  # Can be a list of lists, numpy array, etc.
    enu_obj = ENU(position)
    