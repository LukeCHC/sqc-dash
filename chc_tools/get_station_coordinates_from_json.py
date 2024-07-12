import json
from pathlib import Path
from Coord import LLA, ECEF
import re

def get_station_coordinates_from_json(station_name, json_file_path = Path(r"\\meetingroom\Integrity\SWASQC\station_data\combined_station_list.json")):
    with json_file_path.open() as f:
        stations_json = json.load(f)
        station_values = stations_json[station_name]
        ground_pos = LLA((station_values['Lat'], station_values['Lon'], 0))
        return ground_pos
    
def get_station_coordinates_from_conf(station_name, conf_file_path = Path(r"\\meetingroom\Integrity\BDS155\clk_stations_2024155R.conf")):
    with open(conf_file_path, 'r') as file:
        for line in file:
            
            if line.startswith('#'):
                continue
            
            if line.startswith('A'):
                if station_name in line:
                    parts = line.split()

                    x,y,z = parts[3:6]                    
            
                    ecef = ECEF((x,y,z))
                    ground_pos = ecef.ecef2lla()
                    
                    return ground_pos