# -*- coding: utf-8 -*-
"""
Created on Thu Oct  5 10:42:09 2023

@author: chcuk
"""

from typing import Union, Optional
from pathlib import Path
import numpy as np
import pandas as pd
from datetime import datetime
from time_transform import dt2float

class ReadCLK:
    def __init__(self, input_path: Union[Path, str]) -> None:
        """
        Initialize the ReadCLK class.

        Args:
            input_path (Path or str): Path to the CLK file.
            intvalCLK (int): Interval for the CLK file.
        """
        self.input_path = Path(input_path)
        self.sys_map = {'G': 1, 'R': 2, 'C': 3, 'E': 4, 'J':5}  # Dummy system mapping

    def read(self) -> pd.DataFrame:
        """
        Read the CLK file and return the data as a pandas DataFrame.

        Returns:
            pd.DataFrame: DataFrame containing CLK data.
        """
        buffer = []

        try:
            with open(self.input_path, 'r') as file:
                for line in file:
                    tokens = line.strip().split()
                    if tokens[0] == 'AS':
                        # Extract time elements, excluding fractional seconds
                        time_str = "".join(tokens[2:7]) + tokens[7].split('.')[0]
                        time_tag = datetime.strptime(time_str, "%Y%m%d%H%M%S")
                        
                        try:
                            sys = self.sys_map[tokens[1][0]]
                        except KeyError:
                            raise ValueError(f"Unknown system identifier: {tokens[1][0]}")
    
                        prn = int(tokens[1][1:])
                        clk = float(tokens[9])
                        clkSD = float(tokens[10]) if int(tokens[8]) > 1 else np.nan
                        buffer.append([time_tag, sys, prn, clk, clkSD])
    
    
            return pd.DataFrame(buffer, columns=["time", "sys", "prn", "clock", "clockSD"])

        except FileNotFoundError:
            print(f"File not found: {self.input_path}")
            return pd.DataFrame()
        except ValueError as ve:
            print(f"Value error: {ve}")
            return pd.DataFrame()
        except Exception as e:
            print(f"An unexpected error occurred: {e}")
            return pd.DataFrame()

    def output2npy(self, save_dir=None) -> Optional[np.ndarray]:
        """
        Read CLK data and save it as a numpy array if a directory is provided.

        Args:
            save_dir (Path or str, optional): Directory where the numpy array will be saved.

        Returns:
            np.ndarray: Numpy array containing CLK data or None if DataFrame is empty.
        """
        df = self.read()
        if df.empty:
            return None

        # Apply dt2float to the 'time' column
        df["time"] = df["time"].apply(dt2float)
        
        npy_array = df.to_numpy()
        
        if save_dir:
            save_path = Path(save_dir) / f"{self.input_path.stem}.npy"
            np.save(save_path, npy_array)
        return npy_array

#%%

# Test Cases for the class
if __name__ == "__main__":
    # Initialize a ReadSP3 object
    reader = ReadCLK(Path(r"C:/Users/chcuk/Work/Projects/I2GV2/test/CLK/GFZ0MGXRAP_20232700000_01D_30S_CLK.CLK"))

    # Test the read method
    df = reader.read()
    print(df.head())

    # # Test the output2npy method
    npy_data = reader.output2npy()
    print(npy_data[:5])