import plotly.graph_objects as go
import streamlit as st
from datetime import datetime, time, timedelta
import numpy as np
from matplotlib import pyplot as plt

from Coord import ECEF
from download_live_eph import DownloadAndDecodeChcEph
from GNSS import GPSKepler
from eph_decode_formatter import eph_attributes_to_arr

class SkyMapAzEl:
    def __init__(self, SkyMapDash, session_state):
        """self inherited from SkyMapDash"""

        # self.mode = SkyMapDash.mode
        self.local_dir = SkyMapDash.local_dir
        st.session_state = session_state
        self.sp3_npy_path = SkyMapDash.sp3_npy_path
        self.brdc_npy_path = SkyMapDash.brdc_npy_path

        if st.session_state.selected_station:
            self.ground_pos = SkyMapDash.ground_pos

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

        self.show_availability_table(fullday_data_arr_azel)


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
    
    def show_availability_table(self, fullday_data_arr_azel):

        st.write("Satellite Availability Over a Day")

        unique_sats = np.unique(fullday_data_arr_azel[:, 2])
        unique_epochs = np.unique(fullday_data_arr_azel[:, 0])

        # Create a mapping from epoch and satellites to their indices
        epoch_to_idx = {epoch: i for i, epoch in enumerate(unique_epochs)}
        sat_to_idx = {sat: i for i, sat in enumerate(unique_sats)}

        availability_matrix = np.zeros((len(unique_sats), len(unique_epochs)), dtype=int)

        # Get indices of all epochs and satellites in the data
        epoch_indices = np.vectorize(epoch_to_idx.get)(fullday_data_arr_azel[:, 0])
        sat_indices = np.vectorize(sat_to_idx.get)(fullday_data_arr_azel[:, 2])

        # Mask for elevation above 15 degrees
        elevation_mask = fullday_data_arr_azel[:, -1] > 15

        # Use these indices to directly access and update the availability matrix
        np.add.at(availability_matrix, (sat_indices[elevation_mask], epoch_indices[elevation_mask]), 1)

        # The matrix is ready, and you can normalize it if multiple entries occur for the same epoch and satellite
        availability_matrix = (availability_matrix > 0).astype(int)

        epoch_datetimes = [datetime.fromtimestamp(epoch) for epoch in unique_epochs]

        # Plotting the heatmap
        plt.figure(figsize=(10, 8))
        cmap = plt.get_cmap('coolwarm')  # Using a two-tone colormap

        # Plot the heatmap
        cax = plt.imshow(availability_matrix, aspect='auto', cmap=cmap)
        plt.colorbar(cax, label='Availability (1 = Available, 0 = Not Available)')

        # Generate labels for every 3 hours
        # This time we ensure that we only create labels for existing ticks
        tick_positions = []  # Positions where ticks will be placed
        tick_labels = []     # Corresponding labels for these positions

        for i, dt in enumerate(epoch_datetimes):
            if dt.hour % 3 == 0:  # Every 3 hours
                tick_positions.append(i)
                tick_labels.append(dt.strftime('%H:%M'))

        # Set x-axis ticks to display time of day, every 3 hours
        plt.xticks(ticks=tick_positions, labels=tick_labels)

        # Set y-axis labels to display satellite PRNs with 'G' prefix
        plt.yticks(ticks=np.arange(len(unique_sats)), labels=[f"G{int(prn):02d}" for prn in unique_sats])

        plt.xlabel('Time of Day')
        plt.ylabel('Satellites (PRN)')
        plt.title('Satellite Availability Over a Day')
        plt.grid(False)  # Turn off the grid if preferred

        st.pyplot(plt)


        




