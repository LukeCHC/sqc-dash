# -*- coding: utf-8 -*-
"""
Created on Wed Oct  4 11:52:02 2023

@author: chcuk
"""

from datetime import datetime
from pathlib import Path
import numpy as np
import pandas as pd
# from TimeTrans import dt2float

from typing import  Union, Optional

class ReadSP3:
    def __init__(self, input_path: Union[Path, str]) -> None:
        """
        Initialize the ReadSP3 class.

        Args:
            input_path (Path or str): Path to the SP3 file.
        """
        self.input_path = Path(input_path)

    def read(self) -> pd.DataFrame:
        """
        Read the SP3 file and return the data as a pandas DataFrame.

        Returns:
            pd.DataFrame: DataFrame containing SP3 data.
        """
        buffer = []
        sys_map = {'G': 1, 'R': 2, 'C': 3, 'E': 4, 'J': 5}  # Dummy system mapping

        try:
            with open(self.input_path, 'r') as file:
                for line in file:
                    tokens = line.strip().split()
                    if tokens[0] == '*':
                        # Zero-pad each time element and then split it at the dot
                        time_elements = [str(token).zfill(2).split('.')[0] for token in tokens[1:7]]
                        time_str = "".join(time_elements)
                        time_tag = datetime.strptime(time_str, "%Y%m%d%H%M%S")
                    elif tokens[0][0] == 'P':
                        try:
                            sys = sys_map[tokens[0][1]]
                        except KeyError:
                            raise ValueError(f"Unknown system identifier: {tokens[0][1]}")

                        prn = int(tokens[0][2:])
                        x, y, z, clk = map(float, tokens[1:5])
                        buffer.append([time_tag, sys, prn, x, y, z, clk])

            return pd.DataFrame(buffer, columns=["time", "sys", "prn", "x", "y", "z", "clock"])

        except FileNotFoundError:
            print(f"File not found: {self.input_path}")
            return pd.DataFrame()
        except ValueError as ve:
            print(f"Value error: {ve}")
            return pd.DataFrame()
        except Exception as e:
            print(f"An unexpected error occurred: {e}")
            return pd.DataFrame()

    def output2npy(self, save_dir = None) -> Optional[np.ndarray]:
        """
        Read SP3 data and save it as a numpy array if a directory is provided.

        Args:
            save_dir (Path or str): Directory where the numpy array will be saved.

        Returns:
            np.ndarray: Numpy array containing SP3 data or None if DataFrame is empty.
        """
        df = self.read()
        if df.empty:
            return None


        # old method was to use dt2 float, a useless object that has no 
        # purpose and was only used for storing in numpy
        # use timestamp instead
        # Apply dt2float to the 'time' column
        # df['time'] = df['time'].apply(dt2float)
        
        #convert pandas timestamp to seconds
        df['time'] = df['time'].astype('int64')//10**9
        
        #to convert back to datetime pd.to_datetime(df['unix_time_column'], unit='s')
        
        #convert to numpy
        npy_array = df.to_numpy()
        
        #save if directory provided
        if save_dir:
            save_path = Path(save_dir) / f"{self.input_path.stem}.npy"
            np.save(save_path, npy_array)
        return npy_array

    def read_multi(self, path_list: [Path]) -> pd.DataFrame:
        """
        Read multiple SP3 files and concatenate their data.
    
        Args:
            path_list ([Path]): List of Paths to SP3 files.
            
        Returns:
            pd.DataFrame: DataFrame containing concatenated SP3 data.
        """
        
        # Include self.input_path only if it's not in path_list
        dfs = [self.read()] if self.input_path not in path_list else []  
        
        # Loop over each path in the list to read and append their data
        for path in path_list:
            self.input_path = path  # Update the input path
            dfs.append(self.read())  # Read and append the DataFrame to the list
        
        # Concatenate all dataframes and reset the index
        return pd.concat(dfs, ignore_index=True)

#%%

# Test Cases for the class
if __name__ == "__main__":
    # Initialize a ReadSP3 object
    reader = ReadSP3(Path(r"C:\Users\chcuk\Work\Projects\I2GV2\test\GFZ0MGXRAP_20232700000_01D_05M_ORB.SP3"))

    # Test the read method
    df = reader.read()
    print(df.head())

    # # Test the output2npy method
    npy_data = reader.output2npy()
    print(npy_data[:5])

    # # Test the read_multi method
    # multi_df = reader.read_multi([Path("path/to/sp3/file1"), Path("path/to/sp3/file2")])
    # print(multi_df.head())
