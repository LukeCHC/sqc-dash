# -*- coding: utf-8 -*-
"""
Created on Wed May  4 12:19:17 2022

@author: chcuk
"""
# -*- coding: utf-8 -*-
"""
Created on Thu Apr 28 10:20:59 2022

@author: chcuk
"""
import numpy as np
import math
from numpy.linalg import norm
# from Common.common import PI
from typing import Union # this allows the inputs to be of multiple different types
import warnings

class ecef:
    # <-- Class constants for magic numbers
    EARTH_RADIUS = 6378137  # meters 
    E1_SQ = 6.69437999014e-3  # First eccentricity squared 
    
    # Used to be named WGS84_A = 6378137.0
    # below is how we calculate E1_SQ
    # WGS84_f = 1 / 298.257223565
    # WGS84_E2 = WGS84_f * (2 - WGS84_f) 
    
    def __init__(self, position: Union[np.ndarray, list, tuple], velocity: Union[np.ndarray, list, tuple] = None):
        """
        Initialize the ECEF object with position and velocity.
        
        Args:
            position (Union[np.ndarray, list, tuple]): The position in ECEF coordinates.
            velocity (Union[np.ndarray, list, tuple], optional): The velocity. Defaults to None.
            
        Raises:
            ValueError: If shapes of position and velocity mismatch.
        """
        # <-- Type checking and reshaping moved to a private method
        self.position, self.velocity = self._check_input(position, velocity)
        self.x, self.y, self.z = self.position.T

    def _check_input(self, position, velocity):
        """
        Check and reshape input position and velocity.
        
        Args:
            position: The position array.
            velocity: The velocity array.
            
        Returns:
            tuple: Reshaped position and velocity arrays.
        """
        if not isinstance(position, np.ndarray):
            position = np.array(position).reshape(-1, 3)
        
        if velocity is None:
            velocity = np.zeros_like(position)
        
        if not isinstance(velocity, np.ndarray):
            velocity = np.array(velocity).reshape(-1, 3)
        
        if position.shape != velocity.shape:
            raise ValueError("Position and velocity shapes mismatch")  # <-- Raise exception instead of print
            
        return position, velocity
    
    def __add__(self, ecef2):
        xp = self.position[:, 0] + ecef2.position[:, 0]
        yp = self.position[:, 1] + ecef2.position[:, 1]
        zp = self.position[:, 2] + ecef2.position[:, 2]
        xv = self.velocity[:, 0] + ecef2.velocity[:, 0]
        yv = self.velocity[:, 1] + ecef2.velocity[:, 1]
        zv = self.velocity[:, 2] + ecef2.velocity[:, 2]
        # Making sure the arrays are in the expected shape
        new_position = np.array([xp, yp, zp]).T
        new_velocity = np.array([xv, yv, zv]).T
        return ecef(new_position, new_velocity)


    def distance(self, point2) -> np.ndarray:
        pos1 = self.position
        pos2 = point2.position
        dist = np.linalg.norm(pos1 - pos2, axis=1)  # Used NumPy for vectorized operation
        return dist
    
    def ecef2rac(self, brdc) -> 'rac':  # Assuming rac is a predefined class
        """
        Convert ECEF coordinates to RAC (Radial, Along-track, Cross-track) coordinates.
        
        Parameters:
            brdc (ecef): An ECEF object calculated from brdc eph of rac body.
            
        Returns:
            rac: A rac object containing the converted coordinates.
        """
        # Validate shape of brdc position to match with self.position
        if brdc.position.shape != self.position.shape:
            warnings.warn("array shape mismatch")
        
        # Calculate eAlong, eCross, and eRadial vectors
        eAlong = brdc.velocity / np.linalg.norm(brdc.velocity, axis=1, keepdims=True)
        eCross = np.cross(brdc.position, brdc.velocity)
        eCross /= np.linalg.norm(eCross, axis=1, keepdims=True)
        eRadial = np.cross(eAlong, eCross)
        
        # Initialize arrays for RAC coordinates
        arrRAC = np.full(self.position.shape, np.nan)
        arrRACV = np.full(self.position.shape, np.nan)
        
        # Perform matrix operations to convert to RAC
        for m in range(arrRAC.shape[0]):
            matRAC = np.linalg.inv(np.array([eRadial[m, :], eAlong[m, :], eCross[m, :]]).T)
            arrRAC[m, :] = np.dot(matRAC, self.position[m])
            arrRACV[m, :] = np.dot(matRAC, self.velocity[m])
        
        return rac(arrRAC, arrRACV)  
    
    def ecef2ned(self, ecef2):
        lla = self.ecef2lla()
        mu, lon = lla.latR, lla.lonR
        # Replaced magic numbers with named constants
        DCM = np.array([
            [-np.sin(mu) * np.cos(lon), -np.sin(mu) * np.sin(lon), np.cos(mu)],
            [-np.sin(lon), np.cos(lon), 0],
            [-np.cos(mu) * np.cos(lon), -np.cos(mu) * np.sin(lon), -np.sin(mu)]
        ])
        return DCM @ ecef2.position  # Used '@' as matrix multiplication
    
    def ecef2enu(self, ecef2) -> np.ndarray:
        """Convert ECEF to ENU coordinates."""
        n_positions = len(ecef2.position)
        arrenu = np.full(ecef2.position.shape, np.nan)
        
        lla = self.ecef2lla()
        mu, lon = lla.latR, lla.lonR
        
        sinp = np.sin(mu)
        cosp = np.cos(mu)
        sinl = np.sin(lon)
        cosl = np.cos(lon)
        
        for i in range(n_positions):
            DCM = np.array([
                [-sinl[i], cosl[i], 0],
                [-sinp[i]*cosl[i], -sinp[i]*sinl[i], cosp[i]],
                [cosp[i]*cosl[i], cosp[i]*sinl[i], sinp[i]]
            ])
            
            arrenu[i, :] = np.dot(DCM, ecef2.position[i])
        
        return arrenu
    
    def ecef2enu_m(self) -> list:
        # Need to verify this function
        """Calculate ECEF to local coordinate transformation matrix."""
        DCMS = []
        lla = self.ecef2lla()
        mu, lon = lla.latR, lla.lonR
        
        sinp = np.sin(mu)
        cosp = np.cos(mu)
        sinl = np.sin(lon)
        cosl = np.cos(lon)
        
        for i in range(len([self.position])):
            DCM = np.array([
                [-sinl[i], cosl[i], 0],
                [-sinp[i]*cosl[i], -sinp[i]*sinl[i], cosp[i]],
                [cosp[i]*cosl[i], cosp[i]*sinl[i], sinp[i]]
            ])
            
            DCMS.append(DCM)
        
        return DCMS
    
    def ecef2lla(self) -> 'lla':  # Assuming lla is a predefined class
        """Convert ECEF coordinates to LLA (Latitude, Longitude, Altitude)."""
        # Constants
        semi_major = 6378137.0  # Semi-major axis in meters
        semi_minor = 6356752.3142  # Semi-minor axis in meters
        f = (semi_major - semi_minor) / semi_major  # Flattening
        
        # Reshape x, y, z to row vectors for easier manipulation
        x, y, z = self.x.reshape(1, -1), self.y.reshape(1, -1), self.z.reshape(1, -1)
        
        s = np.sqrt(x ** 2 + y ** 2)
        
        # Initial values for iterative method
        beta0 = np.arctan2(z, (1 - f) * s)
        mu0 = np.zeros_like(beta0)
        mu1 = np.ones_like(beta0)
        
        # Iteratively solve for mu
        while np.abs(mu1 - mu0).mean() > 1e-9:
            mu0 = self._fromBeta2Mu(beta0, self.E1_SQ, self.EARTH_RADIUS, f, s, z)
            beta1 = self._fromMu2Beta(mu0, f)
            mu1 = self._fromBeta2Mu(beta1, self.E1_SQ, self.EARTH_RADIUS, f, s, z)
            beta0 = beta1
        
        N = self.EARTH_RADIUS / np.sqrt(1 - self.E1_SQ * np.sin(mu1) ** 2)
        h = s * np.cos(mu1) + (z + self.E1_SQ * N * np.sin(mu1)) * np.sin(mu1) - N
        
        lonR = np.arctan2(y, x)
        latR = mu1
        altM = h
        
        res = np.vstack((latR, lonR, altM)).T
        return lla(res, "R")  # Assuming lla is a predefined class

    # Private helper functions for ecef2lla
    def _fromBeta2Mu(self, beta, esq, R, f, s, z):
        up = z + esq * (1 - f) * R * np.sin(beta) ** 3 / (1 - esq)
        down = s - esq * R * np.cos(beta) ** 3
        return np.arctan2(up, down)
    
    def _fromMu2Beta(self, mu, f):
        return np.arctan((1 - f) * np.tan(mu))
    
    def satazel(self, ecefsats):
        """
        Calculate azimuth and elevation angles from satellite positions in ECEF coordinates.
        
        Args:
            ecefsats (ECEF): ECEF object containing satellite positions.
            
        Returns:
            np.ndarray: Array containing azimuth and elevation angles.
        """
        xyzr = self.position  # Receiver position
        xyzs = ecefsats.position  # Satellite positions
        ns = xyzs.shape[0]  # Number of satellites

        # Pre-allocate memory for azimuth and elevation angles
        azel = np.zeros((ns, 2))
        
        # Calculate transformation matrix once if it's the same for all satellites
        TM = self.ecef2enu_m()[0]

        for i in range(ns):
            e = xyzs[i, :] - xyzr
            r = norm(e, 2)
            e /= r  # Receiver-to-satellite unit vector in ECEF
            
            # Vector in local tangential coordinate
            enu = np.dot(TM, e.T).reshape(-1)

            # Calculate azimuth and elevation
            t = np.dot(enu, enu)
            az = 0 if t < 1e-12 else np.arctan2(enu[0], enu[1])
            az = az + 2 * np.pi if az < 0 else az
            el = np.arcsin(enu[2])

            azel[i, :] = [az, el]

        return azel
    
    def satazel_vectorised(self, sat_pos):
        """
        Improved version that doesnt use loops
        self.position should be recv/ observer position
        
        pretty sure values are wrong, need to fix
        
        Args:
         sat_pos (ecef): An ecef object containing position of satellites 
        """
        xyzr = self.position  # Receiver position
        xyzs = sat_pos.position  # Satellite positions
    
        # Vectorized difference
        e = xyzs - xyzr
        r = np.linalg.norm(e, axis=1)
        e /= r[:, np.newaxis]  # Normalize each vector
    
        # Transformation matrix
        TM = self.ecef2enu_m()[0]  # Assuming TM is constant for all positions
    
        # Vectorized matrix multiplication
        enu = np.dot(e, TM.T)
    
        # Vectorized azimuth and elevation calculation
        az = np.arctan2(enu[:, 0], enu[:, 1])
        az[az < 0] += 2 * np.pi
        el = np.arcsin(enu[:, 2])
    
        # Combine azimuth and elevation
        azel = np.vstack((az, el)).T
    
        return azel


    

class ecefOld:
    def __init__(self, position, velocity=None):
        if type(position) == np.ndarray:
            if position.ndim != 2: #check array is 2d e.g shape = (1,3)
               print("Wrong number of dimensions, should be 2") 
        if type(position) == list or type(position) == tuple:
            position = np.array([position]).reshape(3,-1).T # turn list to 2d array
        if velocity == None:
            self.velocity = velocity = np.array([[0,0,0] for i in range(len(position))])
        if type(velocity) == list or type(velocity) == tuple :
            velocity = np.array([velocity]).reshape(3,-1).T # turn list to 2d array
        if np.shape(position) != np.shape(velocity):
            print("position and velocity shapes mismatch")
        if len(position[:,0]) == len(position[:,1]) ==len(position[:,2]):
            self.x        = position[:,0]
            self.y        = position[:,1]
            self.z        = position[:,2]
            self.position = np.array([[self.x[i], self.y[i], self.z[i]] for i in range(len(self.x))])
        else: Warning("Length of x, y, z arrays do not match")
        if len(velocity[:,0]) == len(velocity[:,1]) ==len(velocity[:,2]):
            self.vx        = velocity[:,0]
            self.vy        = velocity[:,1]
            self.vz        = velocity[:,2]
            self.velocity = np.array([[self.vx[i], self.vy[i], self.vz[i]] for i in range(len(self.x))])
        
        else: Warning("Length of vx, vy, vz arrays do not match")
        
        # check for float

    def __add__(self, ecef2):
        xp = self.position[:,0] + ecef2.postion[:,0]
        yp = self.position[:,1] + ecef2.postion[:,1]
        zp = self.position[:,2] + ecef2.postion[:,2]
        xv = self.velocity[:,0] + ecef2.postion[:,0]
        yv = self.velocity[:,1] + ecef2.postion[:,1]
        zv = self.velocity[:,2] + ecef2.postion[:,2]
        return ecef(np.array([xp, yp, zp]), np.array([xv, yv, zv]))

    def distance(self, point2):
        pos1 = self.position
        pos2 = point2.position

        dist = [np.linalg.norm(pos1[i]- pos2[i]) for i in range(len(pos1))]
        return dist

    def ecef2rac(self, brdc):
        """ based on inverse matrix of rac2ecef"""
        # brdc is another ecef calclated from brdc eph of rac body
        # brdc should be same shape as position velocity
        xyzPos = self.position
        if brdc.position.shape != xyzPos.shape:
            Warning("array shape mismatch")
        eAlongL = [
            brdc.velocity[i] / np.linalg.norm(brdc.velocity[i], keepdims=True)
            for i in range(np.shape(xyzPos)[0])
        ]

        eAlong = np.array(eAlongL)
        # eCrossL = [
        #     np.cross(xyzPos[i], xyzVel[i])
        #     / np.linalg.norm(np.cross(xyzPos[i], xyzVel[i]), keepdims=True)
        #     for i in range(xyzPos.shape[0])
        # ]
        eCrossL = [
            np.cross(brdc.position[i], brdc.velocity[i])
            / np.linalg.norm(np.cross(brdc.position[i], brdc.velocity[i]), keepdims=True)
            for i in range(brdc.position.shape[0])
        ]
        eCross = np.array(eCrossL)
        eRadial = np.cross(eAlong, eCross)
        arrRAC = np.full((xyzPos.shape), np.nan)
        arrRACV = np.full((xyzPos.shape), np.nan)
        for m in range(arrRAC.shape[0]):
            matRAC = np.array(
                np.matrix([eRadial[m, :], eAlong[m, :], eCross[m, :]]).T.I
            )
            arrRAC[m, :] = np.dot(matRAC, self.position[m])
            arrRACV[m, :] = np.dot(matRAC, self.velocity[m])
        # for m in range(arrRAC.shape[0]):
        #    matRAC = np.array(
        #            np.matrix([eRadial[m], eAlong[m], eCross[m]]).T.I
        #        )
        #    arrRAC[m,:] = np.dot(matRAC, self.position[m])
        return rac(arrRAC, arrRACV)

    def ecef2rac_(self, XYZ):
        """ based on ecef (0,0,0) """
        xyzPos = self.brdcXYZ
        xyzVel = self.brdcXYZVel
        eRadialL = [
            xyzPos[i, :, :] / np.linalg.norm(xyzPos[i, :, :], axis=1, keepdims=True)
            for i in range(xyzPos.shape[0])
        ]
        eRadial = np.array(eRadialL)
        eCrossL = [
            np.cross(xyzPos[i, :, :], xyzVel[i, :, :])
            / np.linalg.norm(
                np.cross(xyzPos[i, :, :], xyzVel[i, :, :]), axis=1, keepdims=True
            )
            for i in range(xyzPos.shape[0])
        ]
        eCross = np.array(eCrossL)
        eAlongL = [
            np.cross(eCross[i, :, :], eRadial[i, :, :])
            / np.linalg.norm(
                np.cross(eCross[i, :, :], eRadial[i, :, :]), axis=1, keepdims=True
            )
            for i in range(xyzPos.shape[0])
        ]
        eAlong = np.array(eAlongL)
        arrRAC = np.full((xyzPos.shape), np.nan)
        for i in range(arrRAC.shape[0]):
            for m in range(arrRAC.shape[1]):
                matRAC = np.array(
                    [eRadial[i, m, :], eAlong[i, m, :], eCross[i, m, :]]
                ).T
                arrRAC[i, m, :] = np.dot(matRAC, XYZ[i, m, :])
        return arrRAC

    def ecef2ned(self, ecef2):
        # geodetic North East Down
        lla = self.ecef2lla()
        mu = lla.latR
        lon = lla.lonR

        DCM = np.matrix(
            [
                [
                    -math.sin(mu) * math.cos(lon),
                    -math.sin(mu) * math.sin(lon),
                    math.cos(mu),
                ],
                [-math.sin(lon), math.cos(lon), 0],
                [
                    -math.cos(mu) * math.cos(lon),
                    -math.cos(mu) * math.sin(lon),
                    -math.sin(mu),
                ],
            ]
        )

        ecefVector = np.matrix(
            [ecef2.position[0], ecef2.position[1], ecef2.position[2]]
        ).T
        # returns a vector of size 3
        return np.matmul(DCM, ecefVector)
    
    def ecef2enu(self, ecef2) -> np.ndarray:
        """Convert ECEF to ENU coordinates."""
        n_positions = len(ecef2.position)
        arrenu = np.full(ecef2.position.shape, np.nan)
        
        lla = self.ecef2lla()
        mu, lon = lla.latR, lla.lonR
        
        sinp = np.sin(mu)
        cosp = np.cos(mu)
        sinl = np.sin(lon)
        cosl = np.cos(lon)
        
        for i in range(n_positions):
            DCM = np.array([
                [-sinl[i], cosl[i], 0],
                [-sinp[i]*cosl[i], -sinp[i]*sinl[i], cosp[i]],
                [cosp[i]*cosl[i], cosp[i]*sinl[i], sinp[i]]
            ])
            
            arrenu[i, :] = np.dot(DCM, ecef2.position[i])
        
        return arrenu
    
    def ecef2enu_m(self) -> list:
        """Calculate ECEF to local coordinate transformation matrix."""
        DCMS = []
        lla = self.ecef2lla()
        mu, lon = lla.latR, lla.lonR
        
        sinp = np.sin(mu)
        cosp = np.cos(mu)
        sinl = np.sin(lon)
        cosl = np.cos(lon)
        
        for i in range(len(self.position)):
            DCM = np.array([
                [-sinl[i], cosl[i], 0],
                [-sinp[i]*cosl[i], -sinp[i]*sinl[i], cosp[i]],
                [cosp[i]*cosl[i], cosp[i]*sinl[i], sinp[i]]
            ])
            
            DCMS.append(DCM)
        
        return DCMS
    
    
    def ecef2enu(self,ecef2):
        # compute ecef to local coordinate transfromation matrix
        #                 local tangental coordinate
        # Ref: rtklib_2.4.3\src\rtccmn.c\ecef2enu
        # I: ecef (for geodetic position (lat,lon)(rad))
        #    ecef2: vector in ecef coordinate(x,y,z)
        # O: vector in local tangental coordinate(e,n,u)
        # https://en.wikipedia.org/wiki/Geographic_coordinate_conversion#From_ECEF_to_ENU
        #i = 0
        arrenu = np.full((ecef2.position.shape), np.nan)
        for i in range(len(ecef2.position)):
            lla = self.ecef2lla()
            mu = lla.latR
            lon = lla.lonR
            sinp = math.sin(mu[i])# for j in range(len(mu))]
            cosp = math.cos(mu[i])# for j in range(len(mu))]
            sinl = math.sin(lon[i])# for j in range(len(lon))]
            cosl = math.cos(lon[i]) #for j in range(len(lon))]
            DCM = np.matrix([
                    [-sinl,      cosl,      0],
                    [-sinp*cosl, -sinp*sinl,cosp],
                    [cosp*cosl,  cosp*sinl ,sinp]
                    ]) 
            arrenu[i,:] = np.dot(DCM,ecef2.position[i])
        # ecefVector = np.matrix(
        #     [ecef2.position[i][0], ecef2.position[i][1], ecef2.position[i][2]]
        # ).T
        # returns a vector of size 3
        return arrenu
    
    def ecef2enu_m(self):
        # compute ecef to local coordinate transfromation matrix(m)
        #                 local tangental coordinate
        # Ref: SysCommon.c/xyz2enu
        # I: ecef (for geodetic position (x,y,z)(m))
        #    ecef2: vector in ecef coordinate(x,y,z)
        # O: ecef to local coord transformation matrix
        DCMS = []
        for i in range(len(self.position)):
            lla = self.ecef2lla()
            mu = lla.latR  # m2rad
            lon = lla.lonR # m2rad
            sinp = math.sin(mu[i])# for j in range(len(mu))]
            cosp = math.cos(mu[i])# for j in range(len(mu))]
            sinl = math.sin(lon[i])# for j in range(len(lon))]
            cosl = math.cos(lon[i]) #for j in range(len(lon))]
            DCM = np.matrix([
                    [-sinl,      cosl,      0],
                    [-sinp*cosl, -sinp*sinl,cosp],
                    [cosp*cosl,  cosp*sinl ,sinp]
                    ]) 
            DCMS.append(DCM)
            #arrenu[i,:] = np.dot(DCM,ecef2.position[i])
        # ecefVector = np.matrix(
        #     [ecef2.position[i][0], ecef2.position[i][1], ecef2.position[i][2]]
        # ).T
        # returns a vector of size 3
        return DCMS
    
    

    def ecef2lla(self):

        x = self.x.reshape(1,-1)
        y = self.y.reshape(1,-1)
        z = self.z.reshape(1,-1)

        s = np.sqrt(x ** 2 + y ** 2)
        R = 6378137  # equatorial plane (m)
        # e = 8.1819190842622e-2  # First eccentriciy
        esq = 6.69437999014e-3  # First eccentriciy squared
        a = 6378137.0  # Semi-major axis (m)
        b = 6356752.3142  # Semi-minor axis (m)
        f = (a - b) / a

        # e = np.sqrt(1 - (1-f)**2)     # 0.08181919092890692

        def fromBeta2Mu(beta):
            # reduced latitude
            up = [z[0,i] + esq * (1 - f) * R * (math.sin(beta[i])) ** 3 / (1 - esq) for i in range(z.shape[1])]
            down = [s[0,i] - esq * R * (math.cos(beta[i])) ** 3 for i in range(z.shape[1])]

            return [math.atan(up[i] / down[i]) for i in range(len(up))]

        def fromMu2Beta(mu, f):
            # reduced eccentricity
            return [math.atan(((1 - f) * math.sin(mu[i])) / math.cos(mu[i])) for i in range(len(mu))]

        beta0 = [math.atan(z[0,i] / (1 - f) * s[0,i]) for i in range(len(z[0]))] 
        mu0, mu1 = 0, 1
        while np.abs((np.array(mu1) - np.array(mu0))).mean() > 1e-9:
            mu0 = fromBeta2Mu(beta0)
            beta1 = fromMu2Beta(mu0, f)
            mu1 = fromBeta2Mu(beta1)
            beta0 = beta1
        N = [R / (np.sqrt(1 - esq * (math.sin(mu1[i])) ** 2)) for i in range(len(mu1))]
        h = [s[0,i] * math.cos(mu1[i]) + (z[0,i] + esq * N[i] * math.sin(mu1[i])) * math.sin(mu1[i]) - N[i] for i in range(len(mu1))]

        lonR = [np.arctan2(y[0][i], x[0][i]) for i in range(len(x[0]))]
        latR = mu1
        altM = h  # ellipsoidal height
        
        res = np.array([[latR, lonR, altM]]).reshape(3,-1).T
        return lla(res, "R")
    
# =============================================================================
#     def satazel_s(self,ecefsat):
#         #I position: x,y,z
#         #O az,el azimuth/elevation(rad) 0<az<2*pi -pi/2<el<pi/2
#         xyzr = self.position
#         xyzs = ecefsat.position
#         e = np.array(xyzs) - np.array(xyzr)
#         r = norm(e,2)
#         e = e/r        #receiver-to-satellilte unit vevtor (ecef)
#         TM = self.ecef2enu_m() # Transform matrix
#         # vector in local tangental coordinate 
#         enu = np.dot(TM,e.T)
#         # matrix to array
#         enu = np.asarray(enu).reshape(-1)
#         t = np.dot(enu,enu)
#         if (t < 1e-12):
#             az = 0
#         else:
#             az = np.arctan2(enu[0],enu[1])
#         if (az < 0):
#             az += 2 * PI
#         el = np.arcsin(enu[2])
#         return az,el
# =============================================================================
    
    def satazel(self,ecefsats):
        #I position: x,y,z
        #O az,el azimuth/elevation(rad) 0<az<2*pi -pi/2<el<pi/2
        xyzr = self.position  # Note: len(self.position) =1
        xyzs = ecefsats.position
        ns = ecefsats.position.shape[0] # number of sats
        azel = []
        for i in range(ns):
            e = np.array(xyzs[i,:]) - np.array(xyzr)
            r = norm(e,2)
            e = e/r        #receiver-to-satellilte unit vevtor (ecef)
            TM = self.ecef2enu_m() # Transform matrix
            # vector in local tangental coordinate 
            enu = np.dot(TM,e.T)
            # matrix to array
            enu = np.asarray(enu).reshape(-1)
            t = np.dot(enu,enu)
            if (t < 1e-12):
                az = 0
            else:
                az = np.arctan2(enu[0],enu[1])
            if (az < 0):
                az += 2 * np.pi
            el = np.arcsin(enu[2])
            azel.append([az,el])
        return azel
    
        xyzr = self.position
        xyzs = ecefsats.position
        e = np.array(xyzs) - np.array(xyzr)
        r = norm(e,2)
        e = e/r        #receiver-to-satellilte unit vevtor (ecef)
        TM = self.ecef2enu_m() # Transform matrix
        # vector in local tangental coordinate 
        enu = np.dot(TM,e.T)
        # matrix to array
        enu = np.asarray(enu).reshape(-1)
        t = np.dot(enu,enu)
        if (t < 1e-12):
            az = 0
        else:
            az = np.arctan2(enu[0],enu[1])
        if (az < 0):
            az += 2 * np.pi
        el = np.arcsin(enu[2])
        return az,el


class rac:
    def __init__(self, position, velocity):
        self.position = position
        self.velocity = velocity
        if type(position) == np.ndarray:
            if position.ndim != 2: #check array is 2d e.g shape = (1,3)
               print("Wrong number of dimensions, should be 2") 
        if velocity == None:
            self.velocity = np.array([[0,0,0] for i in range(len(position))])
        if type(position) == list:
            self.position = np.array([position]).reshape(3,-1).T # turn list to 2d array
        if type(velocity) == list:
            self.velocity = np.array([velocity]).reshape(3,-1).T # turn list to 2d array
        if np.shape(self.position) != np.shape(self.velocity):
            print("position and velocity shapes mismatch")

    def rac2ecef(self, brdc):
        racPos = brdc.position
        racVel = brdc.velocity
        # racVel[i,:,:] ->2D
        # axis =1 for row
        eAlongL = [
            racVel[i] / np.linalg.norm(racVel[i], keepdims=True)
            for i in range(racPos.shape[0])
        ]
        eAlong = np.array(eAlongL)
        eCrossL = [
            np.cross(racPos[i], racVel[i])
            / np.linalg.norm(np.cross(racPos[i], racVel[i]), keepdims=True)
            for i in range(racPos.shape[0])
        ]
        eCross = np.array(eCrossL)
        eRadial = np.cross(eAlong, eCross)
        arrECEF = np.full((racPos.shape), np.nan)
        arrECEFV = np.full((racPos.shape), np.nan)
        for i in range(arrECEF.shape[0]):
            matRAC = np.array([eRadial[i, :], eAlong[i, :], eCross[i, :]]).T
            arrECEF[i] = np.dot(matRAC, self.position[i,:])
            arrECEFV[i] = np.dot(matRAC, self.velocity[i])
        return ecef(arrECEF, arrECEFV)


class neuATX:
    def __init__(self, position, sunPos):
        #= position [[x,y,z]]
        #  sunPos   [[x,y,z]]
        self.postion = position
        self.sunPos = sunPos

    def neu2ecef(self, arrATX):
        sunP = self.sunPos

        kValL = [
            -self.postion[i] / np.linalg.norm(-self.postion[i], keepdims=True)
            for i in range(self.postion.shape[0])
        ]
        kVal = np.array(kValL)

        eValL = [
            (sunP[i] - self.postion[i])
            / np.linalg.norm((sunP[i] - self.postion[i]), keepdims=True)
            for i in range(self.postion.shape[0])
        ]
        eVal = np.array(eValL)

        jVal0 = np.cross(kVal, eVal)
        jValL = [
            jVal0[i] / np.linalg.norm(jVal0[i], keepdims=True)
            for i in range(self.postion.shape[0])
        ]
        jVal = np.array(jValL)

        iVal = np.cross(jVal, kVal)

        arrPC = np.full((self.postion.shape[0], 3), np.nan)
        vel   = np.zeros((arrPC.shape[0],arrPC.shape[1]))
        for i in range(arrPC.shape[0]):
            matPC = np.array([iVal[i], jVal[i], kVal[i]]).T
            arrPC[i] = np.dot(matPC, arrATX[i])
        #posMC = self.posPC[:] - arrPC
        return ecef(arrPC, vel)

    def sunPos(self):

        intvalStr = "%ds" % self.intval
        dateS = [
            datetime.strptime(str(self.posPC[i, 0, 0]), "%Y%m%d%H%M%S.%f")
            for i in range(self.posPC.shape[0])
        ]
        dateE = [
            datetime.strptime(str(self.posPC[i, -1, 0]), "%Y%m%d%H%M%S.%f")
            for i in range(self.posPC.shape[0])
        ]
        dateR = [
            pd.date_range(start=dateS[i], end=dateE[i], freq=intvalStr).tolist()
            for i in range(self.posPC.shape[0])
        ]
        gpsT = [[SP3.sun().utc2gpsw(x) for x in dateR[i]] for i in range(len(dateR))]
        gpsTimeArr = np.array(gpsT)
        sunPerSV = []
        for i in range(gpsTimeArr.shape[0]):
            days = []
            for m in range(gpsTimeArr.shape[1]):
                days.append(SP3.sun().sunpos(gpsTimeArr[i, m, :], 18).tolist())
            sunPerSV.append(days)
        sunAllSV = []
        for i in range(gpsTimeArr.shape[0]):
            days = []
            for x in sunPerSV[i]:
                for m in range(svnum):
                    days.append(x)
            sunAllSV.append(days)
        sunP = np.array(sunAllSV)
        return sunP


class lla: # lat, lon, alt
    def __init__(self, position, mode):
        # input must be in degrees
        # north and east are positive directions
        # alt is ellipsoidal height
        if type(position) == np.ndarray:
            if len(position.shape) != 2: #check array is 2d e.g shape = (1,3)
                Warning("Wrong number of dimensions, should be 2") 
        if type(position) == list or type(position) == tuple:
            position = np.array([position]) # turn list to 2d array
        if type(position) == np.ndarray:
            if position.ndim != 2: #check array is 2d e.g shape = (1,3)    
                position = position.reshape(3,-1).T
            
        if mode.upper() == "D":
            self.latD = position[:,0]
            self.lonD = position[:,1]
            self.latR = position[:,0] * (np.pi / 180)
            self.lonR = position[:,1] * (np.pi / 180)
            self.altM = position[:,2]
        if mode.upper() == "R":
            self.latR = position[:,0]
            self.lonR = position[:,1]
            self.latD = position[:,0] * (180 / np.pi)
            self.lonD = position[:,1] * (180 / np.pi)
            self.altM = position[:,2]
        if np.abs(self.latD.any()) > 90:
            Warning("Lat outside range of -90 < Lat < 90")
        if np.abs(self.lonD.any()) > 180:
            Warning("Lon outside range of -180 < Lon < 180")
            
        
        if len(position[:,0]) == len(position[:,1]) ==len(position[:,2]):
            self.position = np.array([[self.latR[i], self.lonR[i], self.altM[i]] for i in range(len(self.latR))])

    def __sub__(self, lla2):

        lonDiff = [(self.lonD[i] - lla2.lonD[i]) * 3600 * 30.8667 * math.cos(self.latR[i]) for i in range(len(self.lonD))]
        latDiff = (self.latD - lla2.latD) * 3600 * 30.8667
        altDiff = self.altM - lla2.altM

        return llaDelta([lonDiff, latDiff, altDiff])

    def lla2ecef(self):
        WGS84_A = 6378137.0
        WGS84_f = 1 / 298.257223565
        WGS84_E2 = WGS84_f * (2 - WGS84_f)
        # deg2rad = math.pi / 180.0
        # rad2deg  = 180.0 / math.pi
        lat = self.latR
        lon = self.lonR
        alt = self.altM
        N = [WGS84_A / (math.sqrt(1 - WGS84_E2 * math.sin(lat[i]) * math.sin(lat[i]))) for i in range(len(lat))]
        x = [(N[i] + alt[i]) * math.cos(lat[i]) * math.cos(lon[i]) for i in range(len(lat))]
        y = [(N[i] + alt[i]) * math.cos(lat[i]) * math.sin(lon[i]) for i in range(len(lat))]
        z = [(N[i] * (1 - WGS84_f) * (1 - WGS84_f) + alt[i]) * math.sin(lat[i]) for i in range(len(lat))]
        vel = None
        return ecef([x, y, z], vel)


class llaDelta:
    def __init__(self, distance):
        self.lonM = distance[0]
        self.latM = distance[1]
        self.altM = distance[2]


def enu2ecef(ecef1,penu):
    # Ref:  rtklib_2.4.3\src\rtccmn.c\enu2ecef
    # transform ecef vector to local tangental coordinate
    # I: *pos   geodetic position plla(lat,lon,h) (rad)
    # I: *r     vector in ecef coordinate penu[e,n,u]
    # O: *e     vector in local tangental coordinate {x,y,z}
    npos = ecef1.position.shape
    exyz = np.full(npos,np.nan)
    exyzv = np.zeros(npos)
    for i in range(npos[0]):
        plla = ecef1.ecef2lla()
        #plla = ecef1.ecef2lla_rtklib()
        sinp = math.sin(plla.latR[i])# for j in range(len(plla.latR))]
        cosp = math.cos(plla.latR[i])# for j in range(len(plla.latR))]
        sinl = math.sin(plla.lonR[i])# for j in range(len(plla.latR))]
        cosl = math.cos(plla.lonR[i])# for j in range(len(plla.latR))]
        DCM = np.matrix(np.zeros(shape=(3,3)))
        DCM[0,0] = -sinl
        DCM[0,1] = cosl
        DCM[0,2] = 0
        DCM[1,0] = -sinp*cosl
        DCM[1,1] = -sinp*sinl
        DCM[1,2] = cosp
        DCM[2,0] = cosp*cosl
        DCM[2,1] = cosp *sinl
        DCM[2,2] = sinp
        exyz[i,:] = np.dot(DCM.T,penu[i])
    return ecef(np.array(exyz), exyzv)

# zoee = ecef(
#     np.array([-2710810.9636, 4766114.6131, 3247415.2424]), np.array([0, 0, 0])
# ).ecef2neu(
#     ecef(np.array([-2710810.9636, 4766114.6131, 3247415.2424]), np.array([0, 0, 0]))
# )


# a = np.array([11387.469805, 14541.731163, -20846.735717])
# b = np.array([11315.743620, 14537.170116, -20888.862102])
# c = np.array([2597.430320, 20370.187304, 18948.277092])
# d = np.array([2561.336880, 20423.840749, 18895.443498])
# d1 = (b - a) / 30
# d2 = (d - c) / 30
# # PC11  11387.469805  14541.731163 -20846.735717    229.657568
# # PC14   2597.430320  20370.187304  18948.277092
# # PC11  11315.743620  14537.170116 -20888.862102    229.658255
# # PC14   2561.336880  20423.840749  18895.443498
# posc11 = a
# vocc11 = d1
# posc14 = c
# vocc14 = d2
# posanc11 = np.array([11387.468805, 14541.730163, -20846.734717])
# vocanc11 = d1
# posanc14 = np.array([2597.431320, 20370.188304, 18948.278092])
# vocanc14 = d2
# posanc = np.array([posanc11, posanc14])
# vocanc = np.array([vocanc11, vocanc14])
# pos = np.array([posc11, posc14])
# voc = np.array([vocc11, vocc14])
# rac1 = ecef(posanc, vocanc).ecef2rac(ecef(pos, voc))
# xyz = rac1.rac2ecef(ecef(posanc, vocanc))


# xyzPos = np.array(
#     [
#         [11387.469805, 14541.731163, -20846.735717],
#         [2597.430320, 20370.187304, 18948.277092],
#     ]
# )
# xyzVel = np.array([[2000, 3000, 4000], [2500, 3500, 4500]])
# brdcPos = np.array([[1, 1, 1], [1, 1, 1]])
# brdcVel = np.array([[4, 5, 6], [4, 5, 6]])

# rac1 = ecef(xyzPos, xyzVel).ecef2rac(ecef(brdcPos, brdcVel))
# xyz = rac1.rac2ecef(ecef(brdcPos, brdcVel))

# xyz

# rac = rac(np.array([[3, 2, 1], [1, 2, 3]]), np.array([[2, 2, 2], [4, 5, 6]])).rac2ecef(
#     rac(np.array([[1, 1, 1], [4, 5, 6]]), np.array([[1, 1, 1], [4, 5, 6]]))
# )
