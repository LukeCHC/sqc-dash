# -*- coding: utf-8 -*-
"""
GAL Kepler
Created on Tue May 7 2024
@author: Luke
"""

from GNSS import GPS
from datetime import datetime as dt
from Coord import rotation_matrices as rm
from time_transform.time_format import GalTime

def float2dt(fltt):
    fmt =  '%Y%m%d%H%M%S.0'
    return dt.strptime(str(fltt),fmt)  

from GNSS import GAL
import numpy as np
from datetime import datetime 
from time_transform.time_format import float2dt

class GALKepler():
    def __init__(self, brdc_arr):
        """
        perform GPS Kepler calculation
        
        brdc_arr: numpy array containing pre matched data
        """
        #= dt(gpsTime), to be calculated, ntag
        if isinstance(brdc_arr, np.ndarray):
            self.brdc_arr = brdc_arr

    def run(self):
        """
        Run the GAL Kepler calculation
        """
        x, y, z = self._kepler()

        process_epochs = self.brdc_arr[:,0]
        system = self.brdc_arr[:,1]
        prn = self.brdc_arr[:,2]

        return np.array([process_epochs, system, prn, x, y, z]).T
        
    def newton_raphson_kepler(self, Mk, e, tolerance=1e-6, max_iterations=1000):
        """
        Solve the Kepler equation for the eccentric anomaly.

        Parameters:
        - Mk : float
            Mean anomaly in radians.
        - e : float
            Eccentricity of the orbit.
        - tolerance : float, optional
            The acceptable error between successive iterations (default is 1e-6).
        - max_iterations : int, optional
            Maximum number of iterations to perform (default is 1000).

        Returns:
        - Ek : float
            Eccentric anomaly in radians.
        """
        if Mk < 0 or Mk > 2 * np.pi:
            Mk = np.mod(Mk, 2 * np.pi)  # Normalize Mk to be within 0 and 2*pi
        
        # Initial guess for E_k can be Mk itself
        Ek = Mk

        for _ in range(max_iterations):
            Ek_next = Ek - (Ek - e * np.sin(Ek) - Mk) / (1 - e * np.cos(Ek))
            if abs(Ek_next - Ek) < tolerance:
                return Ek_next
            Ek = Ek_next

        raise RuntimeError(f"Solution did not converge after {max_iterations} iterations.")

    def _kepler(self):
        """
        Performs the calculation
        source: https://gssc.esa.int/navipedia/index.php?title=GPS_and_Galileo_Satellite_Coordinates_Computation
        """

        brdc_arr = self.brdc_arr

        process_epochs_unix_timestamps = brdc_arr[:,0]
        system = brdc_arr[:,1]
        prn = brdc_arr[:,2]

        data_observations = brdc_arr[:,3:]
        bias      = data_observations[:,0]
        drift     = data_observations[:,1]
        driftRate = data_observations[:,2]
        iode = data_observations[:,3]
        crs       = data_observations[:,4]
        delta_n    = data_observations[:,5]
        mean_anomaly_0 = data_observations[:,6]
        cuc       = data_observations[:,7]
        e         = data_observations[:,8]
        cus       = data_observations[:,9]
        sqrt_a     = data_observations[:,10]
        toe_sow   = data_observations[:,11]
        cic       = data_observations[:,12]
        omega_0    = data_observations[:,13]
        cis       = data_observations[:,14]
        i_0        = data_observations[:,15]
        crc       = data_observations[:,16]
        omega     = data_observations[:,17]
        omega_dot  = data_observations[:,18]
        i_dot      = data_observations[:,19]

        epoch_dt = [datetime.fromtimestamp(ux_ts) for ux_ts in process_epochs_unix_timestamps]

        epoch_gpst = [GalTime(tt) for tt in epoch_dt]

        epoch_sow = np.array([tt.GALSOW for tt in epoch_gpst])

        # Time from ephemeris reference epoch
        t_k = epoch_sow - toe_sow

        mean_anomaly_k = mean_anomaly_0 + (np.sqrt(GPS.miu)/ sqrt_a**3 + delta_n) * t_k

        # Eccentric Anomaly
        # E_k = mean_anomaly_tk + e * np.sin(mean_anomaly_tk)
        E_k = np.array([self.newton_raphson_kepler(Mk, e) for Mk, e in zip(mean_anomaly_k, e)])

        # True Anomaly
        v_k = np.arctan2(np.sqrt(1-e**2) * np.sin(E_k), np.cos(E_k) - e)

        # Argument of Latitude
        u_k = v_k + omega + cus * np.sin(2*(omega + v_k)) + cuc * np.cos(2*(omega + v_k))

        # radial distance
        r_k = sqrt_a**2 * (1 - e * np.cos(E_k)) + crc * np.cos(2*(omega + v_k)) + crs * np.sin(2*(omega + v_k))

        # inclination
        i_k = i_0 + i_dot * t_k + cic * np.cos(2*(omega + v_k)) + cis * np.sin(2*(omega + v_k))

        # longtude of the ascending node
        lambda_k = omega_0 + (omega_dot - GPS.rad) * t_k - (GPS.rad * toe_sow)

        zero_vec = np.zeros(len(r_k))

        rk_vector = np.array([r_k, zero_vec, zero_vec])

        rk_vector = rk_vector.T[:, :, np.newaxis]  # Final shape (n, 3, 1)

        R3_lambda_k = rm.R3(-lambda_k)
        R1_i_k = rm.R1(-i_k)
        R3_u_k = rm.R3(-u_k)

        R = R3_lambda_k @ R1_i_k @ R3_u_k

        result = (R @ rk_vector).squeeze()

        x_k, y_k, z_k = result.T

        return x_k, y_k, z_k

    