import streamlit as st
import numpy as np
from datetime import datetime, time, timedelta
from pathlib import Path
import json


from chc_modules import FindSV, FindSvBrdc
from sat_pos_calcs import SatPosCalcs
from display_map_mode import FoliumMap
from station_analysis_mode import StationAnalysisMode

#


class SkyMapDash:
    """Dashboard to display satellite positions"""

    def __init__(self, local_dir = Path(r"F:/skymap_dash/")):
        """
        Initialize the dashboard

        local_dir: Path
            Directory to store the downloaded ephemeris files
        
        """

        self.local_dir = Path(local_dir)
        self._initialise_session_states()
    
    def _initialise_session_states(self):
        """
        Initialise the session states for the dashboard.

        Each state acts as a flag to determine the current state of the dashboard,
        ensuring that all necessary flags are set to their default values if they have not been initialised yet.
        """

        # Dictionary of default values for session states
        default_states = {
            'live_map_mode': True,
            'live_sat_pos': None,
            'live_sat_pos_ecef': None, 
            'orbit_lla_arr': None,
            'selected_mode_idx': 0,
            'azel_mode_idx': None,
            'shanghai': False,
            'guangdong': False,
            'selected_station': None
        }

        # Initialise default values for session states
        for key, value in default_states.items():
            if key not in st.session_state:
                st.session_state[key] = value
        
    def main(self):
        """Main function to run the dashboard"""
                
        # set page config
        st.set_page_config(layout="wide")
        self.reduce_top_whitespace()
        st.title("CHC Sky Map")

        self.display_sidebar_options()

        if st.session_state.live_map_mode:
            self.live_map_mode()

        if st.session_state.station_stats_mode:
            station_mode = StationAnalysisMode(self, session_state=st.session_state)
            station_mode.run()

    def display_sidebar_options(self):
        """Display the sidebar options"""
        
        st.sidebar.title("Options")
        
        # mode selection
        mode_list = ["Live Map", "Station Analysis", "Past Map"]
        selected_mode = st.sidebar.radio("Select Mode", mode_list, index = st.session_state.selected_mode_idx)
        st.session_state.selected_mode_idx = mode_list.index(selected_mode)
        
        # handle mode selection
        if selected_mode == "Live Map":
            self.handle_live_map_mode()
        elif selected_mode == "Station Analysis":
            self.handle_station_analysis_mode()
        elif selected_mode == "Past Map":
            self.handle_past_map_mode()
            
    def handle_live_map_mode(self):
        """Sets flags for live map mode"""
        st.session_state.live_map_mode = True
        st.session_state.past_plot_mode = False
        st.session_state.station_stats_mode = False
        
    def handle_station_analysis_mode(self):
        """Sets the flag to true"""
        st.session_state.station_stats_mode = True
        
            
    def handle_past_map_mode(self):
        # Add any specific functionality for past map mode if necessary
        pass
    
    # def get_live_eph(self):
    #     """
    #     Fetch live ephemeris data from CHC stream
        
    #     saves current positions to session state.sat_pos_lla_arr
    #     saves orbit positions to session state.orbit_lla_arr
        
    #     """
        
    #     SatPosCalcs(self, st.session_state).retrieve_and_process_satellite_data()
            
    def live_map_mode(self):
        
        if st.session_state.selected_mode_idx == 0:
                        
            self.display_home_folium_map()
                
    def display_home_folium_map(self):
        """
        Display the home folium map
        """
        
        map_plot = FoliumMap(self, session_state=st.session_state)
        map_plot.show()

    def find_sv_sp3(self):
        """
        calls find sv, saves file to local directory
        """
        with st.spinner("Downloading SP3"):
            FindSV(self.input_date, 'G', self.local_dir).run()
        st.sidebar.write("Downloaded SP3")

    def find_sv_brdc(self):
        """
        calls find sv brdc, saves file to local directory
        """
        with st.spinner("Downloading SP3"):
            FindSvBrdc(self.input_date, 'G', self.local_dir).run()
            st.sidebar.write("Downloaded BRDC")

    def display_map_past(self):
        """
        Display the past satellite positions, selected date
        """
        
    def reduce_top_whitespace(self):
        # Reducing whitespace on the top of the page
        st.markdown("""
        <style>

        .block-container
        {
            padding-top: 1rem;
            padding-bottom: 0rem;
            margin-top: 1rem;
        }

        </style>
        """, unsafe_allow_html=True)


if __name__ == "__main__":
    
    SkyMapDash().main()