# -*- coding: utf-8 -*-
"""
Created on Thu Oct 19 11:58:34 2023

@author: chcuk
"""

# Based on the debugging output, it appears that the class might not be capturing the data correctly.
# The possible reason could be case sensitivity or extra spaces in the lines.
# Let's modify the class to address these issues.

from pathlib import Path
from GNSS import name2sysNum_series
import pandas as pd
import numpy as np

# Updating the class to handle varying numbers of data elements in the FIX-S lines
class ReadI2GRes:
    """
    Class to read .res files and extract relevant data into Pandas DataFrames.
    This version should be the final version of the reader class.
    """
    
    def __init__(self, file_path):
        """
        Initialize the class with the path to the .res file.
        
        Parameters:
            file_path (str): Path to the .res file.
        """
        self.file_path = Path(file_path)
        self.fix_p_rows = []
        self.fix_s_rows = []
        self.ref_sats = []
        
        # Defining columns based on the file format description
        self.fix_p_columns = ["epoch", "X", "Y", "Z", "zhd", "zwd", "zwd_mod", "dtrG", "dtrE", "dtrC"]
        self.fix_s_columns = [
            "epoch", "prn", "bias1", "bias2", "el", "trop_est", "trop_mod", "iono_est", "iono_mod", "ionoestsd", "ionomodsd",
            "res_oc1", "res_oc2", "res_gf", "res_if", "reg_trop", "reg_iono", 
            "ppprtk1", "ppprtk2", "ref_g", "ref_e", "ref_c2", "ref_c3"]
        
    
    def _read_file(self):
        """
        Read the .res file and populate the fix_p_data and fix_s_data lists.
        This method outputs the ref satellites
        """
        epoch_info = None
        
        try:
            with self.file_path.open("r") as file:
                for line in file:
                    line = line.strip()
                    
                    # Skip comments and empty lines
                    if line.startswith("/*") or not line:
                        continue
                    
                    # Extract epoch information
                    if "epoch:" in line.lower():
                        epoch_info = line.lower().split("epoch:")[1].strip()
                        continue
                    
                    if "reference sat:" in line.lower():
                        # bds: 1-16 bds2 17-46 bds3
                        # dynamically handle the ref sats 
                        ref_sats = line.split()[2:6]
                        refG, refE, refC2, refC3 = np.nan, np.nan, np.nan, np.nan
                        for sat in ref_sats:
                            if sat[0] == 'G':
                                refG = sat
                            if sat[0] == 'E':
                                refE = sat
                            if sat[0] == 'C' and int(sat[1:3]) <= 16:
                                refC2 = sat
                            if sat[0] == 'C' and int(sat[1:3]) > 16:
                                refC3 = sat
                            
                        self.ref_sats.append([refG, refE, refC2, refC3])
                    
                    # Extract FIX-P data
                    if "fix-p" in line.lower():
                        data = line.split(":")[1].strip().split()
                        fix_p_row_data = [epoch_info] + data
                        self.fix_p_rows.append(fix_p_row_data)
                    
                    # Extract FIX-S data
                    if "sat " in line.lower():
                        data = line.split()[1:]
                        row_data = [epoch_info] + data + [refG, refE, refC2, refC3]
                        
                        # Handle varying numbers of data elements
                        while len(row_data) < len(self.fix_s_columns):
                            row_data.append(None)
                            
                        self.fix_s_rows.append(row_data)
                        continue

        except Exception as e:
            print(f"Error reading file: {e}")
    def get_fix_p_data(self):
        """
        Retrieve the FIX-P data as a Pandas DataFrame.
        
        Returns:
            DataFrame: FIX-P data.
        """
        self._read_file()
        return pd.DataFrame(self.fix_p_rows, columns=self.fix_p_columns)
    
    def get_fix_s_data(self):
        """
        Retrieve the FIX-S data as a Pandas DataFrame.
        this function is a newer version that also returns new paramaters
        added to res files.
        
        new params: 'modsd', 'estsd', 'ref sats'
        
        Returns:
            DataFrame: FIX-S data.
        """
        
        self.new_fix_data = []
        self._read_file()
        
        df = pd.DataFrame(self.fix_s_rows, columns=self.fix_s_columns)
        df[["ref_g", "ref_e", "ref_c2", "ref_c3"]] = df[["ref_g", "ref_e", "ref_c2", "ref_c3"]].map(lambda x: int(x[1:]) if pd.notna(x) else x) # note this req pandas 2.1.0
        # df[["ref_g", "ref_e", "ref_c2", "ref_c3"]] = df[["ref_g", "ref_e", "ref_c2", "ref_c3"]].map(lambda x: x[1:]) # note this req pandas 2.1.0
        
        
        result_df = name2sysNum_series(df['prn'])
        df = pd.concat([df, result_df], axis=1)
        df.drop(['prn'], axis=1, inplace=True)
        
        # Select all columns except selected ones here
        columns_to_convert = df.columns.difference(['epoch','sys', 'num' 'az', 'el', "ref_g", "ref_e", "ref_c"])
        
        df['epoch'] = pd.to_datetime(df['epoch'])
        
        # Convert selected columns to float
        df[columns_to_convert] = df[columns_to_convert].astype(float)
        
        df = df.reindex(columns = ['epoch', 'sys','num', "bias1", "bias2", "el", 
                                   "trop_est", "trop_mod", "iono_est", 
                                   "iono_mod", "ionoestsd", "ionomodsd",
                                   "res_oc1", "res_oc2", "res_gf", "res_if", 
                                   "reg_trop", "reg_iono", "ppprtk1", 
                                   "ppprtk2", "ref_g", "ref_e", "ref_c2", "ref_c3"])

        return df

    def read(self):
        return self.get_fix_p_data(), self.get_fix_s_data()

#%%

# test code

if __name__ == '__main__':
    # Testing the class with the uploaded file
    reader = ReadI2GRes(r"\\meetingroom\Integrity\SWASQC\res_334\DSHZ_2023334_intg.res")
    fix_p_data = reader.get_fix_p_data()
    fix_s_data = reader.get_fix_s_data()
    
    # # Show sample data
    print(fix_p_data.head())
    print(fix_s_data.head())
