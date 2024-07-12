"""
Created on Tue Nov 22 13:32:56 2022

@author: chcuk
"""
import pandas as pd
import numpy as np
from pathlib import Path

class readSOP:
    """
    Reader for Swas output parameters file
    Note the system numbers are different to usual in this file and we must change:
    G - 1
    R - 2
    E - 4
    C - 8
    """
        
    COLUMN_NAMES = [
        "Date", "Time", "sys", "prn", "xs", "ys", "zs", "xr", "yr", "zr",
        "cdtr", "cdts", "rel", "dTrp", "dr1", "dr2", "dr3", "m_w", "m_h",
        "zhd", "az", "el", "y 1", "y 2", "cdion 1", "cdion 2", "dcb 1",
        "dcb 2", "bias 1", "bias 2", "fixFlag 1", "fixFlag 2", "refFlag 1",
        "refFlag 2"
    ]
    
    
    def __init__(self, inPath):
        # Check if the input is a string or a Path object and convert to Path object if it's a string
        self.inPath = inPath if isinstance(inPath, Path) else Path(inPath)
        
    def read(self):
        # Try reading the file, handle the FileNotFoundError if the file is not found
        try:
            data = pd.read_csv(self.inPath, sep=" ", header=None)
        except FileNotFoundError:
            print(f"File {self.inPath} not found.")
            return None

        # Set the column names and perform data transformations
        data.columns = self.COLUMN_NAMES
        
        # Remove 'FIX' from date values e.g 'FIX2022/10/29'
        data["Date"] = data["Date"].str[3:]
        for i in range(2, len(data.columns)):
            data[data.columns[i]] = data[data.columns[i]].astype(float)
            
        # Vectorized conversion of time to seconds of the day
        time_parts = data['Time'].str.split(':', expand=True).astype(float)
        data['Time'] = time_parts[0] * 3600 + time_parts[1] * 60 + time_parts[2]
        
        data = self.remap_systems(data)
            
        return data
    
    def remap_systems(self, df):
        # Mapping from old values to new values
        mapping_dict = {1: 1, 2: 2, 8: 3, 4: 4}

        df['sys'] = df['sys'].replace(mapping_dict)
        
        return df
    
    def output2NPY(self, outPath):
        # Convert DataFrame to numpy array and save it as a .npy file
        df = self.read()
        if df is not None:
            np.save(outPath, df.to_numpy())
            return True
        else:
            return False

#%%

if __name__ == '__main__':

    # how to call
    reader = readSOP(r"\\meetingroom\Integrity\I2Gnew\result\doy302\22336_intg.qoc")
    data = reader.read()
    # reader.output2NPY("/path/to/save/npy")
