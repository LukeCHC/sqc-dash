import streamlit as st
import folium
import json
import numpy as np
from datetime import datetime

from streamlit_folium import st_folium
from folium.features import DivIcon
from sat_pos_calcs import SatPosCalcs

class FoliumMap:
    def __init__(self, SkyMapDash, session_state):
        """
        Initialize the Folium map

        SkyMapDash: SkyMapDash
            Instance of the SkyMapDash class

        session_state: SessionState
            Session state object

        """
        
        self.SkyMapDash = SkyMapDash
        self.local_dir = SkyMapDash.local_dir
        st.session_state = session_state
        
    def show(self):
        """Show the Folium map"""
        
        self.show_multi_options()
        
        SH_COORDINATES = (31.23, 121.47)
        
        m = folium.Map(
            location=SH_COORDINATES,
            zoom_start=3.5,
            control_scale=True,
            zoom_control=False,
            scrollWheelZoom=True,
            dragging=True,
            attributionControl=False,
            max_bounds=True,
            
            )
        
        fg_stations = self.add_station_markers()
        
        fg_satellites = self.add_satellite_markers()
        
        fg_orbits = self.add_satellite_orbits()
        
        m.add_child(fg_stations)
        m.add_child(fg_satellites)
        m.add_child(fg_orbits)
        m.keep_in_front(fg_satellites)
        
        st_data = st_folium(m, width=1300, height=700)  # Ensure st_folium is properly imported
        
    def show_multi_options(self):
        
        st.sidebar.write('## Map Options')
        
        with st.sidebar:
            
            check1 = st.checkbox("Display SH Stations", key="sh")
            st.session_state.shanghai = check1

            check2 = st.checkbox("Display GD Stations", key="gd")
            st.session_state.guangdong = check2
            
            if st.button("Get Live Ephemeris"):
                self.get_live_eph()

            if st.session_state.live_sat_pos is not None:
                check3 = st.checkbox("Display Satellites", key="sv")
                st.session_state.satellites = check3
    
            if st.session_state.orbit_lla_arr is not None:
                check4 = st.checkbox("Display Orbits", key="orb")
                st.session_state.orbit = check4
        
    def get_live_eph(self):
        """
        Fetch live ephemeris data from CHC stream
        
        saves current positions to session state.sat_pos_lla_arr
        saves orbit positions to session state.orbit_lla_arr
        
        """
        
        SatPosCalcs(self, st.session_state).retrieve_and_process_satellite_data('short')
        
    def add_station_markers(self):
        """
        Add station markers to the map
        
        fg: folium.FeatureGroup
            Feature group to add the markers to
        """
        
        fg = folium.FeatureGroup(name='Stations')
        
        station_dict = {}
        
        if st.session_state.shanghai:
            with open("misc/sh_stn_list.json") as f:
                sh_stations = json.load(f)
                fg = self.add_markers_from_dict(sh_stations, fg)
                
        if st.session_state.guangdong:
            with open("misc/gd_stn_list.json") as f:
                gd_stations = json.load(f)
                fg = self.add_markers_from_dict(gd_stations, fg)  
                            
            
        return fg
    
    def add_satellite_markers(self):
        """
        Add satellite markers to the map
        """
        fg = folium.FeatureGroup(name='Satellites')
    
        sat_pos_arr = st.session_state.live_sat_pos
    
        if sat_pos_arr is not None:
            if st.session_state.satellites:
                for i in range(sat_pos_arr.shape[0]):
                    lat = sat_pos_arr[i, 2]
                    lon = sat_pos_arr[i, 3]
                    prn = int(sat_pos_arr[i, 1])
                    altitude = sat_pos_arr[i, 4]  # Assuming the altitude is stored at index 4
                
                    sat_icon = folium.CustomIcon(
                        icon_image='misc/satellite.png',
                        icon_size=(30, 45),
                        icon_anchor=(10, 25),
                        popup_anchor=(-3, -76),
                    )
                
                    text_icon = DivIcon(
                        icon_size=(30, 45),
                        icon_anchor=(15, 45),
                        popup_anchor=(-3, -76),
                        html='<div style="font-size: 12pt; color: black; font-weight: bold;">G%s</div>' % format(prn, '02d')
                    )
                
                    nested_popup_html = f"""
                    <div id='nested-popup-{prn}' style='display:none;'>
                        <strong>Additional Information</strong><br>
                        Detailed info about satellite G{prn:02d}...<br>
                        Haha Lol Omg Wow Such Info <br>
                        Luke is so smart<br>
                        <a href="#" onclick="document.getElementById('nested-popup-{prn}').style.display='none';return false;">Close</a>
                    </div>
                    <a href="#" onclick="document.getElementById('nested-popup-{prn}').style.display='block';return false;"></a>
                    <div id='main-popup-{prn}'>
                        <strong>Satellite PRN:</strong> G{prn:02d}<br>
                        <strong>Latitude:</strong> {lat:.2f}<br>
                        <strong>Longitude:</strong> {lon:.2f}<br>
                        <strong>Altitude:</strong> {altitude:.2f} km<br>
                        <a href="#" onclick="document.getElementById('nested-popup-{prn}').style.display='block';return false;">More info</a>
                    </div>
                    """

                    fg.add_child(
                        folium.Marker(
                            location=[lat, lon],
                            popup=folium.Popup(nested_popup_html, max_width=300),
                            icon=sat_icon,
                        )
                    )
                
                    fg.add_child(
                        folium.Marker(
                            location=[lat, lon],
                            icon=text_icon
                        )
                    )
    
        return fg
    
    def add_satellite_orbits(self):
        """ Add satellite orbits to the map"""
        
        fg = folium.FeatureGroup(name='Orbits')
        
        orbit_lla_arr = st.session_state.orbit_lla_arr
        
        if orbit_lla_arr is not None:
            if st.session_state.orbit:
                
                unique_prns = np.unique(orbit_lla_arr[:,1])
                
                for prn in unique_prns:
                    prn_orbit = orbit_lla_arr[orbit_lla_arr[:,1] == prn]
                    
                    # Process coordinates to handle antimeridian crossing, this prevents orbit lines from wrapping around the map
                    split_orbits = self.split_coordinates_at_antimeridian(prn_orbit[:, 2:])
                
                    tooltip_html = f'<span style="font-size: 14pt;">G{int(prn):02d} </span>'
                    
                    for arc in split_orbits:
                        
                        arc_without_alt = arc[:, :2]
                                            
                        fg.add_child(
                            folium.PolyLine(
                                # locations=prn_orbit[:,2:],
                                locations=arc_without_alt,
                                color='red',
                                weight=2,
                                opacity=0.6,
                                tooltip=tooltip_html,
                                smooth_factor=10
                            )
                        )
        return fg
        
    def split_coordinates_at_antimeridian(self, coordinates):
        """Split coordinates at the antimeridian to prevent wrapping."""
        if len(coordinates) < 2:
            return [coordinates]  # Return the input directly if too few points to split.

        lat_coords = coordinates[:, 0]
        lon_coords = coordinates[:, 1]

        lon_diff = np.diff(lon_coords)
        cross_indices = np.where(np.abs(lon_diff) > 180)[0]

        split_coords = []
        last_index = 0

        for idx in cross_indices:
            # Include the point before the jump, ensure at least two points
            if idx + 1 - last_index > 1:
                segment = coordinates[last_index:idx+1]  # Segment up to and including this index
                split_coords.append(segment)
            last_index = idx + 1

        # Add the last segment if it contains more than one point
        if len(coordinates) - last_index > 1:
            final_segment = coordinates[last_index:]
            split_coords.append(final_segment)

        return split_coords
        
    def add_markers_from_dict(self, station_dict, feature_group):
        """Helper function to add markers to a feature group from a dictionary of stations."""
        
        for stn, info in station_dict.items():
            lat = info['Lat']
            lon = info['Lon']
            feature_group.add_child(
                folium.Marker(
                    location=[lat, lon],
                    popup=f'{stn} <br> {lat}, {lon}',
                    icon=folium.Icon(color='green')
                )
            )
        
        return feature_group
        

        