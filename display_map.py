import plotly.graph_objects as go
import streamlit as st
from datetime import datetime, time, timedelta
import numpy as np

from Coord import ECEF
from download_live_eph import DownloadAndDecodeChcEph
from GNSS import GPSKepler
from eph_decode_formatter import eph_attributes_to_arr

class SkyMapMap:
    """Handles the map plotting for SkyMapDash"""
    def __init__(self, SkyMapDash, session_state):
        """self inherited from SkyMapDash"""

        # self.mode = SkyMapDash.mode
        self.local_dir = SkyMapDash.local_dir
        st.session_state = session_state
        self.sp3_npy_path = SkyMapDash.sp3_npy_path
        self.brdc_npy_path = SkyMapDash.brdc_npy_path

        if st.session_state.selected_station:
            self.ground_pos = SkyMapDash.ground_pos

    def show_live_data(self):
        """Show live data on the map"""

        with st.spinner("Preparing live data..."):

            fig = self.prepare_map_fig()
        
            fullday_data_arr_lla = self.get_live_data()

        unique_prn = np.unique(fullday_data_arr_lla[:,1])        

        for prn in unique_prn:
            fullday_prn_arr = fullday_data_arr_lla[fullday_data_arr_lla[:,1] == prn]
            
            single_epoch_prn_arr = fullday_prn_arr[-1,:].reshape(-1,4)

            # fig = self.plot_sv_orbit(fig, fullday_prn_arr) 

            fig = self.plot_sv_position(fig, single_epoch_prn_arr)


        if st.session_state.selected_station:
            fig = self.plot_station(fig)

        st.plotly_chart(fig, use_container_width=True)


    def show_past_data(self):
        """Show past data on the map"""
        
        fig = self.prepare_map_fig()

        second_of_day = self.prepare_date_time_selection()

        fullday_data_arr_lla = self.load_lla_data()

        unique_prn = np.unique(fullday_data_arr_lla[:,1])


        for prn in unique_prn:
            fullday_prn_arr = fullday_data_arr_lla[fullday_data_arr_lla[:,1] == prn]
            
            single_epoch_prn_arr = fullday_prn_arr[np.abs(fullday_prn_arr[:,0] - second_of_day) < 30]

            # fig = self.plot_sv_orbit(fig, fullday_prn_arr) 

            fig = self.plot_sv_position(fig, single_epoch_prn_arr)

            if st.session_state.selected_station:
                fig = self.plot_station(fig)

        fig.update_layout(
            # width=2000,
            height=720,
            autosize = True
        )

        st.plotly_chart(fig, use_container_width=False)

    def plot_sv_orbit(self, fig, fullday_prn_arr):
        """Adds the orbit trace for a single satellite"""

        sample_indices = np.linspace(0, len(fullday_prn_arr) - 1, num=25, dtype=int)

        epoch_list = fullday_prn_arr[:,0][sample_indices]
        prn = fullday_prn_arr[:,1][sample_indices]
        lat = fullday_prn_arr[:,2][sample_indices]
        lon = fullday_prn_arr[:,3][sample_indices]

        prn_code = [f"G{int(i):02d}" for i in prn]

        fig.add_trace(go.Scattergeo(
                lon = lon,
                lat = lat,
                text=[f"{prn_code[i]} {epoch_list[i]}" for i in range(len(epoch_list))],
                mode = 'lines',
                line = dict(width = 2, color = 'blue'),
            ))
        
        return fig

    def plot_sv_position(self, fig, single_epoch_prn_arr):
        """plots the satellite position for a single epoch"""
        
        epoch = single_epoch_prn_arr[:,0]
        prn = single_epoch_prn_arr[:,1]
        lat = single_epoch_prn_arr[:,2]
        lon = single_epoch_prn_arr[:,3]

        prn_code = f"G{int(prn):02d}" 

        fig.add_trace(go.Scattergeo(
            lat = lat,
            lon = lon,
            text=[f"{prn_code}"],
            mode='markers+text',
            textposition='top right',
            textfont=dict(
            family="Roboto-bold",
            size=16,
            color="black"  # Set text color to black
                ),
            marker = dict(
                size = 10,
                symbol = 'x',
                color = 'red',
                line = dict(
                    width = 3,
                    color = 'rgba(68, 68, 68, 0)'
                )
            )
        ))

        return fig

    def load_lla_data(self):

        """
        Load the xyz data from the numpy file.
        """
        if st.session_state.mode == 'sp3':
            sat_pos_xyz = np.load(self.sp3_npy_path)
        else:
            sat_pos_xyz = np.load(self.brdc_npy_path)

        epoch = sat_pos_xyz[:,0].reshape(-1,1)
        prn = sat_pos_xyz[:,2].reshape(-1,1)

        sat_pos_xyz = ECEF(sat_pos_xyz[:,-3:])
        sat_pos_lla = sat_pos_xyz.ecef2lla()
        full_arr = np.hstack([epoch, prn, sat_pos_lla.lat_d, sat_pos_lla.lon_d])
        return full_arr

    def plot_station(self, fig):
        ground_lat, ground_lon, zero = self.ground_pos
        elevation_mask_deg = 15

        # Angular radius in degrees from the horizon to the limit of the visible sky
        angular_radius_deg = 90 - elevation_mask_deg

        # Number of points to define the perimeter of the circle
        num_points = 10
        lats = [ground_lat + angular_radius_deg * np.cos(np.radians(angle)) for angle in np.linspace(0, 360, num_points)]
        lons = [ground_lon + angular_radius_deg * np.sin(np.radians(angle)) / np.cos(np.radians(ground_lat)) for angle in np.linspace(0, 360, num_points)]

        # Add station marker
        fig.add_trace(go.Scattergeo(
            lon = [ground_lon],
            lat = [ground_lat],
            text = f"{st.session_state.selected_station}",
            mode = 'markers+text',
            textposition='top right',
            textfont=dict(
                family="Roboto",
                size=16,
                color="black"  # Set text color to black
                    ),
            marker = dict(
                size = 25,
                symbol = 'star',
                color = 'gold',
                line = dict(
                    width = 3,
                    color = 'rgba(68, 68, 68, 0)'
                )
            )
        ))

        # Add the FoV circle to the plot
        fig.add_trace(go.Scattergeo(
            lon = lons,
            lat = lats,
            mode = 'lines',
            line = dict(width = 2, color = 'brown'),
        ))

        #set plot to station
        fig.update_geos(
            projection_rotation = dict(lat = ground_lat, lon = ground_lon))
    

        return fig


    def plot_station_(self, fig):


        ground_lat, ground_lon, zero = self.ground_pos 

        elevation_mask_deg = 10
        theta_rad = np.radians(elevation_mask_deg)
        # Calculate the angular radius of the visible sky
        angular_radius_rad = np.radians(90) - theta_rad
        # Calculate the area of the spherical cap
        visible_sky_area = 2 * np.pi * (1 - np.cos(angular_radius_rad))

        angular_radius_deg = self.steradians_to_degrees(visible_sky_area)


        num_points = 36
        lats = [ground_lat + np.cos(np.radians(angle)) * angular_radius_deg for angle in np.linspace(0, 360, num_points)]
        lons = [ground_lon + np.sin(np.radians(angle)) * angular_radius_deg / np.cos(np.radians(ground_lat)) for angle in np.linspace(0, 360, num_points)]

        # add station
        fig.add_trace(go.Scattergeo(
            lon = [ground_lon],
            lat = [ground_lat],
            text = f"{st.session_state.selected_station}",
            mode = 'markers',
            marker = dict(
                size = 25,
                symbol = 'star',
                color = 'gold',
                line = dict(
                    width = 3,
                    color = 'rgba(68, 68, 68, 0)'
                )
            )
        )
        )

        # Add the FoV circle to the plot
        fig.add_trace(go.Scattergeo(
            lon = lons,
            lat = lats,
            mode = 'lines',
            line = dict(width = 2, color = 'brown'),
        ))

        return fig

    def prepare_date_time_selection(self):
        
        if 'selected_datetime' not in st.session_state:
            selected_datetime = datetime.combine(st.session_state.selected_date, time(0, 0))
            st.session_state['selected_datetime'] = selected_datetime
        
        selected_datetime = st.slider(
            "Select a time",
            value=st.session_state['selected_datetime'],
            min_value=datetime.combine(st.session_state.selected_date, time(0, 0)),
            max_value=datetime.combine(st.session_state.selected_date, time(23, 59)),
            format="HH:mm",
            step=timedelta(minutes=1)
    )

        st.session_state['selected_datetime'] = selected_datetime
        second_of_day = (selected_datetime.hour * 3600 +
                        selected_datetime.minute * 60 +
                        selected_datetime.second)
        
        return second_of_day

    def prepare_map_fig(self):
        fig = go.Figure()
        fig.update_geos(
            projection_type="satellite",
            projection_scale=0.9
            )

        fig.update_layout(
            title = 'Satellite Positions',
            geo_scope='world',
            showlegend = False
        )

        fig.update_geos(
            resolution=50,
            showcoastlines=True, coastlinecolor="RebeccaPurple",
            showland=True, landcolor="LightGreen",
            showocean=True, oceancolor="LightBlue",
            showlakes=True, lakecolor="Blue",
            showrivers=True, rivercolor="Blue"
        )

        return fig
    
    def get_live_data(self):
        EPHIP = '18.170.8.65'
        EPHPORT = 10011

        decoded_data = DownloadAndDecodeChcEph(EPHIP, EPHPORT).run()

        gps_eph_data = decoded_data[1].ephgps

        gps_eph_arr = eph_attributes_to_arr(gps_eph_data)
        
        gps_kepler = GPSKepler(gps_eph_arr)
        sv_pos_xyz = gps_kepler.run()

        epoch = sv_pos_xyz[:,0].reshape(-1,1)
        prn = sv_pos_xyz[:,2].reshape(-1,1)

        sat_pos_ecef = ECEF(sv_pos_xyz[:,3:])
        sat_pos_lla = sat_pos_ecef.ecef2lla()
        sat_pos_lla_arr = np.hstack([epoch, prn, sat_pos_lla.lat_d, sat_pos_lla.lon_d])

        return sat_pos_lla_arr

    def steradians_to_degrees(self, area):
        """Convert an area in steradians to an angular radius in degrees."""
        return np.degrees(np.arccos(1 - area / (2 * np.pi)))