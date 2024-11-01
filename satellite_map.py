import streamlit as st
import numpy as np
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime
from pathlib import Path
import folium
from folium.features import DivIcon

# Import necessary functions from your existing code
from Coord import LLA
from sat_pos_calcs import SatPosCalcs

# Import necessary functions from your existing code
from streamlit_folium import st_folium
from folium.features import DivIcon

class SatelliteVisibilityApp:
    def __init__(self):
        self.local_dir = Path(r"test")
        self.sat_pos_calcs = SatPosCalcs(self, st.session_state)
        self._init_session_state()

    def _init_session_state(self):
        default_states = {
            'input_lat': 35.0,
            'input_lon': 100.0,
            'sat_pos_lla_arr': None,
            'sat_pos_azel_arr': None,
            'fullday_orbit_azel_arr': None,
        }

        for key, value in default_states.items():
            if key not in st.session_state:
                st.session_state[key] = value

    def run(self):
        st.title("Satellite Visibility App")
        st.write(":earth_africa: Click the map to set the ground position. Click the button to calculate satellite visibility :earth_africa:")
        self.show_map()
        self.user_input_section()
        col1, col2 = st.columns(2)
        with col1:
            calc_button = st.button("Calculate Satellite Visibility", type='primary', use_container_width=True, key="calc_button")
        with col2:
            instructions_button = st.button(":information_source: How This Works ", use_container_width=True, key="instructions_button")

        if calc_button:
            
            if self.date == datetime.now().date():
                self.calculate_visibility_live()
            else:
                self.calculate_visibility_past()
    
        if instructions_button:
            self.show_instructions()

        self.show_results()

    def user_input_section(self):
        """Handles user input for latitude, longitude, date, and time."""
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            self.latitude = st.number_input("Latitude [-90, 90]", min_value=-90.0, max_value=90.0, value=st.session_state.input_lat, key="latitude_input")
        with col2:
            self.longitude = st.number_input("Longitude [-180, 180]", min_value=-180.0, max_value=180.0, value=st.session_state.input_lon, key="longitude_input")
        with col3:
            self.date = st.date_input("Date", max_value=datetime.now().date(), key="date_input")
        with col4:
            self.time = st.time_input("Time", key="time_input")

    def initialize_map(self):
        self.map = folium.Map(
            location=[st.session_state.input_lat, st.session_state.input_lon],
            zoom_start=3.5,
            control_scale=True,
            zoom_control=False,
            scrollWheelZoom=True,
            dragging=True,
            attributionControl=False,
            max_bounds=True,
        )



    def clear_markers(self):
        marker_keys = [key for key in self.map._children if key.startswith('marker_')]
        for key in marker_keys:
            del self.map._children[key]


    def add_current_position_marker(self):
        folium.Marker(
            [st.session_state.input_lat, st.session_state.input_lon],
            popup="Ground Position",
            icon=folium.Icon(color='green')
        ).add_to(self.map)

    def add_satellite_markers(self):
        if st.session_state.sat_pos_lla_arr is not None:
            for sat_pos in st.session_state.sat_pos_lla_arr:
                folium.Marker(
                    [sat_pos[2], sat_pos[3]],
                    popup=f"G{int(sat_pos[1]):02d}",
                    icon=folium.Icon(color='red')
                ).add_to(self.map)

                folium.Marker(
                    location=[sat_pos[2], sat_pos[3]],
                    icon=DivIcon(
                        icon_size=(30, 45),
                        icon_anchor=(15, 45),
                        popup_anchor=(-3, -76),
                        html='<div style="font-size: 12pt; color: black; font-weight: bold;">G%s</div>' % format(int(sat_pos[1]), '02d')
                    )
                ).add_to(self.map)

    def display_map(self):
        map_output = st_folium(self.map, width=700, height=500, key="map")
        return map_output

    def update_position_on_click(self, map_output):
        if map_output['last_clicked']:
            new_lat, new_lon = map_output['last_clicked']['lat'], map_output['last_clicked']['lng']
            if -90 <= new_lat <= 90 and -180 <= new_lon <= 180:
                st.session_state.input_lat = self.input_lat = new_lat
                st.session_state.input_lon = self.input_lon = new_lon
                if st.session_state.sat_pos_lla_arr is not None:
                    self.calculate_azel()
                folium.Marker(
                    [new_lat, new_lon],
                    popup="Ground Position",
                    icon=folium.Icon(color='green')
                ).add_to(self.map)
                st_folium(self.map, width=700, height=500, key="map")

    def show_map(self):
        self.initialize_map()
        self.clear_markers()
        self.add_current_position_marker()
        self.add_satellite_markers()
        
        # Display the map and handle click events
        map_output = st_folium(self.map, width=700, height=500, key="map")
        
        # Process click events
        if map_output and map_output['last_clicked']:
            new_lat = map_output['last_clicked']['lat']
            new_lon = map_output['last_clicked']['lng']
            if -90 <= new_lat <= 90 and -180 <= new_lon <= 180:
                st.session_state.input_lat = new_lat
                st.session_state.input_lon = new_lon
                if st.session_state.sat_pos_lla_arr is not None:
                    self.calculate_azel()
                # Rerun the app to update the map with new markers
                st.rerun()


        def calculate_visibility_live(self):
            """Calculates and displays satellite visibility based on user input."""
            self.sat_pos_calcs.retrieve_and_process_satellite_data()
            sat_pos_lla_arr = st.session_state.live_sat_pos
            st.session_state.sat_pos_lla_arr = sat_pos_lla_arr
            print(sat_pos_lla_arr.shape)
            self.calculate_azel()
            self.add_satellite_markers()
            self.display_map()

    def calculate_visibility_past(self):
        self.sat_pos_calcs = SatPosCalcs(self, st.session_state)
        self.sat_pos_calcs.retrieve_and_process_satellite_data_past()
        sat_pos_lla_arr = st.session_state.live_sat_pos
        st.session_state.sat_pos_lla_arr = sat_pos_lla_arr
        print(sat_pos_lla_arr.shape)
        self.calculate_azel()
        self.add_satellite_markers()
        self.display_map()
        

    def calculate_azel(self):
        st.write(st.session_state.sat_pos_lla_arr)
        
        ground_pos = LLA((st.session_state.input_lat, st.session_state.input_lon, 0), 'd')
        st.session_state.ground_pos = ground_pos
        sat_pos_lla_arr = st.session_state.sat_pos_lla_arr
        sat_pos_lla_obj = LLA(sat_pos_lla_arr[:, 2:], 'd')
        sat_azel_arr = st.session_state.ground_pos.calculate_azel(sat_pos_lla_obj)
        st.session_state.sat_pos_azel_arr = np.hstack([sat_pos_lla_arr, sat_azel_arr])
        st.session_state.fullday_orbit_azel_arr = self.sat_pos_calcs.calculate_fullday_azel()

    def show_results(self):
        if st.session_state.sat_pos_azel_arr is not None:
            self.generate_static_azel_plot(st.session_state.sat_pos_azel_arr)

        if st.session_state.fullday_orbit_azel_arr is not None:
            self.show_satellite_availability_over_time(st.session_state.fullday_orbit_azel_arr)
            self.show_gantt_chart(st.session_state.fullday_orbit_azel_arr)

    @st.experimental_dialog("Instructions: ")
    def show_instructions(self):
        st.markdown("""
[Github](https://github.com/LukeCHC/sqc-dash)
### Instructions
1. Click on the map to set the ground station position.
2. Input the date and time.
3. Today's date will use live BRDC ephemeris from a real time stream
4. Past Days will use past BRDC files from NASA CDDIS.
5. Click the button to calculate satellite visibility.

### Steps Involved
1. Connect to live data broadcast or past data ftp.
2. Calculate satellite positions using kepler's laws of planetary motion.
3. Transform satellite positions to Latitude and Longitude.
4. Calculate azimuth and elevation of satellites from the ground station.
""")

    def generate_static_azel_plot(self, sat_pos_azel):
        """Generates a static azimuth-elevation plot for satellite positions."""
        fig = go.Figure()
        unique_sats = np.unique(sat_pos_azel[:, 1])

        for prn in unique_sats:
            prn_arr = sat_pos_azel[sat_pos_azel[:, 1] == prn]
            trace = go.Scatterpolar(
                r=prn_arr[:, -1],
                theta=prn_arr[:, -2],
                mode='markers+text',
                text=f'G{int(prn):02d}',
                textposition='top right',
                textfont=dict(
                    family="Roboto-bold",
                    size=16,
                    color="black"
                ),
                name=f'G{int(prn):02d}',
                marker=dict(symbol='circle')
            )
            fig.add_trace(trace)

        fig.add_trace(go.Scatterpolar(
            r=[15] * 360,
            theta=np.arange(0, 360),
            mode='lines',
            line=dict(color='black', width=1),
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
            width=1600,
            height=700,
            template='plotly'
        )

        st.plotly_chart(fig, use_container_width=True)

    def show_satellite_availability_over_time(self, fullday_data_arr_azel):
        """Shows the number of satellites with elevation above 15° over time."""
        fullday_data_arr_azel[fullday_data_arr_azel[:, -1] <= 15, -1] = np.nan
        unique_epochs, satellite_counts = self.count_satellites_above_elevation(fullday_data_arr_azel)
        unique_datetimes = [datetime.fromtimestamp(epoch) for epoch in unique_epochs]

        fig = go.Figure(data=go.Scatter(x=unique_datetimes, y=satellite_counts, mode='markers+lines'))
        fig.update_layout(
            title="Number of Satellites with Elevation Above 15°",
            xaxis_title="Epoch",
            yaxis_title="Satellite Count",
        )
        st.plotly_chart(fig, use_container_width=True)

    def show_gantt_chart(self, fullday_data_arr_azel):
        """Displays a Gantt chart showing satellite visibility periods."""
        df = pd.DataFrame(fullday_data_arr_azel, columns=['epoch', 'prn', 'lat', 'lon', 'alt', 'az', 'el'])
        df['epoch'] = pd.to_datetime(df['epoch'], unit='s')

        el_crossing_df = df.groupby('prn').apply(self.sat_pos_calcs.find_elevation_crossings, include_groups=False).reset_index()
        el_crossing_df.columns = ['PRN', 'Arc Number', 'Entering Epoch', 'Leaving Epoch']

        el_crossing_df['PRN'] = [f"G{int(prn):02d}" for prn in el_crossing_df['PRN']]
        el_crossing_df['Arc Number'] = [i + 1 for i in el_crossing_df['Arc Number']]

        tasks = []
        for _, row in el_crossing_df.iterrows():
            tasks.append({
                'Task': row['PRN'],
                'Start': row['Entering Epoch'],
                'Finish': row['Leaving Epoch'],
                'Resource': 'Visible'
            })

        tasks_df = pd.DataFrame(tasks)
        tasks_df['Start'] = pd.to_datetime(tasks_df['Start'])
        tasks_df['Finish'] = pd.to_datetime(tasks_df['Finish'])

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
        unique_epochs = np.unique(orbit_lla_arr[:, 0])
        satellite_counts = []

        for epoch in unique_epochs:
            epoch_rows = orbit_lla_arr[orbit_lla_arr[:, 0] == epoch]
            satellite_count = np.sum(epoch_rows[:, -1] > elevation_threshold)
            satellite_counts.append(satellite_count)

        return unique_epochs, np.array(satellite_counts)

if __name__ == "__main__":
    app = SatelliteVisibilityApp()
    app.run()


