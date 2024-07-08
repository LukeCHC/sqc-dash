# -*- coding: utf-8 -*-
"""
Created on Tue Dec  5 11:05:05 2023

@author: chcuk
"""
import numpy as np

from Coord import ECEF
from Coord import LLA
from Coord import ENU

def test_ecef():
    
    print("Testing ECEF")
    def test_distance_to_point():
        
        ecef1 = ECEF([[0, 0, 0], [1, 1, 1], [2, 2, 2]])
        ecef_single_point = ECEF([[1, 1, 1]])
    
        expected_output = np.array([1.73205081, 0., 1.73205081])  # Expected distances
        actual_output = ecef1.distance_to_point(ecef_single_point)
    
        try:
            assert np.allclose(actual_output, expected_output)
            print("Test distance_to_point: Pass")
        except AssertionError:
            print("Test distance_to_point: Fail")
            
    def test_distance_pairwise():
        ecef1 = ECEF([[0, 0, 0], [1, 1, 1], [2, 2, 2]])
        ecef2 = ECEF([[1, 1, 1], [2, 2, 2], [3, 3, 3]])
    
        expected_output = np.array([1.73205081, 1.73205081, 1.73205081])  # Expected pairwise distances
        actual_output = ecef1.distance_pairwise(ecef2)
    
        try:
            assert np.allclose(actual_output, expected_output)
            print("Test distance_pairwise: Pass")
        except AssertionError:
            print("Test distance_pairwise: Fail")
            
    def test_ecef2lla():
        
        # We are going to run this test by using the point of mount everest
        lat =  27.9881 #N
        lon =  86.9250 #E
        alt= 8848 #meters
        
        lla1= LLA([lat,lon,alt]) 
        
        ecef1 = lla1.lla2ecef()
        
        lla2 = ecef1.ecef2lla()
        
        dist = lla1.distance_to_point(lla2)
        
        print(f"Distance between positions after lla 2 ecef 2 lla: {dist[0]} m.")
        
    def test_ecef2enu():
        # matlab example
        # https://uk.mathworks.com/help/map/ref/ecef2enu.html
        obs_lat = np.radians(45.9132)
        obs_lon = np.radians(36.7484)
        obs_h = 1877743.2 # ellipsoidal height in km
        ecef1 = ECEF([5507.5289*1000, 4556.2241*1000, 6012.8208*1000])
        enu = ecef1.ecef2enu(obs_lat, obs_lon, obs_h)
        ecef2 = enu.enu2ecef()
        
        dist = ecef1.distance_to_point(ecef2)
        print(f"Distance between positions after ecef 2 enu 2 ecef: {dist[0]} m.")
    
    def test_azel_calculation():
        """
        Test the calculation of azimuth and elevation.
        The test uses known ECEF coordinates for an observer and a satellite,
        and compares the calculated azimuth and elevation with expected values.
        """
        # Test data from SOP file
        xs, ys, zs = -22620249.06, 12104020.777, 6803717.768
        xr, yr, zr = -2891520.683, 4649102.241, 3261022.999
        az_data, el_data = 1.981, 0.859  # Expected values in radians
    
        # Create ECEF instances for observer and single satellite
        observer = ECEF([xr, yr, zr])
        satellite = ECEF([xs, ys, zs])
    
        # Calculate azimuth and elevation
        azel_arr = observer.calculate_azel(satellite)
        
        az_calc = azel_arr[:,0]
        el_calc = azel_arr[:,1]
    
        # Convert calculated values to radians if they are in degrees
        az_calc_rad = np.radians(az_calc)
        el_calc_rad = np.radians(el_calc)
    
        # Define tolerance for comparison
        tolerance = 0.01  # Adjust tolerance as needed
    
        # Assert that calculated and expected values are close
        assert abs(az_calc_rad - az_data) < tolerance, f"Azimuth mismatch. Expected: {az_data}, Calculated: {az_calc_rad}"
        assert abs(el_calc_rad - el_data) < tolerance, f"Elevation mismatch. Expected: {el_data}, Calculated: {el_calc_rad}"
    
        print("Azimuth and elevation calculation test passed.")

    def test_azel_calculation_multi():
        """
        Test the calculation of azimuth and elevation for multiple targets.
        The test uses known ECEF coordinates for an observer and a satellite,
        and compares the calculated azimuth and elevation with expected values.
        """
        # Test data from SOP file
        xs1, ys1, zs1 = -22620249.06, 12104020.777, 6803717.768
        xs2, ys2, zs2 = -13136504.729, 20968053.842, 9224548.827
        xr, yr, zr = -2891520.683, 4649102.241, 3261022.999
        az_data1, el_data1 = 1.981, 0.859  # Expected values in radians
        az_data2, el_data2 = 3.125, 1.331  # Expected values in radians
    
        # Create ECEF instances for observer and single satellite
        observer = ECEF([xr, yr, zr])
        satellites = ECEF([[xs1, ys1, zs1],[xs2, ys2, zs2]])
    
        # Calculate azimuth and elevation
        azel_arr = observer.calculate_azel(satellites)
    
        az_calc, el_calc = azel_arr[:,0], azel_arr[:,1]
    
        # Convert calculated values to radians if they are in degrees
        az_calc_rad = np.radians(az_calc)
        el_calc_rad = np.radians(el_calc)
    
        # Define tolerance for comparison
        tolerance = 0.01  # Adjust tolerance as needed
    
        # Assert that calculated and expected values are close
        assert abs(az_calc_rad[0] - az_data1) < tolerance, f"Azimuth mismatch. Expected: {az_data1}, Calculated: {az_calc_rad[0]}"
        assert abs(el_calc_rad[0] - el_data1) < tolerance, f"Elevation mismatch. Expected: {el_data1}, Calculated: {el_calc_rad[0]}"
        assert abs(az_calc_rad[1] - az_data2) < tolerance, f"Azimuth mismatch. Expected: {az_data2}, Calculated: {az_calc_rad[1]}"
        assert abs(el_calc_rad[1] - el_data2) < tolerance, f"Elevation mismatch. Expected: {el_data2}, Calculated: {el_calc_rad[1]}"
    
        print("Azimuth and elevation multi calculation test passed.")

        
    test_distance_to_point()
    test_distance_pairwise()
    test_ecef2lla()
    test_ecef2enu()
    test_azel_calculation()
    test_azel_calculation_multi()
    
    
    
def test_lla():
    
    print("Testing LLA")
    def test_distance_to_point():
        
        
        # NOT WORKING DUE TO LLA TYPE IS INSTANCE
        lla_shard = LLA([[51.5045, -0.0865, 0]])  # The Shard, London
        lla_eiffel = LLA([[48.8584, 2.2945, 0]])  # Eiffel Tower, Paris
    
        # Calculate expected distance
        # Note: This is a rough estimation as the formula in your method is a simplified one.
        lat_diff = (51.5045 - 48.8584) * 3600 * 30.8667
        lon_diff = ((-0.0865 - 2.2945) * 3600 * 30.8667) * np.cos(np.radians(51.5045))
        alt_diff = 0  # Same altitude
    
        expected_distance = np.linalg.norm([lat_diff, lon_diff, alt_diff])
    
        # Calculate actual distance
        actual_distance = lla_shard.distance_to_point(lla_eiffel)
    
        # Test assertion
        try:
            assert np.allclose(actual_distance, expected_distance)
            print("Test LLA distance_to_point: Pass")
        except AssertionError:
            print("Test LLA distance_to_point: Fail")
        
    test_distance_to_point()
    
if __name__ == '__main__':
    test_ecef()
    print('\n')
    test_lla()
    
    
        # ecef1 = ECEF([638137,1,1])
        # obs_lat = 0 #observer pos
        # obs_lon = 0 #observer pos
        # enu = ecef1.ecef2enu(obs_lat, obs_lon)
        # ecef2 = enu.enu2ecef() # Need to fix
        # dist = ecef2.distance_to_point(ecef1)
        # print(f"Before ENU conv: {ecef1.position}")
        # print(f"After ENU conv:{ecef2.position}")
        # print(f"distance between (m): {dist}")
        
        #%%
"""
gpt managed to fix ecef to enu


import numpy as np

# Constants for Earth
a = 6378137  # radius of the Earth in meters
f = 1 / 298.257223563  # flattening
e2 = f * (2-f)  # square of eccentricity

# Function to convert latitude, longitude, and altitude to ECEF coordinates
def lla_to_ecef(lat, lon, alt):
    # Convert latitude and longitude to radians
    lat_rad = np.radians(lat)
    lon_rad = np.radians(lon)

    # Prime vertical radius of curvature
    N = a / np.sqrt(1 - e2 * np.sin(lat_rad)**2)

    # ECEF coordinates
    X = (N + alt) * np.cos(lat_rad) * np.cos(lon_rad)
    Y = (N + alt) * np.cos(lat_rad) * np.sin(lon_rad)
    Z = ((1-e2) * N + alt) * np.sin(lat_rad)

    return np.array([X, Y, Z])

# Function to transform ECEF coordinates to ENU coordinates
def ecef_to_enu(ecef, lat_ref, lon_ref, alt_ref):
    # Convert reference latitude, longitude, and altitude to ECEF coordinates
    ecef_ref = lla_to_ecef(lat_ref, lon_ref, alt_ref)
    
    # Compute the difference vector
    delta = ecef - ecef_ref

    # Convert reference latitude and longitude to radians
    lat_ref_rad = np.radians(lat_ref)
    lon_ref_rad = np.radians(lon_ref)

    # Compute the transformation matrix from ECEF to ENU
    R = np.array([[-np.sin(lon_ref_rad), np.cos(lon_ref_rad), 0],
                  [-np.cos(lon_ref_rad)*np.sin(lat_ref_rad), -np.sin(lon_ref_rad)*np.sin(lat_ref_rad), np.cos(lat_ref_rad)],
                  [np.cos(lon_ref_rad)*np.cos(lat_ref_rad), np.sin(lon_ref_rad)*np.cos(lat_ref_rad), np.sin(lat_ref_rad)]])

    # Apply the transformation matrix to the difference vector
    enu = R.dot(delta)

    return enu

# Given ECEF coordinates for the point of interest
ecef_coords = np.array([5507.5289, 4556.2241, 6012.8208]) * 1000  # Convert from km to m

# Given geodetic coordinates for the local origin
lat0 = 45.9132  # Latitude in degrees
lon0 = 36.7484  # Longitude in degrees
h0 = 1877.7532 * 100

"""