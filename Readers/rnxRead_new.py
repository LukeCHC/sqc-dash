import numpy as np
import pandas as pd
from pathlib import Path

class OptimizedReadRINEX:
    def __init__(self, inPath, logger=None):
        self.inPath = inPath
        self.logger = logger

    def _log(self, message):
        if self.logger:
            self.logger.write_log(message)
        else:
            print(message)

    def read(self):
        try:
            self._log("Reading header")
            header = self.header()
            self._log("Reading raw data")
            data = self.rawData(header)
            return data

        except Exception as e:
            self._log(f"Error reading RINEX file: {e}")
            return None

    def header(self):
        header_dict = {
            'RINEX VERSION / TYPE': '',
            'PGM / RUN BY / DATE': '',
            'COMMENT': '',
            'MARKER NAME': '',
            'MARKER NUMBER': '',
            'MARKER TYPE': '',
            'OBSERVER / AGENCY': '',
            'REC # / TYPE / VERS': '',
            'ANT # / TYPE': '',
            'APPROX POSITION XYZ': [0, 0, 0],
            'ANTENNA: DELTA H/E/N': [0, 0, 0],
            'ANTENNA: DELTA X/Y/Z': [0, 0, 0],
            'ANTENNA: PHASECENTER': '',
            'ANTENNA: B.SIGHT XYZ': [0, 0, 0],
            'ANTENNA: ZERODIR AZI': 0,
            'ANTENNA: ZERODIR XYZ': [0, 0, 0],
            'CENTER OF MASS: XYZ': [0, 0, 0],
            'SYS / # / OBS TYPES': {'G': [], 'R': [], 'C': [], 'E': [], 'S': [], 'J': [], 'I': []},
            'SIGNAL STRENGTH UNIT': '',
            'INTERVAL': 0,
            'TIME OF FIRST OBS': [0, 0, 0, 0, 0, 0.0],
            'TIME OF LAST OBS': [0, 0, 0, 0, 0, 0.0],
            'RCV CLOCK OFFS APPL': 0,
            'SYS / DCBS APPLIED': '',
            'SYS / PCVS APPLIED': '',
            'SYS / SCALE FACTOR': '',
            'SYS / PHASE SHIFT': {'G': {}, 'R': {}, 'C': {}, 'E': {}, 'S': {}, 'J': {}, 'I': {}},
            'GLONASS SLOT / FRQ #': '',
            'GLONASS COD/PHS/BIS': '',
            'LEAP SECONDS': 0,
            '# OF SATELLITES': 0,
            'PRN / # OF OBS': ''
        }

        with open(self.inPath, 'r') as file:
            lines = file.readlines()

        i = 0
        while i < len(lines):
            line = lines[i]
            if 'END OF HEADER' in line:
                break
            i = self.parse_header_line(line, header_dict, lines, i)
        
        return header_dict
    
    def parse_header_line(self, line, header_dict, lines, i):
        key = line[60:].strip()
        try:
            if key in header_dict:
                if key.startswith('SYS / # / OBS TYPES'):
                    sys_id = line[0]
                    num_obs_types = int(line[3:6])
                    obs_types = line[7:60].split()
                    if num_obs_types > 14:
                        i += 1
                        next_line = lines[i].strip()
                        obs_types += next_line[7:60].split()
                    header_dict['SYS / # / OBS TYPES'][sys_id].extend(obs_types)
                elif 'APPROX POSITION XYZ' in key or 'ANTENNA: DELTA' in key or 'CENTER OF MASS: XYZ' in key:
                    header_dict[key] = [float(line[i:i+14].strip()) for i in range(0, 42, 14)]
                elif 'TIME OF' in key:
                    header_dict[key] = [
                        int(line[0:6].strip()), int(line[6:12].strip()), int(line[12:18].strip()), 
                        int(line[18:24].strip()), int(line[24:30].strip()), float(line[30:43].strip())
                    ]
                else:
                    header_dict[key] = line[:60].strip()
        except ValueError as e:
            self._log(f"Error parsing header line: {e}")
            self._log(f"Line: {line.strip()}")
        return i + 1

    def rawData(self, header):
        obs_types = header['SYS / # / OBS TYPES']
        max_obs = max(len(types) for types in obs_types.values())

        data = {sys: [] for sys in 'GRCES'}
        timestamps = []

        with open(self.inPath, 'r') as file:  # Changed to text mode
            for line in file:
                if line.startswith('>'):
                    epoch_record = self.parse_epoch_record(line)
                    timestamp = self.construct_timestamp(epoch_record[:6])
                    timestamps.append(timestamp)
                    num_observations = epoch_record[7]

                    for _ in range(num_observations):
                        obs_line = file.readline().strip()
                        if not obs_line:
                            break
                        sys = obs_line[0]
                        record = self.parse_observation_record(obs_line, len(obs_types[sys]))
                        data[sys].append([timestamp] + record + [np.nan] * (max_obs - len(record)))

        return self.construct_dataframes(obs_types, data, timestamps)

    def parse_epoch_record(self, line):
        # Parse the epoch record using string operations
        parts = line.split()
        year, month, day, hour, minute = map(int, parts[1:6])
        second = float(parts[6])
        flag = int(parts[7])
        num_sv = int(parts[8])
        
        # Parse receiver clock offset if present
        clock_offset = float(parts[9]) if len(parts) > 9 else 0.0
        
        return [year, month, day, hour, minute, second, flag, num_sv, clock_offset]

    def parse_observation_record(self, line, num_obs):
        # Parse observation record using string operations
        obs = []
        for i in range(num_obs):
            start = 3 + i * 16
            end = start + 14
            value = line[start:end].strip()
            obs.append(float(value) if value else np.nan)
        return obs

    def construct_timestamp(self, epoch):
        return int(f"{epoch[0]:04d}{epoch[1]:02d}{epoch[2]:02d}{epoch[3]:02d}{epoch[4]:02d}{int(epoch[5]):02d}")

    def construct_dataframes(self, obs_types, data, timestamps):
        dfs = {}
        for sys in 'GRCES':
            if data[sys]:
                df = pd.DataFrame(data[sys], columns=['timestamp'] + obs_types[sys])
                df['timestamp'] = pd.to_datetime(df['timestamp'], format='%Y%m%d%H%M%S')
                df.set_index('timestamp', inplace=True)
                dfs[sys] = df

        return tuple(dfs.get(sys, pd.DataFrame()) for sys in 'GRCES') + (pd.to_datetime(timestamps, format='%Y%m%d%H%M%S'),)

if __name__ == '__main__':
    from datetime import datetime

    file_path = Path(r"F:\obs_data\AC231550.24o")
    
    start = datetime.now()
    
    reader = OptimizedReadRINEX(file_path)

    data = reader.read()
    end = datetime.now()
    print(data)
    print(f"Time taken: {end - start}")