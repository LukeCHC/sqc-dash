import streamlit as st
from pathlib import Path
import numpy as np
from datetime import datetime, time, timedelta
from plotly import graph_objects as go

from GNSS import GPSKepler
from Coord import ECEF
from chc_modules import FindSV, FindSvBrdc
from download_live_eph import tcprecv_data, DownloadAndDecodeChcEph
from eph_decode_formatter import eph_attributes_to_arr, extract_eph_attributes

class SkyMapper:
    
    def __init__(self):
        self.local_dir = Path(r"F:\skymap_test")
        pass

    def main(self):
        """
        Main function to run the Streamlit app.
        """
        # Set the page configuration
        st.set_page_config(layout="wide")

        # Display the app title
        st.title("Your Dashboard Title Here")


        ## initialise states
        if 'plot_persist' not in st.session_state:
            st.session_state.plot_persist = False

        if 'plot_ready' not in st.session_state:
            st.session_state.plot_ready = False

        if 'selected_date' not in st.session_state:
            st.session_state.selected_date = False

        if 'selected_datetime' not in st.session_state:
            st.session_state.selected_datetime = False

        if 'mode' not in st.session_state:
            st.session_state.mode = False

        if 'show_azel' not in st.session_state:
            st.session_state.show_azel = False

        if 'show_live' not in st.session_state:
            st.session_state.show_live = False

        self.display_sidebar_options()

        if st.session_state.plot_persist:
            if st.session_state.selected_date:
                if st.session_state.selected_datetime:
                    self.prepare_map_plot()

        if st.session_state.show_azel:
            self.display_azel()

        if st.session_state.show_live:
            self.display_live_tracker()

        
    def display_live_tracker(self):
        """
        Displays the live tracker
        """

        EPHIP = '18.170.8.65'
        EPHPORT = 10011

        st.write("Live Tracker")
        decoded_data = DownloadAndDecodeChcEph(EPHIP, EPHPORT).run()

        gps_eph_data = decoded_data[1].ephgps

        gps_eph_arr = eph_attributes_to_arr(gps_eph_data)
        
        gps_kepler = GPSKepler(gps_eph_arr)
        sv_pos_xyz = gps_kepler.run()


        sat_pos_ecef = ECEF(sv_pos_xyz[:,3:])
        sat_pos_lla = sat_pos_ecef.ecef2lla()
        sat_pos_lla_arr = np.hstack([sv_pos_xyz[:,:3], sat_pos_lla.lat_d, sat_pos_lla.lon_d])
            

        self._show_live_plot(sat_pos_lla_arr)

    def _show_live_plot(self, sat_pos_lla_arr):

        import plotly.graph_objects as go

        fig = go.Figure()

        unique_prn = np.unique(sat_pos_lla_arr[:,2])

        st.write(f"Unique PRN: {unique_prn}")

        for prn in unique_prn:
            mask = np.where(sat_pos_lla_arr[:,2] == prn)
            single_sat_arr = sat_pos_lla_arr[mask]
            fig = self.plot_satellite_positions(fig, single_sat_arr)
        
        fig.update_layout(
            title = 'Satellite Positions',
            geo_scope='world',
            width=1500,  # Custom figure width
            height=700  # Custom figure height
        )

        fig.update_geos(
            resolution=50,
            showcoastlines=True, coastlinecolor="RebeccaPurple",
            showland=True, landcolor="LightGreen",
            showocean=True, oceancolor="LightBlue",
            showlakes=True, lakecolor="Blue",
            showrivers=True, rivercolor="Blue"
        )
        st.plotly_chart(fig)

    def display_sidebar_options(self):
        """
        Displays options for the user to select.
        """

        selected_date = st.sidebar.date_input("Select a date", value=datetime.now())
        st.session_state.selected_date = selected_date

        year = selected_date.year
        month = selected_date.month
        day = selected_date.day
        doy = selected_date.timetuple().tm_yday

        self.input_date = datetime(year, month, day)

        self.sp3_npy_path = self.local_dir/ "sv_pos_npy" / f"sv_pos_sp3_{year}_{doy:03d}_G.npy"
        self.brdc_npy_path = self.local_dir/ f"sv_pos_brdc_{year}_{doy:03d}_G.npy"
        
        st.session_state.plot_ready = False


        if not self.brdc_npy_path.exists():
            st.sidebar.button("Download BRDC", on_click = self.find_sv_brdc)
        else:
            st.sidebar.write("BRDC file exists")
            st.session_state.plot_ready = True
            st.session_state.mode = 'brdc'

        if not self.sp3_npy_path.exists():
            st.sidebar.button("Download SP3", on_click = self.find_sv_sp3)
        else: 
            st.sidebar.write("SP3 file exists")
            st.session_state.mode = 'sp3'
            if not st.session_state.plot_ready:
                st.session_state.plot_ready = True
        
        if st.session_state.plot_ready:
            if st.sidebar.button("Plot") or st.session_state.plot_persist:
                st.session_state.selected_datetime = datetime.combine(selected_date, time(0, 0))
                st.session_state.plot_persist = True

            if st.sidebar.button("Azel"):
                st.session_state.plot_persist = False
                st.session_state.show_azel = True

        if st.sidebar.button("Live Tracker"):
            st.session_state.plot_persist = False
            st.session_state.show_azel = False
            st.session_state.show_live = True

    def find_sv_sp3(self):
        """
        calls find sv
        """
        st.sidebar.write("Downloading SP3")
        FindSV(self.input_date, 'G', self.local_dir).run()
        st.sidebar.write("Downloaded SP3")

    def find_sv_brdc(self):
        """
        calls find sv brdc
        """
        st.sidebar.write("Downloading BRDC")
        FindSvBrdc(self.input_date, 'G', self.local_dir).run()
        st.sidebar.write("Downloaded BRDC")

    def prepare_map_plot(self, mode = 'sp3'):

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
        
        ground_pos_lla = (0, 0, 0)# self.get_ground_pos()

        mode = st.session_state.mode

        self.display_scattergeo_fig(second_of_day, ground_pos_lla, mode)        

    def display_azel(self):
        """
        Displays azel information
        """

        lat_input = st.number_input("Latitude", value=0.0, min_value = -90.0, max_value= 90.0, step = 0.5)
        lon_input = st.number_input("Longitude", value=0.0, min_value = -90.0, max_value= 90.0, step = 0.5)

        if st.button("Calculate"):

            print("Calculating")

            ground_pos = ECEF([lat_input, lon_input, 0.0])

            azel_arr = self.calc_azel(ground_pos)

            print("azel calculated")
        
            self.display_azel_plot(azel_arr)

    def _get_azel_traces_per_epoch(self, epoch_selected, unique_sats, full_azel_arr):
        traces = []
        filtered_data = full_azel_arr[full_azel_arr[:, 0] == epoch_selected]

        # Plot data for each satellite
        for prn in unique_sats:
            prn_arr = filtered_data[filtered_data[:, 2] == prn]
            el_values_mask = prn_arr[:, -2] <= 15
            prn_above = prn_arr[~el_values_mask]

            trace = go.Scatterpolar(
                r= prn_above[:, -1],
                theta=prn_above[:, -2],
                mode='markers',
                name=f'G{int(prn):02d}',
                marker=dict(symbol='circle')
            )
            traces.append(trace)
        return traces

    def display_azel_plot(self, azel_arr):

        SAMPLE = 20

        # Initial Plot
        unique_epochs = np.unique(azel_arr[:, 0])[::SAMPLE]
        unique_sats = np.unique(azel_arr[:, 2])
        fig = go.Figure()

        # Preparing frames for each epoch
        frames = []
        for epoch in unique_epochs:
            frame_traces = self._get_azel_traces_per_epoch(epoch, unique_sats, azel_arr)
            frames.append(go.Frame(data=frame_traces, name=str(epoch)))

        # Set up the initial state of the figure with the first epoch's data
        fig.add_traces(frames[0].data)

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
                radialaxis=dict(visible=True, range=[90, 0]),
                angularaxis=dict(direction='clockwise')
            ),
            title=f"Satellite Visibility for Epoch {str(unique_epochs[0])}",  # Initial title
            legend_title="Satellite PRN",
        )

        # Update layout with frames
        fig.frames = frames

        # Show the figure
        st.plotly_chart(fig)

    def calc_azel(self, ground_pos):

        mode = st.session_state.mode


        if mode == 'sp3':
            sat_pos_xyz = np.load(self.sp3_npy_path)
        else:
            sat_pos_xyz = np.load(self.brdc_npy_path)

        xyz_arr = ECEF(sat_pos_xyz[:,-3:])

        sat_pos_azel = ground_pos.calculate_azel(xyz_arr)


        full_azel_arr = np.hstack([sat_pos_xyz[:,:3], sat_pos_azel])

        return full_azel_arr

    def get_field_of_view(self, ground_pos_lla = (0,0,0), elevation_mask_deg = 10):
        """
        Calculate the field of view of a receiver on the ground.
        
        note: doesnt include atmos refraction

        """ 
        # Convert elevation mask from degrees to radians
        theta_rad = np.radians(elevation_mask_deg)

        # Calculate the angular radius of the visible sky
        angular_radius_rad = np.radians(90) - theta_rad

        # Calculate the area of the spherical cap
        visible_sky_area = 2 * np.pi * (1 - np.cos(angular_radius_rad))

        return visible_sky_area

    def display_scattergeo_fig(self, second_of_day, ground_pos_lla, mode = 'sp3'):
        """
        Creates a scattergeo plot using Plotly.
        """
        import plotly.graph_objects as go
        ground_lat, ground_lon, ground_alt = ground_pos_lla
        num_points = 100

        sat_pos_lla_arr = self.load_lla_data(second_of_day, mode)

        fig = go.Figure()

        unique_prn = np.unique(sat_pos_lla_arr[:,0])

        hours, remainder = divmod(second_of_day, 3600)
        minutes, seconds = divmod(remainder, 60)
        epoch = datetime.combine(datetime.today().date(),time(int(hours), int(minutes), int(seconds)))
        epoch_list = [(epoch + timedelta(seconds = i)).time() for i in range(-3600, 3900, 300)]  


        st.write(f"{epoch_list[0]} to {epoch_list[-1]}")

        for prn in unique_prn:
            mask = np.where(sat_pos_lla_arr[:,0] == prn)
            single_sat_arr = sat_pos_lla_arr[mask]
            fig = self.plot_satellite_positions(fig, single_sat_arr, epoch_list)
        

        
        fov_steradians = self.get_field_of_view()

        angular_radius_deg = self.steradians_to_degrees(fov_steradians)
        
        # Generate points for the circle
        lats = [ground_lat + np.cos(np.radians(angle)) * angular_radius_deg for angle in np.linspace(0, 360, num_points)]
        lons = [ground_lon + np.sin(np.radians(angle)) * angular_radius_deg / np.cos(np.radians(ground_lat)) for angle in np.linspace(0, 360, num_points)]

        # Add the FoV circle to the plot
        fig.add_trace(go.Scattergeo(
            lon = lons,
            lat = lats,
            mode = 'lines',
            line = dict(width = 2, color = 'brown'),
        ))
        fig.update_layout(
            title = 'Satellite Positions',
            geo_scope='world',
            width=1500,  # Custom figure width
            height=700  # Custom figure height
        )

        fig.update_geos(
            resolution=50,
            showcoastlines=True, coastlinecolor="RebeccaPurple",
            showland=True, landcolor="LightGreen",
            showocean=True, oceancolor="LightBlue",
            showlakes=True, lakecolor="Blue",
            showrivers=True, rivercolor="Blue"
        )
        st.plotly_chart(fig)

    def get_center_of_arc(self, data):
        """Gets the sat position that is in the middle of the arc"""
        n = len(data)
        central_idx = n // 2
        return data[central_idx]

    def plot_satellite_positions(self, fig, single_sat_arr, epoch_list= None):

        sample_indices = np.linspace(0, len(single_sat_arr) - 1, num=25, dtype=int)


        try:
            prn = single_sat_arr[:,0][sample_indices]
            lat = single_sat_arr[:,1][sample_indices]
            lon = single_sat_arr[:,2][sample_indices]

        except:
            prn = single_sat_arr[:,0]
            lat = single_sat_arr[:,1]
            lon = single_sat_arr[:,2]

        try:
            sat_lat = self.get_center_of_arc(lat)
            sat_lon = self.get_center_of_arc(lon)
        except:
            sat_lat = lat
            sat_lon = lon

        prn_code = [f"G{int(i):02d}" for i in prn]

        # plot the current position
        fig.add_trace(go.Scattergeo(
            lon = [sat_lon],
            lat = [sat_lat],
            text=[prn_code[0]],
            mode = 'markers',
            marker = dict(
                size = 10,
                color = 'rgb(255, 0, 0)',
                line = dict(
                    width = 3,
                    color = 'rgba(68, 68, 68, 0)'
                )
            )
        ))

        if epoch_list is not None:
            # plot the orbits
            fig.add_trace(go.Scattergeo(
                lon = lon,
                lat = lat,
                text=[f"{prn_code[i]} {epoch_list[i].strftime('%H:%M')}" for i in range(len(lat))],
                mode = 'lines',
                line = dict(width = 2, color = 'blue'),
            ))

        return fig

    def load_lla_data(self, second_of_day, mode = 'sp3'):
        """
        Load the xyz data from the numpy file.
        """
        if mode == 'sp3':
            sat_pos_xyz = np.load(self.sp3_npy_path)
        else:
            sat_pos_xyz = np.load(self.brdc_npy_path)

        time_mask = np.where(np.abs(sat_pos_xyz[:,0] - int(second_of_day)) <= 3600)

        current_epoch_pos = sat_pos_xyz[time_mask]

        sat_pos_xyz = ECEF(current_epoch_pos[:,-3:])
        sat_pos_lla = sat_pos_xyz.ecef2lla()
        prn = current_epoch_pos[:,2]
        full_arr = np.vstack([prn, sat_pos_lla.lat_d, sat_pos_lla.lon_d]).T

        return full_arr
        

    def steradians_to_degrees(self, area):
        """Convert an area in steradians to an angular radius in degrees."""
        return np.degrees(np.arccos(1 - area / (2 * np.pi)))


if __name__ == "__main__":
    
    SkyMapper().main()
