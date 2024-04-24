import streamlit as st
from pathlib import Path
import numpy as np
from datetime import datetime, time, timedelta
import json

from GNSS import GPSKepler
from Coord import ECEF
from chc_modules import FindSV, FindSvBrdc
from download_live_eph import DownloadAndDecodeChcEph
from eph_decode_formatter import eph_attributes_to_arr

from display_map import SkyMapMap
from display_azel import SkyMapAzEl

class SkyMapDash:
    """Dashboard to display satellite positions"""

    def __init__(self, local_dir = Path(r"F:/skymap_dash/")):
        """
        Initialize the dashboard

        local_dir: Path
            Directory to store the downloaded ephemeris files
        
        """

        self.local_dir = Path(local_dir)
        
    def main(self):
        """Main function to run the dashboard"""
                
        st.set_page_config(layout="wide")

        st.title("SkyMap Dashboard")

        self._initialise_session_states()

        self.display_sidebar_options()

        if st.session_state.plot_persist:
            if st.session_state.selected_date:
                if st.session_state.selected_datetime:
                    map_plot = SkyMapMap(self, session_state = st.session_state)
                    map_plot.show_past_data()

        if st.session_state.show_live:
            map_plot = SkyMapMap(self, session_state=st.session_state)
            map_plot.show_live_data()

        if st.session_state.show_azel:
            azel_plot = SkyMapAzEl(self, session_state=st.session_state)
            azel_plot.show_past_azel()

    def _initialise_session_states(self):
        """
        Initialise the session states
        
        Each state acts as a flag to determine the current state of the dashboard
        """

        # display past data map
        if 'plot_persist' not in st.session_state:
            st.session_state.plot_persist = False

        # display show plot button
        if 'plot_ready' not in st.session_state:
            st.session_state.plot_ready = False

        # checks if input date is selected
        if 'selected_date' not in st.session_state:
            st.session_state.selected_date = False

        # checks if input time is selected
        if 'selected_datetime' not in st.session_state:
            st.session_state.selected_datetime = False

        # checks if using sp3 or brdc data
        if 'mode' not in st.session_state:
            st.session_state.mode = False

        # display azel sky plots
        if 'show_azel' not in st.session_state:
            st.session_state.show_azel = False

        # display live data
        if 'show_live' not in st.session_state:
            st.session_state.show_live = False

        if 'selected_station' not in st.session_state:
            st.session_state.selected_station = False

    def display_sidebar_options(self):
        """Display the sidebar options"""

        st.sidebar.title("Options")

        test_date = datetime(2024,4,1,0,0,0)

        # date input
        selected_date = st.sidebar.date_input("Select a date", value=test_date)
        st.session_state.selected_date = selected_date

        year = selected_date.year
        month = selected_date.month
        day = selected_date.day
        doy = selected_date.timetuple().tm_yday
        self.input_date = datetime(year, month, day)

        # file paths 
        self.sp3_npy_path = self.local_dir/ "sv_pos_npy" / f"sv_pos_sp3_{year}_{doy:03d}_G.npy"
        self.brdc_npy_path = self.local_dir/ f"sv_pos_brdc_{year}_{doy:03d}_G.npy"

        # do not display plot button
        st.session_state.plot_ready = False


        # station select

        stations = json.load(open("stn_list.json")).keys()
        selected_station = st.sidebar.selectbox("Select Station", stations, index = None)
        st.session_state.selected_station = selected_station

        if selected_station is not None:
            ground_pos_dict = json.load(open("stn_list.json"))[selected_station]
            lat = ground_pos_dict['Lat']
            lon = ground_pos_dict['Lon']
            self.ground_pos = (lat, lon, 0)

        if not self.brdc_npy_path.exists():
            st.sidebar.button("Download BRDC", on_click = self.find_sv_brdc)
        else:
            st.sidebar.write("BRDC file exists for this day")
            st.session_state.plot_ready = True
            st.session_state.mode = 'brdc'

        if not self.sp3_npy_path.exists():
            st.sidebar.button("Download SP3", on_click = self.find_sv_sp3)
        else: 
            st.sidebar.write("SP3 file exists for this day")
            st.session_state.mode = 'sp3'
            if not st.session_state.plot_ready:
                st.session_state.plot_ready = True

        if st.session_state.plot_ready:
            if st.sidebar.button("Show Map") or st.session_state.plot_persist:
                st.session_state.selected_datetime = datetime.combine(selected_date, time(0, 0))
                st.session_state.show_azel = False
                st.session_state.plot_persist = True

            if st.sidebar.button("Show Azel"):
                st.session_state.plot_persist = False
                st.session_state.show_azel = True

        if st.sidebar.button("Live Tracker"):
            st.session_state.plot_persist = False
            st.session_state.show_azel = False
            st.session_state.show_live = True

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
        

if __name__ == "__main__":
    
    SkyMapDash().main()