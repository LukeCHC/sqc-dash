from pathlib import Path
from datetime import datetime, timedelta
import numpy as np
import pandas as pd
import pytz

from Downloading.downloading_brdc import DownloadBrdc
from Readers import ReadBRDC
from GNSS import GPSKepler, MatchEph, BDSKepler, GALKepler


class FindSvBrdc:
    OBS_TIME = 0
    SYS = 1
    PRN = 2
    BIAS = 3
    DRIFT = 4
    DRIFT_RATE = 5
    IODE = 6
    CRS = 7
    DELTAN = 8
    M0 = 9
    CUC = 10
    E = 11
    CUS = 12
    SQRTA = 13
    TOE_SOW = 14
    CIC = 15
    OMEGA0 = 16
    CIS = 17
    I0 = 18
    CRC = 19
    OMEGA = 20
    OMEGA_DOT = 21
    IDOT = 22
    CODES_ON_L2 = 23
    TOE_GPS_WEEK = 24
    L2P_DATA_FLAG = 25
    SV_ACCURACY = 26
    SV_HEALTH = 27
    TGD = 28
    IODC = 29
    TRANSMISSION_TIME = 30
    FIT_INTERVAL = 31
    REF_TIME = 32

    def __init__(
        self,
        process_days,
        system_to_process,
        local_dir,
        save_file_flag=True,
        interval=30,
        logger=None,
    ):
        """
        I SPENT 1 HOUR AND A HALF TRYING TO FIX A STUPID TIMEZONE BUG. I HATE TIMEZONES
        I BELIEVE PD.TO_DATETIME AND DATETIME.FROMTIMESTAMP BEHAVE DIFFERENTLY WHEN IT COMES TO TIMEZONES
        I HATE TIMEZONES
        
        Calculate satellite positions for entire day using brdc files
        can only process one system at a time

        process_days: list of datetime objects
        local_dir: Path object of the local directory to store the brdc files
        system_to_process: str, int, or list of str or int, systems to process ('G', 'R', 'C', 'E') or (1, 2, 3, 4)
        save_file: bool, save the satellite positions to a .npy file
        interval: int, interval in seconds to calculate satellite positions
        logger: SimpleLogger object for logging
        
        
        
        
        NOTE: C59 satellite final result is very perculiar. It is not the same as the other satellites
        
        """

        self.local_dir = Path(local_dir)
        self.save_file_flag = save_file_flag
        self.interval = interval
        self.logger = logger
        self._verify_process_dates(process_days)
        self._generate_process_epochs()
        self._configure_systems(system_to_process)

    def _configure_systems(self, system_to_process):
        sys_map = {"G": 1, "R": 2, "C": 3, "E": 4}
        if isinstance(system_to_process, (str, int)):
            system_to_process = [system_to_process]  # Convert single entry to list

        self.system_to_process = []
        for sys in system_to_process:
            if isinstance(sys, str):
                if sys.upper() in sys_map:
                    self.system_to_process.append(sys_map[sys.upper()])
                else:
                    raise ValueError(f"Unsupported satellite system identifier: {sys}")
            elif isinstance(sys, int):
                if sys in [1, 2, 3, 4]:
                    self.system_to_process.append(sys)
                else:
                    raise ValueError(
                        "system_to_process must be 1, 2, 3, or 4 for integers"
                    )
            else:
                raise TypeError(
                    "system_to_process must be a string or integer, or a list of strings or integers"
                )

    def _verify_process_dates(self, process_days):
        """ensures no duplicate dates in list"""
        if isinstance(process_days, list):
            epoch_dates = [i.date() for i in process_days]
        elif isinstance(process_days, datetime):
            epoch_dates = [process_days.date()]
        else:
            raise TypeError(
                "process_days must be a list of datetime objects or a single datetime object"
            )
        self.process_days = list(set(epoch_dates))

    def _generate_process_epochs(self):
        """generate list of epochs to process"""

        first_day = min(self.process_days)
        last_day = max(self.process_days)

        first_epoch = datetime(first_day.year, first_day.month, first_day.day, 0, 0, 0)
        last_epoch = datetime(last_day.year, last_day.month, last_day.day, 23, 59, 59)

        total_epochs = int((last_epoch - first_epoch).total_seconds())

        self.process_epochs = [
            first_epoch + timedelta(seconds=i)
            for i in range(0, total_epochs, self.interval)
        ]

    def run(self):
        self.download_brdc_files()
        self.load_brdc_files()
        time_match_arrays_list = self.time_match_brdc()
        sv_pos_arr = self.calculate_sv_positions(time_match_arrays_list)

        if self.save_file_flag:
            self.save_sv_positions(sv_pos_arr)

        return sv_pos_arr

    def save_sv_positions(self, sv_pos_arr):
        """save the satellite positions to a .npy file"""

        for system in self.system_to_process:
            sv_pos_sys_arr = sv_pos_arr[sv_pos_arr[:, self.SYS] == system]
            
            unix_timestamps = sv_pos_sys_arr[:, self.OBS_TIME]
            
            datetimes_arr = np.array(
                [datetime.fromtimestamp(i) for i in unix_timestamps], dtype="datetime64[D]"
            )

            day_changes = np.where(np.diff(datetimes_arr) != np.timedelta64(0, "D"))[0] + 1

            sv_pos_sys_arr_split = np.split(sv_pos_sys_arr, day_changes, axis=0)

            sys_letter = {1: "G", 2: "R", 3: "C", 4: "E"}[system]

            for day_idx, sv_pos_day in enumerate(sv_pos_sys_arr_split):
                sv_pos_day = self.replace_timestamp_with_sod(sv_pos_day)

                process_day = self.process_days[day_idx]
                file_name = f"sv_pos_brdc_{process_day.year}_{process_day.timetuple().tm_yday:03d}_{sys_letter}.npy"
                file_path = self.local_dir / file_name
                np.save(file_path, sv_pos_day)

    def replace_timestamp_with_sod(self, sv_pos_day):
        """Replace the first column of the array with the seconds of the day."""

        tz = 'Europe/London'
        local_tz = pytz.timezone(tz)

        # Extract Unix timestamps
        unix_timestamps = sv_pos_day[:, self.OBS_TIME]
        
        # Convert to timezone-aware datetime objects
        timestamps_dt = np.array([pd.to_datetime(ts, unit='s', utc=True).tz_convert(local_tz).to_pydatetime() for ts in unix_timestamps])

        start_of_day = pd.Timestamp(timestamps_dt[0].date(), tz=local_tz)

        # Calculate seconds of day
        sod = np.array([(ts - start_of_day).seconds for ts in timestamps_dt], dtype=int)
        # Replace the first column with seconds of day
        sv_pos_day[:, self.OBS_TIME] = sod

        return sv_pos_day

    def replace_timestamp_with_sod_(self, sv_pos_day):
        """replace the first column of the array with the second of day"""

        # timestamps = sv_pos_day[:,0]
        # timestamps_dt = [datetime.fromtimestamp(i) for i in timestamps]
        # sod = np.array([i.hour * 3600 + i.minute * 60 + i.second for i in timestamps_dt], dtype='int32')
        # sv_pos_day[:,0] = sod

        # Convert UNIX timestamps to 'datetime64[s]'
        tz='Europe/London'
        local_tz = pytz.timezone(tz)
        
        unix_timestamps = sv_pos_day[:, self.OBS_TIME]
        
        # Convert to timezone-aware datetime objects directly
        timestamps_dt = np.array([pd.to_datetime(ts, unit='s', utc=True).tz_convert(local_tz) for ts in unix_timestamps])

        # Determine the start of the day from the first epoch
        start_of_day = pd.Timestamp(timestamps_dt[0].date(), tz=local_tz)

        # Calculate seconds of the day
        sod = np.array([(ts - start_of_day).seconds for ts in timestamps_dt], dtype=int)

        # Replace the first column with seconds of day
        sv_pos_day[:, self.OBS_TIME] = sod
        return sv_pos_day

    def time_match_brdc(self):
        """This time match the correct brdc ephemeris to the epoch we want to calculate the satellite positions for"""

        # tz='Europe/London'
        # local_tz = pytz.timezone(tz)

        epochs_unix_stamp_arr = np.array([i.timestamp() for i in self.process_epochs])
        # epochs_unix_stamp_arr = np.array([local_tz.localize(i).timestamp() for i in self.process_epochs])

        brdc_arrays = self.brdc_arr
        
        time_match_arrays_list = []   

        for i in range(4):
            if i+1 in self.system_to_process:
                brdc_arr = brdc_arrays[i]
                time_match_arrays_list.append(MatchEph(brdc_arr, epochs_unix_stamp_arr).time_match())
            else:
                time_match_arrays_list.append([])

        return time_match_arrays_list

    def calculate_sv_positions(self, time_match_arrays_list):
        sv_pos_list = []  # List to hold satellite position arrays from different systems

        for system in self.system_to_process:
            if system == 1:
                sv_pos_arr = GPSKepler(time_match_arrays_list[0]).run()
            elif system == 3:
                sv_pos_arr = BDSKepler(time_match_arrays_list[2]).run()
            elif system == 4:
                sv_pos_arr = GALKepler(time_match_arrays_list[3]).run()
            else:
                raise ValueError(f"Unsupported satellite system: {system}")

            sv_pos_list.append(sv_pos_arr)

        # Concatenate all position arrays vertically if more than one system is processed
        if len(sv_pos_list) > 1:
            sv_pos_arr = np.vstack(sv_pos_list)
        else:
            sv_pos_arr = sv_pos_list[
                0
            ]  # Directly use the single result if only one system

        return sv_pos_arr

    def load_brdc_files(self):
        """load brdc files into one numpy array"""

        g_array = np.empty([0,33])
        r_array = np.empty([0,18])
        c_array = np.empty([0,30])
        e_array = np.empty([0,30])

        for day in self.process_days:
            year = day.year
            doy = day.timetuple().tm_yday
            file_name = f"BRDC00IGS_R_{year}{doy:03d}0000_01D_MN.rnx"
            local_file_path = self.local_dir / file_name
            if not local_file_path.exists():
                raise FileNotFoundError(f"File {local_file_path} does not exist")

            brdc_data_all_sys = ReadBRDC(local_file_path).read()

            for system in self.system_to_process:
                brdc_data = brdc_data_all_sys[system - 1]
                if system == 1:
                    brdc_data = self.swap_final_ephemeris(brdc_data, system, day)
                    g_array = np.vstack((g_array, brdc_data))
                elif system == 2:
                    r_array = np.vstack((r_array, brdc_data))
                elif system == 3:
                    c_array = np.vstack((c_array, brdc_data))
                elif system == 4:
                    e_array = np.vstack((e_array, brdc_data))
                

        self.brdc_arr = [g_array, r_array, c_array, e_array]

    def swap_final_ephemeris(self, current_day_brdc_data, system_to_process_int, day):
        """Swaps final eph with first eph of next day file, only needed on gps"""
        # gps only for now

        next_day = day + timedelta(days=1)

        year = next_day.year
        doy = day.timetuple().tm_yday
        file_name = f"BRDC00IGS_R_{year}{doy:03d}0000_01D_MN.rnx"
        next_day_file_path = self.local_dir / file_name
        if not next_day_file_path.exists():
            raise FileNotFoundError(f"File {next_day_file_path} does not exist")

        brdc_nextday_data_all_sys = ReadBRDC(next_day_file_path).read()

        brdc_nextday_data = brdc_nextday_data_all_sys[system_to_process_int - 1]

        updated_brdc_arr = np.empty([0, current_day_brdc_data.shape[1]])

        unique_prns = np.unique(current_day_brdc_data[:, self.PRN])

        for prn in unique_prns:
            current_day_prn_arr = current_day_brdc_data[
                current_day_brdc_data[:, self.PRN] == prn
            ]
            next_day_prn_arr = brdc_nextday_data[
                brdc_nextday_data[:, self.PRN] == prn
            ]

            first_eph_nextday = next_day_prn_arr[np.argmin(next_day_prn_arr[:, 0])]
            last_eph_currentday_idx = np.argmax(current_day_prn_arr[:, 0])

            # copy row over to current day
            current_day_prn_arr[last_eph_currentday_idx] = first_eph_nextday

            updated_brdc_arr = np.vstack([updated_brdc_arr, current_day_prn_arr])

        return updated_brdc_arr

    def download_brdc_files(self):
        """downloads brdc files"""
        for day in self.process_days:
            DownloadBrdc(day, self.local_dir, logger=self.logger).download()

        # download next day for time matching to first eph of next day file
        next_day = max(self.process_days) + timedelta(days=1)
        DownloadBrdc(next_day, self.local_dir, logger= self.logger).download()


if __name__ == "__main__":
    # epoch0 = datetime(2021, 1, 1)
    # epoch1 = datetime(2021, 1, 2)
    # epoch2 = datetime(2021, 1, 3)

    # dates = [epoch0, epoch1, epoch2]

    dates = [datetime(2024,6,2)]

    local_dir = Path(r"F:/test/brdc_test")

    print('C')
    # FindSvBrdc(dates, 'G', local_dir).run()
    arr = FindSvBrdc(dates, "C", local_dir, save_file_flag= False).run()
    # print('G')
    # arr = FindSvBrdc(dates, "G", local_dir, save_file_flag= False).run()

    print(arr[0,0])
    print(arr[-1,0])
    
    print(datetime.fromtimestamp(arr[0, 0]))
    print(datetime.fromtimestamp(arr[-1, 0]))
    # print(pd.to_datetime(arr[-1, 0], unit='s'))