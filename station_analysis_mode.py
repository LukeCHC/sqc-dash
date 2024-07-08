import plotly.graph_objects as go
import plotly.express as px
import streamlit as st
from datetime import datetime, time
import numpy as np
from matplotlib import pyplot as plt
import pandas as pd
import json

from Coord import ECEF
from download_live_eph import DownloadAndDecodeChcEph
from GNSS import GPSKepler
from eph_decode_formatter import eph_attributes_to_arr
from Coord import LLA
from sat_pos_calcs import SatPosCalcs

class StationAnalysisMode:
    def __init__(self, SkyMapDash, session_state):
        """self inherited from SkyMapDash"""

        self.local_dir = SkyMapDash.local_dir
        st.session_state = session_state


    def run(self):
        """Run the station analysis page of the skymap dash"""
        
        self.select_station()
        
        if st.session_state.selected_station is not None:
        
            st.title(st.session_state.selected_station, "Analysis")
            
            self.display_station_info()
            
            self.select_station_azel_data_mode()
            
            if (st.session_state.azel_mode_idx == 0):
                if st.sidebar.button("Get Live Station Stats"):
                    self.show_live_azel_components()
                
            elif st.session_state.azel_mode_idx == 1:
                self.show_past_azel()
                
        else:
            st.write("Please select a station in the sidebar")
                
    def select_station(self):
        """Select station, get ground position"""
        try:
            stations_json = json.load(open("misc/stn_list.json"))
            stations = list(stations_json.keys())
            selected_station = st.sidebar.selectbox("Select Station", stations, None)
            station_values = stations_json[selected_station]
            ground_pos = LLA((station_values['Lat'], station_values['Lon'], 0))
            st.session_state.selected_station = selected_station
            st.session_state.ground_pos = ground_pos
        except:
            return None
            
    def select_station_azel_data_mode(self):
        """Select between viewing live or past AzEl data"""
        station_mode_list = ["Live Stats", "Past Stats"]
        station_mode = st.sidebar.radio("Select Station Analysis Mode", station_mode_list)
        st.session_state.azel_mode_idx = station_mode_list.index(station_mode)
    
    def display_station_info(self):
        """Display the station position"""
        
        ground_pos = st.session_state.ground_pos
        
        col1, col2, col3, col4, col5 = st.columns(5)
        col1.metric("Latitude", np.round(ground_pos.lat_d,2))
        col2.metric("Longitude", np.round(ground_pos.lon_d,2))
        col3.metric("Altitude", np.round(ground_pos.alt_m,2))
        col4.metric("Score", 'Haha')
        col5.metric("Status", 'lol')
                
        ground_pos_df = pd.DataFrame({
            'LAT': [ground_pos.lat_d.item()], 
            'LON': [ground_pos.lon_d.item()], 
            'ALT': [ground_pos.alt_m.item()]
        })
        
        st.map(ground_pos_df, size = 5, zoom = 4)
        
    def show_live_azel_components(self):
        """Show the live AzEl plots, tables and such"""
        
        
        self.fetch_live_eph()
        
        self.display_dop_info()

        with st.spinner("Loading AzEl data..."):
            
            sat_pos_lla_arr = st.session_state.live_sat_pos
            
            sat_pos_lla_obj = LLA(sat_pos_lla_arr[:,2:], 'd') 
            
            ground_pos = ECEF(st.session_state.ground_pos.position)
            
            sat_pos_azel = ground_pos.calculate_azel(sat_pos_lla_obj)
            
            sat_pos_azel = np.hstack([sat_pos_lla_arr, sat_pos_azel])
            
            # self.show_visbile_satellites_table(sat_pos_azel)
            
            self.generate_static_azel_plot(sat_pos_azel)
            
        fullday_orbit_azel_arr = self.calculate_fullday_azel()
            
        self.show_satellite_availability_over_time(fullday_orbit_azel_arr)
        
        self.show_gantt_chart(fullday_orbit_azel_arr)
            
    def display_dop_info(self):
        """Calculates and displays dop information"""
        
        sat_pos_ecef = st.session_state.live_sat_pos_ecef
        
        ground_pos_ecef = LLA(st.session_state.ground_pos.position).lla2ecef().position
        
        gdop, pdop, hdop, vdop = self.calculate_dop(sat_pos_ecef, ground_pos_ecef)
        
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("GDOP", np.round(gdop,2))
        col2.metric("PDOP", np.round(pdop,2))
        col3.metric("HDOP", np.round(hdop,2))
        col4.metric("VDOP", np.round(vdop,2))
        
        with st.expander("About DOP Values :satellite: :chart_with_upwards_trend:"):
            st.write('''
            ##### Geometric Dilution of Precision (GDOP)

            - **Represents**: The overall impact of satellite geometry on position and time accuracy.
            - **Good Value**: Below 2 is excellent; 2-5 is good.

            ##### Position Dilution of Precision (PDOP)

            - **Represents**: The effect on 3D positional accuracy (latitude, longitude, and altitude).
            - **Good Value**: Below 3 is considered good.

            ##### Horizontal Dilution of Precision (HDOP)

            - **Represents**: The impact on horizontal position accuracy (latitude and longitude).
            - **Good Value**: Below 2 is very good.

            ##### Vertical Dilution of Precision (VDOP)

            - **Represents**: The effect on vertical position accuracy (altitude).
            - **Good Value**: Below 2 is considered good.

            ##### Time Dilution of Precision (TDOP)

            - **Represents**: The impact on the accuracy of time measurement.
            - **Good Value**: Below 1 is ideal.
            ''')
        
    def calculate_dop(self, sat_positions, receiver_position):
        """
        Calculate DOP values from satellite positions and receiver position.
        :param sat_positions: List of satellite ECEF positions [x, y, z].
        :param receiver_position: Receiver's ECEF position [x, y, z].
        :return: Dictionary containing GDOP, PDOP, HDOP, VDOP values.
        """
        
        # Compute line-of-sight vectors from the receiver to each satellite
        los_vectors = sat_positions - receiver_position
        
        # Compute distances to each satellite
        distances = np.linalg.norm(los_vectors, axis=1)
        
        # Normalize line-of-sight vectors
        H = np.hstack((los_vectors / distances[:, np.newaxis], np.ones((len(los_vectors), 1))))
        
        # Compute the covariance matrix
        HtH_inv = np.linalg.inv(np.dot(H.T, H))
        
        # Calculate DOP values
        GDOP = np.sqrt(np.trace(HtH_inv))
        PDOP = np.sqrt(np.sum(np.diag(HtH_inv)[:3]))
        HDOP = np.sqrt(np.sum(np.diag(HtH_inv)[:2]))
        VDOP = np.sqrt(HtH_inv[2, 2])
        
        return GDOP, PDOP, HDOP, VDOP
        
            
    def generate_static_azel_plot(self, sat_pos_azel):
        
        fig = go.Figure()
        
        unique_sats = np.unique(sat_pos_azel[:, 1])
        
        for prn in unique_sats:
            prn_arr = sat_pos_azel[sat_pos_azel[:, 1] == prn]
            
            trace = go.Scatterpolar(
                r=prn_arr[:, -1],
                theta=prn_arr[:, -2],
                mode='markers+text',
                text = f'G{int(prn):02d}',
                textposition='top right',
                textfont=dict(
                family="Roboto-bold",
                size=16,
                color="black"  # Set text color to black
                    ),
                name=f'G{int(prn):02d}',
                marker=dict(symbol='circle')
            )
            
            fig.add_trace(trace)
            
        # add horizon circle
        fig.add_trace(go.Scatterpolar(
            r = [15]*360,
            theta = np.arange(0, 360),
            mode = 'lines',
            line = dict(color='black', width=1),
            name='Horizon'
        ))
            
            
        fig.update_layout(
            showlegend=False,
            polar=dict(
                radialaxis=dict(visible=True, range=[90, 15]),
                angularaxis=dict(direction='clockwise')
            ),
            title="Satellite Visibility",
            legend_title="Satellite PRN",
            width = 1600,
            height = 700,
            template='plotly'
        )
        
        st.plotly_chart(fig, use_container_width=True)

            

    def show_past_azel(self):
        """Show the past AzEl plot"""

        with st.spinner("Loading AzEl data..."):
            
            second_of_day = self.prepare_date_time_selection()

            fullday_data_arr_azel = self.load_azel_data()

        self.generate_azel_plot(fullday_data_arr_azel)

    def generate_azel_plot(self, fullday_data_arr_azel):
    
        fig = go.Figure()

        unique_sats = np.unique(fullday_data_arr_azel[:, 2])
        unique_epochs = np.unique(fullday_data_arr_azel[:, 0])

        frames = []
        for epoch in unique_epochs[::20]:
            frame_traces = self.generate_azel_frame(epoch, unique_sats, fullday_data_arr_azel)
            frames.append(go.Frame(data=frame_traces, name=str(epoch)))

        # Set up the initial state of the figure with the first epoch's data
        fig.add_traces(frames[0].data)

        fig = self.generate_play_pause_buttons(fig, frames, unique_epochs)

        fig.frames = frames

        fig.update_layout(
            showlegend=False,
            width = 1600,
            height = 700
        )
        st.plotly_chart(fig, use_container_width=True)

        self.show_availability_table()


    def generate_play_pause_buttons(self, fig, frames, unique_epochs):
        # Play and pause buttons
        updatemenus = [
            {
                "buttons": [
                    {
                        "args": [None, {"frame": {"duration": 10, "redraw": True}, "fromcurrent": True, "transition": {"duration": 10, "easing": "quadratic-in-out"}}],
                        "label": "Play",
                        "method": "animate"
                    },
                    {
                        "args": [[None], {"frame": {"duration": 0, "redraw": False}, "mode": "immediate", "transition": {"duration": 0}}],
                        "label": "Pause",
                        "method": "animate"
                    }
                ],
                "direction": "left",
                "pad": {"r": 10, "t": 87},
                "showactive": False,
                "type": "buttons",
                "x": 0.1,
                "xanchor": "right",
                "y": 0,
                "yanchor": "top"
            }
        ]

        # Configure the slider
        sliders = [dict(
            steps=[
                dict(method='animate',
                    args=[[f.name], {'frame': {'duration': 5, 'redraw': True}, 'mode': 'immediate', 'fromcurrent': True}],
                    label=str(f.name))
                for f in frames],
            transition={'duration': 1},
            x=0,  # Slider starting position
            y=0,  # Slider starting position
            currentvalue={'visible': True, 'prefix': 'Epoch: '}
        )]

        fig.update_layout(
            sliders=sliders,
            updatemenus=updatemenus,
            polar=dict(
                radialaxis=dict(visible=True, range=[90, 15]),
                angularaxis=dict(direction='clockwise')
            ),
            
            title=f"Satellite Visibility for Epoch {str(unique_epochs[0])}",  # Initial title
            legend_title="Satellite PRN",
        )

        return fig

    def generate_azel_frame(self, epoch, unique_sats, fullday_data_arr_azel):
        traces = []
        filtered_data = fullday_data_arr_azel[fullday_data_arr_azel[:, 0] == epoch]

        # Plot data for each satellite
        for prn in unique_sats:
            prn_arr = filtered_data[filtered_data[:, 2] == prn]
            el_values_mask = prn_arr[:, -2] <= 15
            prn_above = prn_arr[~el_values_mask]

            trace = go.Scatterpolar(
                r= prn_above[:, -1],
                theta=prn_above[:, -2],
                mode='markers+text',
                text = f'G{int(prn):02d}',
                textposition='top right',
                textfont=dict(
                family="Roboto-bold",
                size=16,
                color="black"  # Set text color to black
                    ),
                name=f'G{int(prn):02d}',
                marker=dict(symbol='circle')

            )
            traces.append(trace)
        return traces


    def prepare_date_time_selection(self):
        
        selected_datetime = datetime.combine(st.session_state.selected_date, time(0, 0))
        st.session_state['selected_datetime'] = selected_datetime

        st.session_state['selected_datetime'] = selected_datetime
        second_of_day = (selected_datetime.hour * 3600 +
                        selected_datetime.minute * 60 +
                        selected_datetime.second)
        
        return second_of_day
    
    def load_azel_data(self):

        """
        Load the xyz data from the numpy file.
        """

        # ground pos

        ground_pos = ECEF(self.ground_pos)


        if st.session_state.mode == 'sp3':
            sat_pos_xyz = np.load(self.sp3_npy_path)
        else:
            sat_pos_xyz = np.load(self.brdc_npy_path)

        xyz_arr = ECEF(sat_pos_xyz[:,-3:])
        sat_pos_azel = ground_pos.calculate_azel(xyz_arr)

        full_azel_arr = np.hstack([sat_pos_xyz[:,:3], sat_pos_azel])

        return full_azel_arr
    
    def calculate_fullday_azel(self):
        """Uses the calculated orbit array to calculate azel for entire day"""
        
        orbit_lla_arr = st.session_state.orbit_lla_arr
        
        ground_pos = st.session_state.ground_pos
        
        ground_pos = ECEF(ground_pos.position)
        orbit_lla_obj = LLA(orbit_lla_arr[:,2:], 'd')
        
        orbit_azel = ground_pos.calculate_azel(orbit_lla_obj)
               
        return np.hstack([orbit_lla_arr, orbit_azel])

    
    def count_satellites_above_elevation(self, orbit_lla_arr, elevation_threshold=15):
        """
        Count the number of satellites with elevation above the given threshold for each unique epoch.

        Args:
            orbit_lla_arr (np.ndarray): Array where each row contains satellite data with the first column as the epoch
                                        and the last column as the elevation.
            elevation_threshold (float): The elevation threshold to count satellites.

        Returns:
            np.ndarray, np.ndarray: Arrays containing unique epochs and their corresponding satellite counts.
        """
        # Extract unique epochs
        unique_epochs = np.unique(orbit_lla_arr[:, 0])

        # Initialize list to store satellite counts
        satellite_counts = []

        # Count satellites with elevation above threshold for each unique epoch
        for epoch in unique_epochs:
            # Filter rows for the current epoch
            epoch_rows = orbit_lla_arr[orbit_lla_arr[:, 0] == epoch]
            # Count satellites with elevation above threshold
            satellite_count = np.sum(epoch_rows[:, -1] > elevation_threshold)
            satellite_counts.append(satellite_count)

        return unique_epochs, np.array(satellite_counts)

    def show_satellite_availability_over_time(self, fullday_data_arr_azel):
        
        # replace the elevation below 15 degrees with NaN
        fullday_data_arr_azel[fullday_data_arr_azel[:, -1] <= 15, -1] = np.nan
        
        
        unique_epochs, satellite_counts = self.count_satellites_above_elevation(fullday_data_arr_azel)
        unique_datetimes = [datetime.fromtimestamp(epoch) for epoch in unique_epochs]
        
            # Create a Plotly scatter plot
        fig = go.Figure(data=go.Scatter(x=unique_datetimes, y=satellite_counts, mode='markers+lines'))

        # Update layout
        fig.update_layout(
            title="Number of Satellites with Elevation Above 15°",
            xaxis_title="Epoch",
            yaxis_title="Satellite Count",
        )

        st.plotly_chart(fig, use_container_width=True)        
        
            
    def show_gantt_chart(self, fullday_data_arr_azel):
        ### only works with pandas1.5.3
        #https://discuss.streamlit.io/t/streamlit-error-using-plotly-reproduced-successfully-outside-streamlit/53801
        
        df = pd.DataFrame(fullday_data_arr_azel, columns=['epoch', 'prn', 'lat', 'lon', 'alt', 'az', 'el'])
        
        df['epoch'] = pd.to_datetime(df['epoch'], unit='s')
        
        # Apply the function to each satellite group
        el_crossing_df = df.groupby('prn').apply(self.find_elevation_crossings).reset_index()
        
        # Create a list for the Gantt chart data
        tasks = []
        for _, row in el_crossing_df.iterrows():
            task = {
                'Task': f"G{int(row['prn']):02d}",
                'Start': row['entering_epoch'],
                'Finish': row['leaving_epoch'],
                'Resource': 'Visible'
            }
            tasks.append(task)
            
        tasks_df = pd.DataFrame(tasks)
        
        # Convert Start and Finish columns to datetime
        tasks_df['Start'] = pd.to_datetime(tasks_df['Start'])
        tasks_df['Finish'] = pd.to_datetime(tasks_df['Finish'])
            
        # Create the Gantt chart
        fig = px.timeline(tasks_df, x_start="Start", x_end="Finish", y="Task", color="Resource",
                        title="Satellite Visibility Periods",
                        labels={"Start": "Visibility Start", "Finish": "Visibility End"})

        fig.update_layout(xaxis_title='Time', yaxis_title='Satellite PRN')

        st.plotly_chart(fig, use_container_width=True)        
        
    def find_elevation_crossings(self, group, threshold=15):
        
        # Identify where the elevation crosses the threshold
        above = group['el'] >= threshold
        # Find transitions
        transition_points = above != above.shift()
        transition_points.iloc[0] = False  # Ignore the first point
        
        # Separate entering and leaving points
        entering_sight = group.loc[transition_points & above, 'epoch']
        leaving_sight = group.loc[transition_points & ~above, 'epoch']
        
        # If the group starts above the threshold, there's no entering point at the start
        if above.iloc[0]:
            entering_sight = pd.concat([pd.Series([group['epoch'].iloc[0]]), entering_sight])

        # If the group ends above the threshold, there's no leaving point at the end
        if above.iloc[-1]:
            leaving_sight = pd.concat([leaving_sight, pd.Series([group['epoch'].iloc[-1]])])

        # Return as DataFrame
        return pd.DataFrame({
            'entering_epoch': entering_sight.reset_index(drop=True),
            'leaving_epoch': leaving_sight.reset_index(drop=True)
        })
        
    def fetch_live_eph(self):
        """
        Fetch live ephemeris data from CHC stream
        
        saves current positions to session state.sat_pos_lla_arr
        saves orbit positions to session state.orbit_lla_arr
        
        """
        
        SatPosCalcs(self, st.session_state).retrieve_and_process_satellite_data()
        