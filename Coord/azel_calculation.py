# -*- coding: utf-8 -*-
"""
Created on Tue Jan 23 14:30:23 2024

@author: chcuk
"""

# source: 

import numpy as np

class AltAzimuthRange():
    """
    A class to calculate the azimuth, elevation and distance between an observer and a target.
    
    This version of the code has been modified to accept numpy arrays as input. 
    This allows for the calculation of multiple targets in one sweep using vector calucations.
    
    Note that inputs and outputs are in degrees.

    Original source:
    https://github.com/sq3tle/altazrange/blob/master/AltAzRange/AltAzRange.py
    
    """
    def __init__(self, observer_arr, target_arr):
        
        self.LAT_IDX, self.LON_IDX, self.ALT_IDX = 0, 1, 2
        self.observer = self.validate_input(observer_arr)
        self.target = self.validate_input(target_arr, is_observer=False)
        
        
    def validate_input(self, arr, is_observer=True):
        if isinstance(arr, list):
            arr = np.array(arr)
        if isinstance(arr, np.ndarray):
            # Reshape 1D numpy array of size 3 to 2D array with shape (1, 3)
            if arr.ndim == 1 and arr.size == 3:
                arr = arr.reshape(1, 3)
            # Check if the array is now 2D and has the correct number of columns
            if arr.ndim != 2 or arr.shape[1] != 3:
                raise ValueError("Input must be a 2D numpy array with shape (N, 3)")
        else:
            raise TypeError("Input must be a list or a numpy array")
        return arr
             
    def normalise_azimuth(self, azimuths:np.ndarray):
        """ensure that azimuth is within 0-360 degrees, written by luke"""
        # Ensure azimuths are within [0, 360)
        azimuths = np.mod(azimuths, 360)
        # Adjust values that are exactly 360 to 0 (since 360 degrees is equivalent to 0 degrees)
        # azimuths[azimuths == 360] = 0
        azimuths = np.round(azimuths, 4)

        return azimuths        
        
    def calculate(self) -> dict:
        ap = self.LocationToPoint(self.observer)
        bp = self.LocationToPoint(self.target)
        bp_radius = bp[:,4] 
        br = self.RotateGlobe(self.target, self.observer, bp_radius)
        dist = np.round(AltAzimuthRange.Distance(ap, bp), 4)
        
        azimuth = np.full(bp.shape[0], np.nan)
        elevation = np.full(bp.shape[0], np.nan)
        
        valid_indices = (br[:, 2] * br[:, 2] + br[:, 1] * br[:, 1]) > 1.0e-6
        
        if valid_indices.any():
        
            theta = np.arctan2(br[valid_indices,2], br[valid_indices,1]) * 180.0 / np.pi
            azimuth[valid_indices] = self.normalise_azimuth(90.0 - theta)
    
            bma = AltAzimuthRange.NormalizeVectorDiff(bp, ap)
            if bma is not None:
                elevation[valid_indices] = 90.0 - (180.0 / np.pi) * np.arccos(
                    bma[valid_indices,0] * ap[:,4] + bma[valid_indices,1] * ap[:,5] + bma[valid_indices,2] * ap[:,6])
                elevation = np.round(elevation, 4)
            else:
                elevation = None
        else:
            azimuth = None
            elevation = None
            
        return_arr = np.vstack([azimuth, elevation, dist]).T.reshape(-1, 3)
        
        return return_arr
        
    def calculate_(self) -> dict:
        ap = self.LocationToPoint(self.observer)
        bp = self.LocationToPoint(self.target)
        bp_radius = bp[:,4] 
        br = self.RotateGlobe(self.target, self.observer, bp_radius)
        dist = np.round(AltAzimuthRange.Distance(ap, bp), 4)
        if (br[:,2] * br[:,2] + br[:,1] * br[:,1] > 1.0e-6).all():
            theta = np.arctan2(br[:,2], br[:,1]) * 180.0 / np.pi
            azimuth = 90.0 - theta
            azimuth = self.normalise_azimuth(azimuth)
    
            bma = AltAzimuthRange.NormalizeVectorDiff(bp, ap)
            if bma.all():
                elevation = 90.0 - (180.0 / np.pi) * np.arccos(
                    bma[:,0] * ap[:,4] + bma[:,1] * ap[:,5] + bma[:,2] * ap[:,6])
                elevation = np.round(elevation, 4)
            else:
                elevation = None
        else:
            azimuth = None
            elevation = None
            
        return_arr = np.vstack([azimuth, elevation, dist]).T.reshape(-1, 3)
        
        return return_arr
        # return {"azimuth": azimuth.item(), "elevation": elevation.item(), "distance": dist.item()}

    @staticmethod
    def default_observer(lat: float, long: float, altitude: float):
        AltAzimuthRange.default_lat = lat
        AltAzimuthRange.default_long = long
        AltAzimuthRange.default_elv = altitude

    @staticmethod
    def Distance(ap, bp):
        dx = ap[:,0] - bp[:,0]
        dy = ap[:,1] - bp[:,1]
        dz = ap[:,2] - bp[:,2]
        return np.sqrt(dx * dx + dy * dy + dz * dz)

    @staticmethod
    def GeocentricLatitude(lat):
        e2 = 0.00669437999014
        clat = np.arctan((1.0 - e2) * np.tan(lat))
        return clat

    @staticmethod
    def EarthRadiusInMeters(latituderadians):
        a = 6378137.0
        b = 6356752.3
        cos = np.cos(latituderadians)
        sin = np.sin(latituderadians)
        t1 = a * a * cos
        t2 = b * b * sin
        t3 = a * cos
        t4 = b * sin
        return np.sqrt((t1 * t1 + t2 * t2) / (t3 * t3 + t4 * t4))

    def LocationToPoint(self, lla_arr):
        
        lat = lla_arr[:,self.LAT_IDX] * np.pi / 180.0
        lon = lla_arr[:,self.LON_IDX] * np.pi / 180.0
        radius = AltAzimuthRange.EarthRadiusInMeters(lat)
        clat = AltAzimuthRange.GeocentricLatitude(lat)

        cos_lon = np.cos(lon)
        sin_lon = np.sin(lon)
        cos_lat = np.cos(clat)
        sin_lat = np.sin(clat)
        x = radius * cos_lon * cos_lat
        y = radius * sin_lon * cos_lat
        z = radius * sin_lat

        cos_glat = np.cos(lat)
        sin_glat = np.sin(lat)

        nx = cos_glat * cos_lon
        ny = cos_glat * sin_lon
        nz = sin_glat

        x += lla_arr[:,self.ALT_IDX] * nx
        y += lla_arr[:,self.ALT_IDX] * ny
        z += lla_arr[:,self.ALT_IDX] * nz

         # {'x': x, 'y': y, 'z': z, 'radius': radius, 'nx': nx, 'ny': ny, 'nz': nz}
        return_arr = np.vstack([x, y, z, radius, nx, ny, nz]).T.reshape(-1, 7)

        return return_arr

    @staticmethod
    def NormalizeVectorDiff(target, observer):
        dx = target[:,0] - observer[:,0]
        dy = target[:,1] - observer[:,1]
        dz = target[:,2] - observer[:,2]
        dist2 = dx * dx + dy * dy + dz * dz
        if (dist2 == 0).any():
            return None
        dist = np.sqrt(dist2)
        
        # {'x': (dx / dist), 'y': (dy / dist), 'z': (dz / dist), 'radius': 1.0}
        return_arr = np.vstack([dx / dist, dy / dist, dz / dist, np.ones_like(dist)]).T.reshape(-1, 4)
        
        return return_arr

    def RotateGlobe(self, target, observer, target_radius):
        br = np.array([target[:,self.LAT_IDX],  (target[:,self.LON_IDX] - observer[:,self.LON_IDX]), target[:,self.ALT_IDX]]).T
        brp = self.LocationToPoint(br)

        alat = AltAzimuthRange.GeocentricLatitude(-observer[:,self.LAT_IDX] * np.pi / 180.0)
        acos = np.cos(alat)
        asin = np.sin(alat)

        bx = (brp[:,0] * acos) - (brp[:,2] * asin)
        by = brp[:,1]
        bz = (brp[:,0] * asin) + (brp[:,2] * acos)

        #{'x': bx, 'y': by, 'z': bz, 'radius': target_radius}
        return_arr = np.vstack([bx, by, bz, target_radius]).T.reshape(-1, 4)

        return return_arr


if __name__ == "__main__":



    observer = np.array([51.773931, 18.061959, 50])
    target = np.array([[51.681562, 17.778988, 430000],
                      [52.30, 21.37, 190000]])
    
    
    calculator = AltAzimuthRange(observer, target)

    result = calculator.calculate()
    
    print(result)