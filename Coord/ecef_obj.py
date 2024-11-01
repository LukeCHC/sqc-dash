import numpy as np
import pandas as pd
import logging
import unittest

class ECEF:
    _N_COLUMNS = 3
    
    def __init__(self, position, velocity=None, logging_enabled=False):
        """
        Initialize the ECEF object with position and optional velocity.

        Args:
            position (various): Can be a list, list of lists, tuple, numpy array, ECEF object, or LLA object.
                                Should represent the position in ECEF coordinates (nx3 array).
            velocity (various, optional): Optional. If provided, should match the shape of the position array.
                                          Represents the velocity in ECEF coordinates.
            logging_enabled (bool, optional): Enable or disable logging. Defaults to False.
        """
        self.logging_enabled = logging_enabled
        self.logger = self._setup_logger()
        self.logger.info("Initializing ECEF object")
        
        self.position = self._convert_input(position)
        self._validate_input(self.position, 'position')

        if velocity is not None:
            self.velocity = self._convert_input(velocity)
            self._validate_input(self.velocity, 'velocity', self.position.shape)
        else:
            self.velocity = np.zeros_like(self.position)

        self.x, self.y, self.z = self.position.T
        self.size = self.position.shape[0]
        
        self.logger.debug(f"ECEF object initialized with {self.size} positions")

    def _setup_logger(self):
        """
        Set up the logger for the ECEF class.

        Returns:
            logging.Logger: Configured logger.
        """
        logger = logging.getLogger(f'{__name__}.{id(self)}')
        logger.setLevel(logging.DEBUG if self.logging_enabled else logging.CRITICAL)
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
            handler.setFormatter(formatter)
            logger.addHandler(handler)
        return logger

    def _convert_input(self, position):
        """
        Convert various input types to a uniform numpy array format.

        Args:
            position (various): The input data to be converted.

        Returns:
            numpy.ndarray: The converted numpy array.
        """
        self.logger.debug(f"Converting input of type {type(position)}")
        if isinstance(position, (list, tuple)):
            # Ensure the input is a list of three arrays (x, y, z coordinates)
            if len(position) == 3 and all(isinstance(arr, np.ndarray) for arr in position):
                return np.column_stack(position).astype(np.float64)
            else:
                return np.array(position).reshape(-1, 3).astype(np.float64)
            # return np.array(position).reshape(-1, 3).astype(np.float64)
        elif isinstance(position, np.ndarray):
            position = position.astype(np.float64)
            if position.ndim == 1:
                position = position.reshape(1, self._N_COLUMNS)
            return position
        elif isinstance(position, ECEF):
            return position.position
        elif isinstance(position, pd.DataFrame):
            return position.to_numpy().astype(np.float64)
        else:
            self.logger.error(f"Unsupported input type: {type(position)}")
            raise TypeError("Unsupported input type for position or velocity")

    def _validate_input(self, array, name, expected_shape=None):
        """
        Validate the input arrays for position and velocity.

        Args:
            array (np.ndarray): The array to validate.
            name (str): Name of the array (for error messages).
            expected_shape (tuple, optional): The expected shape of the array, used to
                                              ensure the velocity array shape matches the position array.

        Raises:
            ValueError: If the array doesn't meet the expected conditions.
        """
        self.logger.debug(f"Validating {name} input")
        if not isinstance(array, np.ndarray):
            self.logger.error(f"{name} must be a numpy array")
            raise TypeError(f"The {name} must be a numpy array")

        if expected_shape and array.shape != expected_shape:
            self.logger.error(f"{name} shape {array.shape} does not match expected shape {expected_shape}")
            raise ValueError(f"The shape of {name} must match the position shape: {expected_shape}")

        if array.ndim != 2 or array.shape[1] != 3:
            self.logger.error(f"{name} must be an nx3 array, got shape {array.shape}")
            raise ValueError(f"The {name} must be an nx3 array")

    def distance_to_point(self, point):
        """
        Calculate distances from each position in the ECEF object to a single point.

        Args:
            point (ECEF): An ECEF object with a single position.

        Returns:
            numpy.ndarray: Distances from each position to the point.
        """
        self.logger.info("Calculating distance to point")
        if not isinstance(point, ECEF) or point.size != 1:
            self.logger.error("Invalid point for distance calculation")
            raise ValueError("Point must be an ECEF object with a single position")
        return np.linalg.norm(self.position - point.position, axis=1)

    def distance_pairwise(self, target_ecef):
        """
        Calculate distances between corresponding positions of two ECEF objects.

        Args:
            target_ecef (ECEF): Another ECEF object with the same number of positions.

        Returns:
            numpy.ndarray: Distances between corresponding positions.
        """
        self.logger.info("Calculating pairwise distances")
        if not isinstance(target_ecef, ECEF) or self.size != target_ecef.size:
            self.logger.error("Invalid target for pairwise distance calculation")
            raise ValueError("Both ECEF objects must have the same number of positions")
        return np.linalg.norm(self.position - target_ecef.position, axis=1)

    def ecef2lla(self):
        """
        Convert ECEF positions to LLA (Latitude, Longitude, Altitude).

        Returns:
            LLA: LLA object containing transformed positions.

        Source:
            https://uk.mathworks.com/help/aeroblks/ecefpositiontolla.html
        """
        self.logger.info("Converting ECEF to LLA")
        from Coord import LLA
        
        # Constants
        semi_major = 6378137.0  # Semi-major axis in meters
        semi_minor = 6356752.3142  # Semi-minor axis in meters
        F = (semi_major - semi_minor) / semi_major  # Flattening
        EARTH_RADIUS = 6378137  # meters
        E1_SQ = 1 - (1 - F)**2  # square of first eccentricity
        
        s = np.sqrt(self.x ** 2 + self.y ** 2)
        
        # Handle poles explicitly
        if np.all(s == 0):
            lat_r = np.sign(self.z) * np.pi / 2  # 90 or -90 degrees in radians
            lon_r = 0
            alt_m = np.abs(self.z) - semi_minor
            rtn_arr = np.vstack((lat_r, lon_r, alt_m)).T
            self.logger.debug(f"Poles special case: lat_r={lat_r}, lon_r={lon_r}, alt_m={alt_m}")
            return LLA(rtn_arr, 'R')
        
        beta0 = np.arctan2(self.z, (1 - F) * s)
        self.logger.debug(f"Initial values: s={s}, beta0={beta0}")
        
        mu0 = np.zeros_like(beta0)
        mu1 = np.ones_like(beta0)
        
        k = 0
        while np.abs(mu1 - mu0).mean() > 1e-9:
            k += 1
            mu0 = self._calc_mu(beta0, E1_SQ, EARTH_RADIUS, F, s)
            beta1 = self._calc_beta(mu0, F)
            mu1 = self._calc_mu(beta1, E1_SQ, EARTH_RADIUS, F, s)
            beta0 = beta1
            self.logger.debug(f"Iteration {k}: mu0={mu0}, beta1={beta1}, mu1={mu1}")
            if k > 100:
                self.logger.warning("ECEF to LLA conversion did not converge")
                break
        
        N = EARTH_RADIUS / np.sqrt(1 - E1_SQ * np.sin(mu1) ** 2)
        h = s * np.cos(mu1) + (self.z + E1_SQ * N * np.sin(mu1)) * np.sin(mu1) - N
        
        lon_r = np.arctan2(self.y, self.x)
        lat_r = mu1
        alt_m = h
        
        self.logger.debug(f"Final values: lat_r={lat_r}, lon_r={lon_r}, alt_m={alt_m}")
        
        rtn_arr = np.vstack((lat_r, lon_r, alt_m)).T
        
        self.logger.debug(f"ECEF to LLA conversion completed in {k} iterations")
        return LLA(rtn_arr, 'R')

    def _calc_beta(self, mu, F):
        """
        Calculate beta from mu.

        Args:
            mu (np.ndarray): Mu values.
            F (float): Flattening factor.

        Returns:
            np.ndarray: Beta values.
        """
        return np.arctan(((1 - F) * np.sin(mu)) / np.cos(mu))
        
    def _calc_mu(self, beta, E1_SQ, R, F, s):
        """
        Calculate mu from beta.

        Args:
            beta (np.ndarray): Beta values.
            E1_SQ (float): Square of first eccentricity.
            R (float): Earth radius.
            F (float): Flattening factor.
            s (np.ndarray): S values.

        Returns:
            np.ndarray: Mu values.
        """
        return np.arctan((self.z + (E1_SQ * (1 - F) / (1 - E1_SQ) * R * np.sin(beta)**3)) / 
                         (s - E1_SQ * R * np.cos(beta)**3))

    def calculate_azel(self, target):
        """
        Calculate the azimuth and elevation of a target satellite observed from self.position.

        Args:
            target (ECEF or LLA): Class objects containing one or multiple satellite positions.

        Returns:
            np.ndarray: 2D array, column 0 contains azimuth, column 1 elevation, both in degrees.
        """
        self.logger.info("Calculating azimuth and elevation")
        obs_lla = self.ecef2lla()
        return obs_lla.calculate_azel(target)

    def ecef2enu(self, lat_ref, lon_ref, alt_ref):
        """
        Transform ECEF coordinates to ENU coordinates relative to a reference point.

        Args:
            lat_ref (float): Latitude position of new local origin, in radians.
            lon_ref (float): Longitude position of new local origin, in radians.
            alt_ref (float): Altitude position of new local origin, in meters.

        Returns:
            ENU: ENU object containing transformed positions.
        """
        self.logger.info("Converting ECEF to ENU")
        from Coord import ENU, LLA
        
        ref_point = LLA([lat_ref, lon_ref, alt_ref], 'R')
        ecef_ref = ref_point.lla2ecef()
        delta = self.position - ecef_ref.position
        
        R = np.array([[-np.sin(lon_ref), np.cos(lon_ref), 0],
                      [-np.cos(lon_ref) * np.sin(lat_ref), -np.sin(lon_ref) * np.sin(lat_ref), np.cos(lat_ref)],
                      [np.cos(lon_ref) * np.cos(lat_ref), np.sin(lon_ref) * np.cos(lat_ref), np.sin(lat_ref)]])
    
        e, n, u = R.dot(delta.T)
        
        return ENU([e, n, u], ref_point)

    def _is_degrees(self, value):
        """
        Check if the value is within the typical range of latitudes/longitudes in degrees.

        Args:
            value (np.ndarray): Value to check.

        Returns:
            bool: True if any value in the input series is larger than 2pi.
        """
        return np.abs(value).max() > 2 * np.pi

class TestECEF(unittest.TestCase):
    def setUp(self):
        self.ecef = ECEF([1, 2, 3])

    def test_initialization(self):
        self.assertEqual(self.ecef.size, 1)
        np.testing.assert_array_equal(self.ecef.position, np.array([[1, 2, 3]]))

    def test_distance_to_point(self):
        point = ECEF([4, 5, 6])
        distance = self.ecef.distance_to_point(point)
        self.assertAlmostEqual(distance[0], np.sqrt(27), places=7)

    def test_distance_pairwise(self):
        other = ECEF([4, 5, 6])
        distance = self.ecef.distance_pairwise(other)
        self.assertAlmostEqual(distance[0], np.sqrt(27), places=7)

def test_ecef2lla():
    print("Testing ECEF to LLA conversion")
    from Coord import LLA, ENU  # Assuming Coord module and LLA, ENU classes are available
    
    
    # Test cases: [lat, lon, alt]
    test_points = [
        [0, 0, 0],  # Origin
        [90, 0, 0],  # North Pole
        [-90, 0, 0],  # South Pole
        [0, 180, 0],  # Opposite the prime meridian
        [45, 45, 1000],  # Mid-latitude, mid-longitude, some altitude
        [-33.8688, 151.2093, 100],  # Sydney Opera House
        [27.9881, 86.9250, 8848],  # Mount Everest
    ]
    
    lat_tol = 1e-8  # About 1 mm
    lon_tol = 1e-8
    alt_tol = 0.01  # 1 cm
    
    for lat, lon, alt in test_points:
        lla_original = LLA([[lat, lon, alt]], unit='D')
        ecef = lla_original.lla2ecef()
        lla_converted = ecef.ecef2lla()
        
        try:
            np.testing.assert_allclose(lla_original.lat_d, lla_converted.lat_d, atol=lat_tol)
            np.testing.assert_allclose(lla_original.lon_d, lla_converted.lon_d, atol=lon_tol)
            np.testing.assert_allclose(lla_original.alt_m, lla_converted.alt_m, atol=alt_tol)
            print(f"Test passed for point: {lat}, {lon}, {alt}")
        except AssertionError as e:
            print(f"Test failed for point: {lat}, {lon}, {alt}")
            print(f"Original: {lla_original.position}")
            print(f"Converted: {lla_converted.position}")
            print(f"Error: {e}")
            
    multiple_points = np.array(test_points)
    
    lla_original = LLA(multiple_points, unit='D')
    ecef = lla_original.lla2ecef()
    lla_converted = ecef.ecef2lla()
    
    try:
        np.testing.assert_allclose(lla_original.lat_d, lla_converted.lat_d, atol=lat_tol)
        np.testing.assert_allclose(lla_original.lon_d, lla_converted.lon_d, atol=lon_tol)
        np.testing.assert_allclose(lla_original.alt_m, lla_converted.alt_m, atol=alt_tol)
        print("Test passed for multiple points")
    except AssertionError as e:
        print("Test failed for multiple points")
        print(f"Original: {lla_original.position}")
        print(f"Converted: {lla_converted.position}")
        print(f"Error: {e}")

def test_ecef2lla_pyproj():
    import pyproj
    print("Testing ECEF to LLA conversion against pyproj")
    
    ecef = pyproj.Proj(proj='geocent', ellps='WGS84', datum='WGS84')
    lla = pyproj.Proj(proj='latlong', ellps='WGS84', datum='WGS84')
    transformer = pyproj.Transformer.from_proj(ecef, lla)
    
    test_points_ecef = [
        [-14195384.890999997,17401583.791000005, 14424579.729999999], # from sp3
        [6378137, 0, 0],  # On equator, prime meridian
        [0, 0, 6356752.3],  # North pole
        [-1280000, 6090000, 1570000],  # Random point
        [1934171.273, -15383634.799,  21559519.653], #more sp3
        [-238566.920, -25980972.201,  14187168.898] 
    ]
    
    
    lat_tol = 1e-8  # About 1 mm
    lon_tol = 1e-8
    alt_tol = 0.01  # 1 cm
    
    for x, y, z in test_points_ecef:
        ecef_point = ECEF([[x, y, z]])
        lla_converted = ecef_point.ecef2lla()
        
        lon, lat, alt = transformer.transform(x, y, z, radians=False)
        
        try:
            np.testing.assert_allclose(lla_converted.lat_d, lat, atol=lat_tol)
            np.testing.assert_allclose(lla_converted.lon_d, lon, atol=lon_tol)
            np.testing.assert_allclose(lla_converted.alt_m, alt, atol=alt_tol)
            print(f"Test passed for ECEF point: {x}, {y}, {z}")
        except AssertionError as e:
            print(f"Test failed for ECEF point: {x}, {y}, {z}")
            print(f"Converted: {lla_converted.position}")
            print(f"PyProj: {lat}, {lon}, {alt}")
            print(f"Error: {e}")
            
    multiple_points = np.array(test_points_ecef)
    ecef_points = ECEF(multiple_points)
    lla_converted_multi = ecef_points.ecef2lla()
    
    for i, (x, y, z) in enumerate(test_points_ecef):
        lon, lat, alt = transformer.transform(x, y, z, radians=False)
        try:
            np.testing.assert_allclose(lla_converted_multi.lat_d[i], lat, atol=lat_tol)
            np.testing.assert_allclose(lla_converted_multi.lon_d[i], lon, atol=lon_tol)
            np.testing.assert_allclose(lla_converted_multi.alt_m[i], alt, atol=alt_tol)
            print(f"Test passed for multipoints: {x}, {y}, {z}")
        except AssertionError as e:
            print(f"Test failed for multipoints: {x}, {y}, {z}")
            print(f"Converted: {lla_converted_multi.position[i]}")
            print(f"PyProj: {lat}, {lon}, {alt}")
            print(f"Error: {e}")
            
if __name__ == '__main__':
    unittest.main(argv=[''], exit=False)
    test_ecef2lla()
    test_ecef2lla_pyproj()
