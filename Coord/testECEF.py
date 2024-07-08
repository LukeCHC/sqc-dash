# -*- coding: utf-8 -*-
"""
Created on Wed Sep 27 11:37:52 2023

@author: chcuk
"""

import unittest
import numpy as np
from Coord import coordFormat as cf

"""
This script uses Python's unittest framework to perform unit testing on the ecef class. 

The TestECEF class inherits from unittest.TestCase, making it a test case class. Each method within TestECEF that starts with 'test_' is considered a test case and will be run by the test runner.

1. setUp(): This method is run before each test case to set up the testing environment, e.g., initialize objects.

2. test_add(), test_distance(), etc.: These are individual test cases. They use unittest's assertion methods to check if the code being tested returns the expected results.

3. unittest.main(): This function serves as the test runner that discovers and runs all the test cases. It automatically identifies any methods that start with 'test_' to run them as test cases.

To run the tests, simply execute this script. The test runner will output the results, indicating which tests passed or failed.
"""

# note, need to add in tests for other functions

class TestECEF(unittest.TestCase):
    def setUp(self):
        # Initialize ecef objects
        self.position1 = np.array([[1, 2, 3]])  # Making it 2D
        self.velocity1 = np.array([[4, 5, 6]])  # Making it 2D
        self.ecef1 = cf.ecef(self.position1, self.velocity1)

        self.position2 = np.array([[7, 8, 9]])  # Making it 2D
        self.velocity2 = np.array([[10, 11, 12]])  # Making it 2D
        self.ecef2 = cf.ecef(self.position2, self.velocity2)

    def test_init(self):
        np.testing.assert_array_equal(self.ecef1.position, self.position1)
        np.testing.assert_array_equal(self.ecef1.velocity, self.velocity1)

    def test_add(self):
        ecef_sum = self.ecef1 + self.ecef2
        expected_position = self.position1 + self.position2
        expected_velocity = self.velocity1 + self.velocity2
        np.testing.assert_array_equal(ecef_sum.position, expected_position)
        np.testing.assert_array_equal(ecef_sum.velocity, expected_velocity)

    def test_distance(self):
        expected_distance = np.linalg.norm(self.position1 - self.position2, axis=1)
        calculated_distance = self.ecef1.distance(self.ecef2)
        np.testing.assert_almost_equal(calculated_distance, expected_distance)

    def test_ecef2rac(self):
        brdc = cf.ecef(np.array([7, 8, 9]))
        # Add code to compute expected RAC coordinates
        # np.testing.assert_array_almost_equal(self.ecef1.ecef2rac(brdc), expected_rac, decimal=9)

    def test_ecef2ned(self):
        # Add code to compute expected NED coordinates
        # np.testing.assert_array_almost_equal(self.ecef1.ecef2ned(self.ecef2), expected_ned, decimal=9)
        pass
    
    def test_ecef2enu(self):
        # Add code to compute expected ENU coordinates
        # np.testing.assert_array_almost_equal(self.ecef1.ecef2enu(self.ecef2), expected_enu, decimal=9)
        pass
    
    def test_ecef2lla(self):
        # Add code to compute expected LLA coordinates
        # np.testing.assert_array_almost_equal(self.ecef1.ecef2lla(), expected_lla, decimal=9)
        pass
    
    def test_satazel(self):
        sat = cf.ecef(np.array([7, 8, 9]))
        # Add code to compute expected azimuth and elevation angles
        # np.testing.assert_array_almost_equal(self.ecef1.satazel(sat), expected_azel, decimal=9)


if __name__ == '__main__':
    unittest.main()

