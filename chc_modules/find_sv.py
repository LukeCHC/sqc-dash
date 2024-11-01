# -*- coding: utf-8 -*-
"""
Created on Thu Oct 20 16:10:10 2022

@author: chcuk
"""
from pathlib import Path
from datetime import datetime, timedelta
import pandas as pd


from Downloading.precise_file_downloading import GNSSDownloader 
from Readers import ReadSP3#, ReadCLK
from Algorithms.nev_interpolation import NevilleInterpolation as NI
import numpy as np

from GNSS.sys_names import SysNames

class FindSV:
    def __init__(self, epoch, system, loc_dir, interval = 30, logger=None):
        """
        Initialize the findSV class.

        Args:
            epoch (datetime): The datetime object for the specific date.
            system (list): List of constellations to process ['G','R','C','E'].
            loc_dir (str): Local directory path for storing files.
            interval (int): Time interval in seconds between points of 
                            interpolation, havent tested obscure values.
            logger (SimpleLogger, optional): Logger for recording activities.

        Returns:
            None
        """
        self.epoch = epoch
        self.system = system
        self.loc_dir = Path(loc_dir)
        self.logger = logger
        self.interval = interval

        # Create subdirectories for different file types
        self.sp3_dir = self.loc_dir / "SP3"
        self.sp3_npy_dir = self.loc_dir / "SP3_NPY"
        self.svPos_dir = self.loc_dir / "SV_POS_NPY"

        self.sp3_dir.mkdir(parents=True, exist_ok=True)
        self.sp3_npy_dir.mkdir(parents=True, exist_ok=True)
        self.svPos_dir.mkdir(parents=True, exist_ok=True)

    def _log(self, message):
        """
        Write a log message if logging is enabled.

        Args:
            message (str): The log message.
        """
        if self.logger:
            self.logger.write_log(message)
        else:
            print(message)

    def download_files(self):
        """
        Download SP3 and CLK files based on the date. 
        Saves downloaded file paths in self.
        """
        # Flag to see if we download rapid or final files
        is_final = (datetime.now() - self.epoch).days >= 13
        
        # Get dates for files to download
        days_to_download = [self.epoch + timedelta(days=i) for i in [-1, 0, 1]]
        
        # Save downloaded file names so we know which to read later
        self.sp3_file_list = []
        self.clk_file_list = []
    
        for day in days_to_download:
            self.sp3_file_list.append(self.download_sp3_or_clk(day, is_final, 'SP3', self.sp3_dir))
    
    
    def download_sp3_or_clk(self, day, is_final, file_type, dir_path):
        """
        Generalized function to download either SP3 or CLK files.
    
        Args:
            day (datetime): The day for which files should be downloaded.
            is_final (bool): Flag to indicate if final files should be downloaded.
            file_type (str): Type of the file ('SP3' or 'CLK').
            dir_path (Path): The directory where the file should be saved.
        """
        # initalise downloader class
        downloader = GNSSDownloader(day, dir_path, self.logger)
        # determine whether to call SP3R, SP3F, CLKR, CLKF
        download_method = getattr(downloader, f"{file_type.lower()}{('F' if is_final else 'R')}")
        # call correct download method, this downloads the files and returns the save path as str
        save_path = download_method()
        log_type = "final" if is_final else "rapid"
        self._log(f"Downloaded {log_type} {file_type} files for {day}.")
        return Path(save_path)

    def read_and_save_sp3_files(self):
        """
        Read SP3 and save as numpy array.
    
        """
        # Loop through the SP3 files and read and save each as a numpy array
        for sp3_file in self.sp3_file_list:
            sp3_reader = ReadSP3(sp3_file)
            sp3_data = sp3_reader.output2npy(self.sp3_npy_dir)
            if sp3_data is not None:
                self._log(f"Read and saved SP3 file {sp3_file} as a numpy array for {self.epoch}.")
    

    def interpolate_data(self):
        """
        Interpolate SP3 

        """

        # get file paths
        sp3_npy_files = [self.sp3_npy_dir / (path.stem + '.npy') for path in self.sp3_file_list]
        
        # Load in as numpy arrays
        sp3_arr_npy = [np.load(i, allow_pickle = True) for i in sp3_npy_files]
        
        # get important epochs, 1st epoch of middle and last day
        start_epoch = sp3_arr_npy[1][0][0] 
        end_epoch = sp3_arr_npy[2][0][0] 
        interval = self.interval #seconds
        
        # points of interpolation
        poi = np.arange(start_epoch, end_epoch, interval)
        
        # combine into one arr
        sp3_arr_comb = np.vstack([i for i in sp3_arr_npy])
        
        #ensure no duplicate rows
        unique_rows = np.unique(sp3_arr_comb[:, 0:3],axis=0, return_index=True)[1]
        sp3_arr_unique = sp3_arr_comb[unique_rows]
        
        all_sv_pos_arr = []
        
        for sys in self.system:
            
            # G:1 R:2 C:3 E:4 J:5
            sysNum = SysNames(sys).sys_num
            
            # Slice that system data
            sp3_sys = sp3_arr_unique[np.where(sp3_arr_unique[:,1] == sysNum)]
            
            # Get all available prn
            unique_prn = np.unique(sp3_sys[:,2]) 
            
            # Initialize a list to store the sub-arrays
            split_arrays = []
            
            # Iterate over each unique prn to filter rows and populate the list
            for value in unique_prn:
                
                # filter by PRN
                prn_arr = sp3_sys[sp3_sys[:, 2] == value]
                
                #Interpolate for each coordinate xyz
                prn_x = NI(prn_arr[:,0], prn_arr[:,3]).multiple_points(poi, 10)
                prn_y = NI(prn_arr[:,0], prn_arr[:,4]).multiple_points(poi, 10)
                prn_z = NI(prn_arr[:,0], prn_arr[:,5]).multiple_points(poi, 10)
                
                prn_list = [value for i in poi]
                sys_list = [sysNum for i in poi]
                
                # convert pandas timestamp in seconds into second of day
                timetags = pd.to_datetime(poi, unit='s')
                timestamps = [i.timestamp() for i in timetags]
                # sod = (timestamps.hour * 3600 + timestamps.minute * 60 + timestamps.second).to_numpy().astype(int)
                
                interp_prn_arr = np.array([
                    timestamps, 
                    sys_list,
                    prn_list, 
                    prn_x * 1000, # km to m, 
                    prn_y * 1000, # km to m, 
                    prn_z * 1000, # km to m
                    ])
                
                split_arrays.append(interp_prn_arr)
                
            # turn list into large array
            sv_pos_arr = np.hstack([i for i in split_arrays]) 
            self.save_sv_pos_to_npy(sv_pos_arr, sys)
            
            # Add the sv_pos_arr to the list of all arrays
            all_sv_pos_arr.append(sv_pos_arr)

        # Combine all sv_pos_arr arrays into one large array
        return_arr = np.hstack(all_sv_pos_arr).T
        
        return return_arr
                
    def save_sv_pos_to_npy(self, sv_pos_arr, sys):
        # get epoch info
        year = self.epoch.year
        doy = self.epoch.timetuple().tm_yday
            
        sv_pos_arr = sv_pos_arr.T
        #save array to svpos dir
        np.save(self.svPos_dir / f"sv_pos_sp3_{year}_{doy:03d}_{sys}.npy", sv_pos_arr )    
            
        self._log(f"Interpolated and saved SP3 for {sys} on {self.epoch.date()}.")
    

    def run(self):
        """
        Main method to run the entire workflow.

        Returns:
            None
        """
        self._log(f"Starting the workflow for {self.epoch}.")
        self._log("Beginning download process of SP3 files")
        
        self.download_files()
        self._log("Beginning conversion process of SP3 to .npy")
        self.read_and_save_sp3_files()
        self._log("Beginning process of SP3 interpolation")
        sv_pos_arr = self.interpolate_data()
        self._log(f"Completed the Find SV for {self.epoch}.")
        return sv_pos_arr
    
if __name__ == '__main__':

    from FileLogging.simple_logger  import SimpleLogger    
    # Sample usage (using placeholders)
    test_dir = Path(r"F:/test/sp3_test/")
    logger = SimpleLogger(test_dir / "test.log", print_to_console=True)
    find_sv_instance0 = FindSV(datetime(2021, 1, 1), ['G'], test_dir, logger = logger)
    find_sv_instance1 = FindSV(datetime(2021, 1, 2), ['G'], test_dir, logger = logger)
    find_sv_instance2 = FindSV(datetime(2021, 1, 3), ['G'], test_dir, logger = logger)
    find_sv_instance0.run()
    find_sv_instance1.run()
    find_sv_instance2.run()