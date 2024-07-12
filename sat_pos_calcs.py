import streamlit as st
from datetime import datetime, timedelta
import numpy as np
import pandas as pd

from GNSS import GPSKepler
from Coord import ECEF, LLA
from download_live_eph import DownloadAndDecodeChcEph
from eph_decode_formatter import eph_attributes_to_arr

from chc_modules.find_sv_brdc import FindSvBrdc

class SatPosCalcs:
    """
    This class handles all calculations of sat positions for the skymap dashboard
    Also handles fetching eph data
    """
    
    def __init__(self, SkyMapDash, session_state):
        """self inherited from SkyMapDash"""

        self.local_dir = SkyMapDash.local_dir
        self.SkyMapDash = SkyMapDash
        st.session_state = session_state
    
    def retrieve_and_process_satellite_data(self, mode = 'Whole Day'):
        # with st.sidebar:
        with st.spinner("Getting Live Broadcast Ephemeris..."):
            single_epoch_gps_brdc_eph = self.get_live_eph()
    
            self.process_satellite_positions(single_epoch_gps_brdc_eph, mode)
            
    def retrieve_and_process_satellite_data_past(self, mode = 'Whole Day'):
        with st.spinner("Fetching BRDC from NASA CDDIS..."):
            
            process_datetime = datetime.combine(self.SkyMapDash.date, self.SkyMapDash.time)
            sv_pos_xyz_arr = FindSvBrdc(process_datetime, 'G', self.local_dir).run()
            
            
            # prepare arr shapes
            epoch = sv_pos_xyz_arr[:,0].reshape(-1,1)
            prn = sv_pos_xyz_arr[:,2].reshape(-1,1)

            # convert from xyz to lla
            sat_pos_ecef = ECEF(sv_pos_xyz_arr[:,3:])
            sat_pos_lla = sat_pos_ecef.ecef2lla()
            
            orbit_lla_arr = np.hstack([epoch, prn, sat_pos_lla.lat_d, sat_pos_lla.lon_d, sat_pos_lla.alt_m])
            
            
            matching_time_pos = orbit_lla_arr[orbit_lla_arr[:,0] == int(process_datetime.timestamp())]
        
            st.session_state.live_sat_pos = matching_time_pos
            st.session_state.orbit_lla_arr = orbit_lla_arr
                
    def process_satellite_positions(self, single_epoch_gps_brdc_eph, extrapolation_mode):
        """Calculate satellite orbit using 1 epochs brdc data"""
        
        # broadcast array to other epochs
        current_timestamp = int(single_epoch_gps_brdc_eph[0,0])
        current_dt =  datetime.fromtimestamp(current_timestamp)
        
        st.write(f"Current datetime: {current_dt:%Y-%m-%d %H:%M:%S}")
        
        if extrapolation_mode == 'Whole Day':
            
            # create datetime range for each 5 minutes in day
            five_min_epoch_list= [current_dt.replace(hour=i, minute=j) for i in range(24) for j in range(0,60,5)]
            middle_idx = len(five_min_epoch_list)//2
            current_dt = five_min_epoch_list[middle_idx]
        
            extrapolated_eph_arr = np.empty((0,single_epoch_gps_brdc_eph.shape[1]))
            for i in range(len(five_min_epoch_list)):
                new_arr = single_epoch_gps_brdc_eph.copy()
                new_arr[:,0] = five_min_epoch_list[i].timestamp()
                extrapolated_eph_arr = np.vstack([extrapolated_eph_arr, new_arr])
                
        else:
            
            # extrapolate ephemeris for 2 hours to calculate orbits
            hourly_dt = [current_dt + timedelta(minutes=i) for i in range(-60, 60, 5)]
            extrapolated_eph_arr = np.empty((0,single_epoch_gps_brdc_eph.shape[1]))
            for i in range(len(hourly_dt)):
                new_arr = single_epoch_gps_brdc_eph.copy()
                new_arr[:,0] = hourly_dt[i].timestamp()
                extrapolated_eph_arr = np.vstack([extrapolated_eph_arr, new_arr])
                
        self.calculate_satellite_positions(extrapolated_eph_arr, current_dt)
            
    def calculate_satellite_positions(self, extrapolated_eph_arr, current_dt):
        """
        Calls kepler function on brdc array
        Generates orbit array and current sat pos array
        save both to session state
        """
        # calcualte xyz via kepler model
        gps_kepler = GPSKepler(extrapolated_eph_arr)
        sv_pos_xyz = gps_kepler.run()
        
        # prepare arr shapes
        epoch = sv_pos_xyz[:,0].reshape(-1,1)
        prn = sv_pos_xyz[:,2].reshape(-1,1)

        # convert from xyz to lla
        sat_pos_ecef = ECEF(sv_pos_xyz[:,3:])
        sat_pos_lla = sat_pos_ecef.ecef2lla()
        
        orbit_lla_arr = np.hstack([epoch, prn, sat_pos_lla.lat_d, sat_pos_lla.lon_d, sat_pos_lla.alt_m])
        
        # get current satellite positions
        sat_pos_lla_arr = orbit_lla_arr[orbit_lla_arr[:,0] == int(current_dt.timestamp())]
    
        # get current satellite positions ecef
        sat_pos_ecef = LLA(sat_pos_lla_arr[:,2:], 'd').lla2ecef().position
    
        st.session_state.live_sat_pos_ecef = sat_pos_ecef
        st.session_state.live_sat_pos = sat_pos_lla_arr
        st.session_state.orbit_lla_arr = orbit_lla_arr
        
    def get_live_eph(self):
        """Connects to stream (Currently ROCG) and downloads live broadcast ephemeris (EPH)"""
        
        EPHIP = '18.170.8.65'
        EPHPORT = 10011

        decoded_data = DownloadAndDecodeChcEph(EPHIP, EPHPORT).run()

        gps_eph_data = decoded_data[1].ephgps

        single_epoch_gps_eph_arr = eph_attributes_to_arr(gps_eph_data)
        
        return single_epoch_gps_eph_arr
    
    def calculate_fullday_azel(self):
        """Uses the calculated orbit array to calculate azel for entire day"""
        
        orbit_lla_arr = st.session_state.orbit_lla_arr
        
        ground_pos = st.session_state.ground_pos
        
        ground_pos = ECEF(ground_pos.position)
        print(f"orbit {orbit_lla_arr.shape}")
        orbit_lla_obj = LLA(orbit_lla_arr[:,2:], 'd')
        
        orbit_azel = ground_pos.calculate_azel(orbit_lla_obj)
               
        return np.hstack([orbit_lla_arr, orbit_azel])
    
    def find_elevation_crossings(self, prn_df, threshold=15):
        """Find the times when the elevation crosses a threshold level, single prn"""
        
        # Identify where the elevation crosses the threshold
        above = prn_df['el'] >= threshold
        # Find transitions
        transition_points = above != above.shift()
        transition_points.iloc[0] = False  # Ignore the first point
        
        # Separate entering and leaving points
        entering_sight = prn_df.loc[transition_points & above, 'epoch']
        leaving_sight = prn_df.loc[transition_points & ~above, 'epoch']
        
        # If the group starts above the threshold, there's no entering point at the start
        if above.iloc[0]:
            entering_sight = pd.concat([pd.Series([prn_df['epoch'].iloc[0]]), entering_sight])

        # If the group ends above the threshold, there's no leaving point at the end
        if above.iloc[-1]:
            leaving_sight = pd.concat([leaving_sight, pd.Series([prn_df['epoch'].iloc[-1]])])

        # Return as DataFrame
        return pd.DataFrame({
            'entering_epoch': entering_sight.reset_index(drop=True),
            'leaving_epoch': leaving_sight.reset_index(drop=True)
        })