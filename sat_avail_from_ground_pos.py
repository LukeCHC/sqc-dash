import streamlit as st
import numpy as np
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta
from pathlib import Path

# Import necessary functions from your existing code
from Coord import LLA, ECEF
from GNSS import GPSKepler
from eph_decode_formatter import eph_attributes_to_arr
from sat_pos_calcs import SatPosCalcs

class SatelliteVisibilityApp:
    def __init__(self):
        self.local_dir = Path(r"test")
        self.sat_pos_calcs = SatPosCalcs(self, st.session_state)

    def run(self):
        st.title("Satellite Visibility App")

        # Input for latitude, longitude, date, and time
        col1, col2 = st.columns(2)
        with col1:
            latitude = st.number_input("Latitude", min_value=-90.0, max_value=90.0, value=35.0)
            longitude = st.number_input("Longitude", min_value=-180.0, max_value=180.0, value=100.0)
        with col2:
            date = st.date_input("Date")
            time = st.time_input("Time")

        if st.button("Calculate Satellite Visibility"):
            # Set ground position
            ground_pos = LLA((latitude, longitude, 0), 'd')
            st.session_state.ground_pos = ground_pos

            self.display_ground_pos_info()

            # Calculate satellite visibility
            self.sat_pos_calcs.retrieve_and_process_satellite_data()
            
            # st.write('live_sat_pos', st.session_state.live_sat_pos)
            
            sat_pos_lla_arr = st.session_state.live_sat_pos
            
            sat_pos_lla_obj = LLA(sat_pos_lla_arr[:,2:], 'd') 
            
            sat_azel_arr = ground_pos.calculate_azel(sat_pos_lla_obj)
            
            sat_pos_lla_azel_arr = np.hstack([sat_pos_lla_arr, sat_azel_arr])
            
            # st.write('sat_pos_azel', sat_pos_lla_azel_arr)
            
            self.generate_static_azel_plot(sat_pos_lla_azel_arr)
            
            self.sat_pos_calcs = SatPosCalcs(self, st.session_state)
            fullday_orbit_azel_arr = self.sat_pos_calcs.calculate_fullday_azel()
            
            self.show_satellite_availability_over_time(fullday_orbit_azel_arr)
            
            self.show_gantt_chart(fullday_orbit_azel_arr)        

    def display_ground_pos_info(self):
        """Display the station position"""
        
        ground_pos = st.session_state.ground_pos
        
        ground_pos_df = pd.DataFrame({
            'LAT': [ground_pos.lat_d.item()], 
            'LON': [ground_pos.lon_d.item()], 
            'ALT': [ground_pos.alt_m.item()]
        })
        
        st.map(ground_pos_df, size = 10, zoom = 2, use_container_width=False)

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
        el_crossing_df = df.groupby('prn').apply(self.sat_pos_calcs.find_elevation_crossings).reset_index()
        el_crossing_df.columns = ['PRN', 'Arc Number', 'Entering Epoch', 'Leaving Epoch']
        
        el_crossing_df['PRN'] = [f"G{int(prn):02d}" for prn in el_crossing_df['PRN']]
        el_crossing_df['Arc Number'] = [i + 1 for i in el_crossing_df['Arc Number']]
        
        st.write(el_crossing_df.set_index(['PRN']), use_container_width=True)
        
        # Create a list for the Gantt chart data
        tasks = []
        for _, row in el_crossing_df.iterrows():
            task = {
                'Task': row['PRN'],
                'Start': row['Entering Epoch'],
                'Finish': row['Leaving Epoch'],
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

if __name__ == "__main__":
    app = SatelliteVisibilityApp()
    app.run()