import numpy as np
import pandas as pd
from pathlib import Path
from array import array
from datetime import datetime

class ReadRINEX:
    """
    A class to read RINEX observation files and extract GNSS observation data.
    
    Attributes:
        inPath (Path): Path to the RINEX file.
        logger (Logger, optional): Logger for logging messages.
    
    Methods:
        read(): Reads the RINEX file and returns the extracted data.
        header(): Parses the header of the RINEX file.
        rawData(header): Extracts raw observation data from the RINEX file based on the header information.
        parse_header_line(line, header_dict, lines, i): Parses a single line of the header.
        process_epoch(line, observation_block_lines, gps_obs_types, glonass_obs_types, bds_obs_types, galileo_obs_types, sbas_obs_types, time_buffer, buffers, prn_buffers, sys_buffers): Processes an epoch of observations.
        process_observation_record(line, timestamp, gps_obs_types, glonass_obs_types, bds_obs_types, galileo_obs_types, sbas_obs_types, buffers, prn_buffers, sys_buffers): Processes a single observation record.
        parse_epoch_record(line): Parses the epoch record line.
        parse_observation_record(line, obs_types): Parses an observation record line.
        construct_timestamp(epoch): Constructs a timestamp from the epoch information.
        deconstruct_timestamp(timestamp): Converts an integer timestamp back to a datetime object.
        construct_dataframes(gps_obs_types, glonass_obs_types, bds_obs_types, galileo_obs_types, sbas_obs_types, time_buffer, buffers, prn_buffers, sys_buffers): Constructs dataframes from the buffers.
        create_dataframe(obs_types, buffer, prn_buffer, sys_buffer): Creates a pandas DataFrame from the observation data.
    """
    
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
            # outputs tuple dataframes['G'], dataframes['R'], dataframes['C'], dataframes['E'], dataframes['S'], timestamps
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
        gps_obs_types = header['SYS / # / OBS TYPES'].get('G', [])
        glonass_obs_types = header['SYS / # / OBS TYPES'].get('R', [])
        bds_obs_types = header['SYS / # / OBS TYPES'].get('C', [])
        galileo_obs_types = header['SYS / # / OBS TYPES'].get('E', [])
        sbas_obs_types = header['SYS / # / OBS TYPES'].get('S', [])

        time_buffer = array('d')
        buffers = {sys: array('d') for sys in 'GRCES'}
        prn_buffers = {sys: [] for sys in 'GRCES'}
        sys_buffers = {sys: [] for sys in 'GRCES'}

        with open(self.inPath, 'r') as file:
            lines = file.readlines()

        block_start = 0
        block_end = -1
        
        for line_idx, line in enumerate(lines):
            if line[0] == '>':
                block_start = block_end + 1
                block_end = line_idx
                
                if block_start != 0:
                    observation_block_lines = lines[block_start:block_end]
                    self.process_epoch(line, observation_block_lines, gps_obs_types, glonass_obs_types, bds_obs_types, galileo_obs_types, sbas_obs_types, time_buffer, buffers, prn_buffers, sys_buffers)

        return self.construct_dataframes(gps_obs_types, glonass_obs_types, bds_obs_types, galileo_obs_types, sbas_obs_types, time_buffer, buffers, prn_buffers, sys_buffers)

    def process_epoch(self, line, observation_block_lines, gps_obs_types, glonass_obs_types, bds_obs_types, galileo_obs_types, sbas_obs_types, time_buffer, buffers, prn_buffers, sys_buffers):
        epoch_record = self.parse_epoch_record(line)
        timestamp = self.construct_timestamp(epoch_record[:6])
        time_buffer.append(timestamp)

        num_observations = epoch_record[7]
        for _ in range(num_observations):
            if observation_block_lines:
                obs_line = observation_block_lines.pop(0).strip()
                if not obs_line:
                    break
                self.process_observation_record(obs_line, timestamp, gps_obs_types, glonass_obs_types, bds_obs_types, galileo_obs_types, sbas_obs_types, buffers, prn_buffers, sys_buffers)

    def process_observation_record(self, line, timestamp, gps_obs_types, glonass_obs_types, bds_obs_types, galileo_obs_types, sbas_obs_types, buffers, prn_buffers, sys_buffers):
        sys = line[0]
        prn = line[1:3].strip()
        obs_types = {'G': gps_obs_types, 'R': glonass_obs_types, 'C': bds_obs_types, 'E': galileo_obs_types, 'S': sbas_obs_types}[sys]
        record = self.parse_observation_record(line, obs_types)
        buffers[sys].extend([timestamp] + record)
        prn_buffers[sys].append(prn)
        sys_buffers[sys].append(sys)

    def parse_epoch_record(self, line):
        return [
            int(line[2:6]), int(line[7:9]), int(line[10:12]),
            int(line[13:15]), int(line[16:18]), float(line[18:29]),
            int(line[31:32]), int(line[32:35]), float(line[41:56] or np.nan)
        ]

    def deconstruct_timestamp(self, timestamp):
        # Convert the integer timestamp back to a datetime object
        timestamp_str = str(int(timestamp))
        return datetime(
            year=int(timestamp_str[:4]),
            month=int(timestamp_str[4:6]),
            day=int(timestamp_str[6:8]),
            hour=int(timestamp_str[8:10]),
            minute=int(timestamp_str[10:12]),
            second=int(timestamp_str[12:14])
        )

    def parse_observation_record(self, line, obs_types):
        type_len = len(obs_types)
        return [
            float(line[3 + i*16:17 + i*16].strip() or np.nan)
            for i in range(type_len)
        ]

    def construct_timestamp(self, epoch):
        return int(f"{epoch[0]:04d}{epoch[1]:02d}{epoch[2]:02d}{epoch[3]:02d}{epoch[4]:02d}{int(epoch[5]):02d}")

    def construct_dataframes(self, gps_obs_types, glonass_obs_types, bds_obs_types, galileo_obs_types, sbas_obs_types, time_buffer, buffers, prn_buffers, sys_buffers):
        time_array = np.frombuffer(time_buffer, dtype=np.float64)
        timestamps = [self.deconstruct_timestamp(ts) for ts in time_array]

        dataframes = {}
        for sys, obs_types in zip('GRCES', [gps_obs_types, glonass_obs_types, bds_obs_types, galileo_obs_types, sbas_obs_types]):
            dataframes[sys] = self.create_dataframe(obs_types, buffers[sys], prn_buffers[sys], sys_buffers[sys])

        return dataframes['G'], dataframes['R'], dataframes['C'], dataframes['E'], dataframes['S'], timestamps

    def create_dataframe(self, obs_types, buffer, prn_buffer, sys_buffer):
        if not obs_types:
            return pd.DataFrame()
        data_array = np.frombuffer(buffer, dtype=np.float64).reshape(-1, len(obs_types) + 1)
        timestamps = [self.deconstruct_timestamp(ts) for ts in data_array[:, 0]]
        df = pd.DataFrame(data_array[:, 1:], index=timestamps, columns=obs_types)
        df.insert(0, 'PRN', prn_buffer)  # Insert PRN as the first column
        df.insert(1, 'System', sys_buffer)  # Insert System as the second column
        return df

if __name__ == '__main__':
    file_path = Path(r"F:\obs_data\AC231550.24o")
    
    start = datetime.now()
    
    reader = ReadRINEX(file_path)

    data = reader.read()
    end = datetime.now()
    print(data[0].head())
    print(f"Time taken: {end - start}")
