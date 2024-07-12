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
        
        # Defining columns based on the file format description
        self.fix_p_columns = ["epoch", "refG", "refE", "refC", "X", "Y", "Z", "zhd", "zwd", "zwd_mod", "dtrG", "dtrE", "dtrC"]
        self.fix_s_columns = [
            "epoch", "prn", "bias1", "bias2", "el", "trop_est", "trop_mod", "iono_est", "iono_mod", "ionoestsd", "ionomodsd",
            "res_oc1", "res_oc2", "res_gf", "res_if", "reg_trop", "reg_iono", 
            "ppprtk1", "ppprtk2"]
        self.new_fix_columns = [
            "epoch", "prn", "bias1", "bias2", "el", "trop_est", "trop_mod", "iono_est", "iono_mod", "ionoestsd", "ionomodsd",
            "res_oc1", "res_oc2", "res_gf", "res_if", "reg_trop", "reg_iono", 
            "ppprtk1", "ppprtk2", "ref_g", "ref_e", "ref_c"]
        
    
    def _read_file(self):
        """
        Read the .res file and populate the fix_p_data and fix_s_data lists.
        This method outputs the ref satellites
        """
        epoch_info = None
        
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
                
                # Extract FIX-P data
                if "fix-p" in line.lower():
                    data = line.split(":")[1].strip().split()
                    fix_p_row_data = [epoch_info] + data
                    self.fix_p_rows.append(fix_p_row_data)
                    
                    refG = fix_p_row_data[1]
                    refE = fix_p_row_data[2]
                    refC = fix_p_row_data[3]
                    continue
                
                # Extract FIX-S data
                if "sat" in line.lower():
                    data = line.split()[1:]
                    row_data = [epoch_info] + data + [refG, refE, refC]
                    
                    # Handle varying numbers of data elements
                    while len(row_data) < len(self.fix_s_columns):
                        row_data.append(None)
                        
                    self.new_fix_data.append(row_data)
                    continue
    
    def _read_file_old(self):
        """
        Read the .res file and populate the fix_p_data and fix_s_data lists.
        This is the old method that doesnt output the ref satellites or single difference values
        """
        epoch_info = None
        
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
                
                # Extract FIX-P data
                if "fix-p" in line.lower():
                    data = line.split(":")[1].strip().split()
                    row_data = [epoch_info] + data
                    self.fix_p_rows.append(row_data)
                    continue
                
                # Extract FIX-S data
                if "sat" in line.lower():
                    data = line.split()[1:]
                    row_data = [epoch_info] + data
                    
                    # Handle varying numbers of data elements
                    while len(row_data) < len(self.fix_s_columns):
                        row_data.append(None)
                        
                    self.fix_s_rows.append(row_data)
                    continue
    
    def get_fix_p_data(self):
        """
        Retrieve the FIX-P data as a Pandas DataFrame.
        
        Returns:
            DataFrame: FIX-P data.
        """
        self._read_file_old()
        return pd.DataFrame(self.fix_p_rows, columns=self.fix_p_columns)
    
    def get_fix_s_data(self):
        """
        Retrieve the FIX-S data as a Pandas DataFrame.
        
        Returns:
            DataFrame: FIX-S data.
        """
        self._read_file_old()
        df = pd.DataFrame(self.fix_s_rows, columns=self.fix_s_columns)
        result_df = name2sysNum_series(df['prn'])
        df = pd.concat([df, result_df], axis=1)
        df.drop(['prn', 'ionomodsd','ionoestsd'], axis=1, inplace=True)
        
        # Select all columns except 'epoch'
        columns_to_convert = df.columns.difference(['epoch', 'az', 'el'])
        
        df['epoch'] = pd.to_datetime(df['epoch'])
        
        # Convert selected columns to float
        df[columns_to_convert] = df[columns_to_convert].astype(float)
        
        
        df = df.reindex(columns = ['epoch', 'sys', 'num', 'el',
                                   "bias1", "bias2",
                                   "trop_est", "trop_mod", 
                                   "iono_est", "iono_mod",
                                   "res_oc1", "res_oc2", "res_gf", "res_if", 
                                   "reg_trop", "reg_iono", "ppprtk1", "ppprtk2"])

        return df
    
    def get_new_fix_data(self):
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
        
        df = pd.DataFrame(self.new_fix_data, columns=self.new_fix_columns)
        df[["ref_g", "ref_e", "ref_c"]] = df[["ref_g", "ref_e", "ref_c"]].map(lambda x: x[1:]) # note this req pandas 2.1.0
        
        
        result_df = name2sysNum_series(df['prn'])
        df = pd.concat([df, result_df], axis=1)
        df.drop(['prn'], axis=1, inplace=True)
        
        # Select all columns except 'epoch'
        columns_to_convert = df.columns.difference(['epoch', 'az', 'el', "ref_g", "ref_e", "ref_c"])
        
        df['epoch'] = pd.to_datetime(df['epoch'])
        
        # Convert selected columns to float
        df[columns_to_convert] = df[columns_to_convert].astype(float)

        
        df = df.reindex(columns = ['epoch', 'sys','num', "bias1", "bias2", "el", 
                                   "trop_est", "trop_mod", "iono_est", 
                                   "iono_mod", "ionoestsd", "ionomodsd",
                                   "res_oc1", "res_oc2", "res_gf", "res_if", 
                                   "reg_trop", "reg_iono", "ppprtk1", 
                                   "ppprtk2", "ref_g", "ref_e", "ref_c"])

        return df

    def read(self):
        return self.get_fix_p_data(), self.get_fix_s_data()

#%%

# test code

if __name__ == '__main__':
    # Testing the class with the uploaded file
    reader = ReadI2GRes(r"\\meetingroom\Integrity\SWASQC\res20240122\CMDN_2024002_intg.res")
    # fix_p_data = reader.get_fix_p_data()
    # fix_s_data = reader.get_fix_s_data()
    new_fix_data = reader.get_new_fix_data()
    
    # # Show sample data
    # fix_p_data.head(), fix_s_data.head()
