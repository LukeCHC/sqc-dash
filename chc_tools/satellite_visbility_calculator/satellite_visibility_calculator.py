import os
from datetime import datetime
from pathlib import Path
import pandas as pd
from tabulate import tabulate
import configparser
from chc_modules.horizon_crossing_calculator import CalculateHorizonCrossings
from Coord import LLA

def read_config():
    """Read configuration from config.ini file in the current working directory."""
    config = configparser.ConfigParser()
    config_path = Path(os.getcwd()) / 'config.ini'
    config.read(config_path)
    
    dates = [datetime.strptime(date.strip(), '%Y-%m-%d') for date in config['Dates']['dates'].split(',')]
    output_folder = Path(config['Paths']['output_folder'])
    
    # Read ground position from config
    latitude = float(config['Ground Position']['latitude'])
    longitude = float(config['Ground Position']['longitude'])
    altitude = float(config['Ground Position']['altitude'])
    
    ground_pos_lla = LLA([latitude, longitude, altitude], 'D')
    
    return dates, output_folder, ground_pos_lla

def process_dates_and_save_to_csv(dates, ground_pos_lla, local_work_dir, csv_path, elevation_mask=15, logger=None):
    """Wrapper tool for Calculate Horizon Crossings class to process multiple dates and save to a csv file."""
    results = []
    for date in dates:
        chc = CalculateHorizonCrossings(date, ground_pos_lla, local_work_dir, elevation_mask, logger)
        el_crossing_df = chc.run()
        results.append(el_crossing_df)
   
    combined_df = pd.concat(results)
   
    # Ensure `sys` and `prn` are integers and all timestamps are uniformly formatted
    combined_df['sys'] = combined_df['sys'].astype(int)
    combined_df['prn'] = combined_df['prn'].astype(int)
   
    # Format the DataFrame as a pretty string without quotes
    formatted_string = tabulate(combined_df, headers='keys', tablefmt='plain', showindex=False)
   
    # Write the formatted string to the CSV file
    with open(csv_path, 'w') as f:
        f.write(formatted_string)

def main():
    dates, output_folder, ground_pos_lla = read_config()
    
    local_work_dir = Path(r"F:/test")
    csv_path = output_folder / "horizon_crossings.csv"
   
    # Ensure output folder exists
    output_folder.mkdir(parents=True, exist_ok=True)
   
    process_dates_and_save_to_csv(dates, ground_pos_lla, local_work_dir, csv_path)

if __name__ == '__main__':
    main()