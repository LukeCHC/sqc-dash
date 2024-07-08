# -*- coding: utf-8 -*-
"""
GPS Kepler
Created on Thu May 2 2024
2022Mar29: tk for one number or multiple numbers
@author: Luke
"""

from GNSS import BDS
from datetime import datetime as dt
from Coord import rotation_matrices as rm
from time_transform.time_format import BdsTime, GpsTime

def float2dt(fltt):
    fmt =  '%Y%m%d%H%M%S.0'
    return dt.strptime(str(fltt),fmt)  

from GNSS import GPS
import numpy as np
from datetime import datetime 
from time_transform.time_format import float2dt

class BDSKepler():
    def __init__(self, brdc_arr):
        """
        perform BDS Kepler calculation
        
        brdc_arr: numpy array containing pre matched data
        """
        #= dt(gpsTime), to be calculated, ntag
        if isinstance(brdc_arr, np.ndarray):
            self.brdc_arr = brdc_arr
        
        # geo stationary satellites    
        self.geo_satellites = [1, 2, 3, 4, 5, 59, 60, 61, 62, 63]
        
        # MEO/ IGSO satellites
        self.meo_igso_satellites = [i for i in range(6, 60)]
        
        # split brdc array into satellite groups
        self._split_brdc_array()
        
    def _split_brdc_array(self):
        """Splits the array into 2 separate arrays for GEO and MEO/IGSO satellites"""
        
        brdc_arr = self.brdc_arr
        
        # GEO satellites
        
        geo_mask = np.isin(brdc_arr[:,2], self.geo_satellites)
        meo_mask = np.isin(brdc_arr[:,2], self.meo_igso_satellites)
        
        geo_brdc_arr = brdc_arr[geo_mask]
        meo_brdc_arr = brdc_arr[meo_mask]
        
        self.geo_brdc_arr = geo_brdc_arr
        self.meo_brdc_arr = meo_brdc_arr
        

    def run(self):
        """
        Run the BDS Kepler calculation
        """
        
        x_geo, y_geo, z_geo = self._kepler(self.geo_brdc_arr, 'geo')
        
        process_epochs_geo = self.geo_brdc_arr[:,0]
        system_geo = self.geo_brdc_arr[:,1]
        prn_geo = self.geo_brdc_arr[:,2]
        
        geo_arr = np.array([process_epochs_geo, system_geo, prn_geo, x_geo, y_geo, z_geo]).T
        
        x_meo, y_meo, z_meo = self._kepler(self.meo_brdc_arr, 'meo')
        process_epochs_meo = self.meo_brdc_arr[:,0]
        system_meo = self.meo_brdc_arr[:,1]
        prn_meo = self.meo_brdc_arr[:,2]
        meo_arr = np.array([process_epochs_meo, system_meo, prn_meo, x_meo, y_meo, z_meo]).T
        
        return np.vstack([geo_arr, meo_arr])
        
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

    def _kepler(self, brdc_arr, mode):
        """
        Performs the calculation
        source: https://gssc.esa.int/navipedia/index.php?title=GPS_and_Galileo_Satellite_Coordinates_Computation
        BDS paper : http://en.beidou.gov.cn/SYSTEMS/ICD/201902/P020190227702348791891.pdf
        """

        process_epochs_unix_timestamps = brdc_arr[:,0]
        system = brdc_arr[:,1]
        prn = brdc_arr[:,2]
        
        
        data_observations = brdc_arr[:,3:]
        bias      = data_observations[:,0] # clock bias
        drift     = data_observations[:,1] # clock drift
        driftRate = data_observations[:,2] # clock drift rate
        iode = data_observations[:,3] # issue of data ephemeris (AODE for BDS)
        crs       = data_observations[:,4] # radius correction sinus component
        delta_n    = data_observations[:,5] # radians/sec
        mean_anomaly_0 = data_observations[:,6] #m0 angle radians
        cuc       = data_observations[:,7] # argument of latitude correction cosinus component
        e         = data_observations[:,8] # eccentricity
        cus       = data_observations[:,9] # argument of latitude correction sinus component
        sqrt_a     = data_observations[:,10] # square root of semi-major axis
        toe_sow   = data_observations[:,11] # time of ephemeris reference epoch in second of week
        cic       = data_observations[:,12] # inclination correction cosinus component
        omega_0    = data_observations[:,13] # OMEGA (right ascension of ascending node)
        cis       = data_observations[:,14] # inclination correction sinus component
        i_0        = data_observations[:,15] # initial inclination
        crc       = data_observations[:,16] # radius correction cosinus component
        omega     = data_observations[:,17] # argument of pericenter angle
        omega_dot  = data_observations[:,18] # nodal precession rate
        i_dot      = data_observations[:,19] # inclination rate radians/sec

        epoch_list_dt = [datetime.fromtimestamp(ux_ts) for ux_ts in process_epochs_unix_timestamps]

        epoch_list_bdst = [GpsTime(tt) for tt in epoch_list_dt]

        epoch_list_sow = np.array([tt.GPSSOW for tt in epoch_list_bdst])

        # Time from ephemeris reference epoch
        t_k = epoch_list_sow - toe_sow
        
        n_0 = np.sqrt(BDS.miu) / sqrt_a**3 # computed mean motion radians/sec
        
        n = n_0 + delta_n # corrected mean motion

        mean_anomaly_k = mean_anomaly_0 + (n * t_k)

        # Eccentric Anomaly
        E_k = np.array([self.newton_raphson_kepler(Mk, e) for Mk, e in zip(mean_anomaly_k, e)])

        # True Anomaly
        sin_vk = (np.sqrt(1 - e**2) * np.sin(E_k)) / (1 - e * np.cos(E_k))
        cos_vk = (np.cos(E_k) - e) / (1 - e * np.cos(E_k))
        v_k = np.arctan2(sin_vk, cos_vk)
        
        # argument of latitude
        phi_k = v_k + omega

        delta_uk = cus * np.sin(2 * (phi_k)) + cuc * np.cos(2 * (phi_k)) # argument of latitude correction
        delta_rk = crs * np.sin(2 * (phi_k)) + crc * np.cos(2 * (phi_k)) # radius correction
        delta_ik = cis * np.sin(2 * (phi_k)) + cic * np.cos(2 * (phi_k)) # inclination correction
        
        u_k = phi_k + delta_uk # corrected argument of latitude

        r_k = sqrt_a**2 * (1 - e * np.cos(E_k)) + delta_rk # corrected radius

        i_k = i_0 + (i_dot * t_k) + delta_ik # corrected inclination
        
        x_k = r_k * np.cos(u_k) #Computed satellite positions in orbital plane
        y_k = r_k * np.sin(u_k)
        
        if mode == 'meo':
        
            omega_k = omega_0 + (omega_dot - BDS.rad) * t_k - (BDS.rad * toe_sow) #corrected longitude of ascending node
            
            X_k = x_k * np.cos(omega_k) - y_k * np.cos(i_k) * np.sin(omega_k)
            Y_k = x_k * np.sin(omega_k) + y_k * np.cos(i_k) * np.cos(omega_k)
            Z_k = y_k * np.sin(i_k)

        if mode =='geo':
            
            omega_k = omega_0 + (omega_dot *t_k) - (BDS.rad * toe_sow) #corrected longitude of ascending node
            
            X_gk = x_k * np.cos(omega_k) - y_k * np.cos(i_k) * np.sin(omega_k)
            Y_gk = x_k * np.sin(omega_k) + y_k * np.cos(i_k) * np.cos(omega_k)
            Z_gk = y_k * np.sin(i_k)
            coordinates_gk = np.array([X_gk, Y_gk, Z_gk])
            
            deg5_rad= np.radians(-5)
            Rx = rm.R1([deg5_rad for i in t_k])
            Rz = rm.R3(BDS.rad * t_k)
            
            combined_rotation = Rz @ Rx
            transformed_coordinates = np.einsum('nij,jn->ni', combined_rotation, coordinates_gk)
            
            X_k = transformed_coordinates[:,0]
            Y_k = transformed_coordinates[:,1]
            Z_k = transformed_coordinates[:,2]
            
        return X_k, Y_k, Z_k
            
# to test use findsvbrdc