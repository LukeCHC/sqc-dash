"""
Created on Tue Nov 22 13:32:56 2022

@author: chcuk
"""
import pandas as pd
import numpy as np
from pathlib import Path
from GNSS import split_prn_code

class ReadCHK:
    """
    Class to read .chk files and extract relevant data into Pandas DataFrames.
    """
    
    def __init__(self, file_path):
        """
        Initialize the class with the path to the .chk file.
        
        Parameters:
            file_path (str): Path to the .chk file.
        """
        self.file_path = Path(file_path)
        self.fix_p_rows = []
        self.fix_s_rows = []
        
        # Defining columns based on the file format description
        self.fix_p_columns = ["epoch", 'staX', 'staY', 'staZ', 'tideCor0', 'tideCor1', 'tideCor2', 'na1' ,'na2', 'na3']
        self.fix_s_columns = ['epoch', 'prn', 'satX', 'satY', 'satZ', 'az', 'mapdry', 'mapwet', 'corrobsf1',
                                   'corrobsf2', 'dtr', 'satclk', 
                                   'gravity', 'freq1', 'freq2', 
                                   'ionfact1', 'ionfact2', 'tropgrid', 'ionogrid']
        
        self._read_file()
    
    def _read_file(self):
        """
        Read the .chk file and populate the fix_p_data and fix_s_data lists.
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
        return pd.DataFrame(self.fix_p_rows, columns=self.fix_p_columns)
    
    def get_fix_s_data(self):
        """
        Retrieve the FIX-S data as a Pandas DataFrame.
        
        Returns:
            DataFrame: FIX-S data.
        """
        
        df = pd.DataFrame(self.fix_s_rows, columns=self.fix_s_columns)
        df = split_prn_code(df, 'prn')
        df = df.reindex(columns = ['epoch', 'sys', 'num', 'satX', 'satY', 'satZ',
                                   'az', 'mapdry', 'mapwet', 'corrobsf1',
                                   'corrobsf2', 'dtr', 'satclk', 
                                   'gravity', 'freq1', 'freq2', 
                                   'ionfact1', 'ionfact2', 'tropgrid', 'ionogrid'])

        return df

    def read(self):
        return self.get_fix_p_data(), self.get_fix_s_data()


class readCHK_old:
    def __init__(self, inPath):
        self.inPath = inPath
        
    def read(self):
        data = pd.read_csv(self.inPath,
            sep=" ",
            header=None,
        )

        data.columns = [
            "Date",
            "Time",
            "sys",
            "prn",
            "lRaw",
            "snr",
            "pRaw",
            "dop",
            "lMod",
            "y",
            "dants",
            "dantr",
            "phw",
            "zwd",
            "m_w",
            "m_h",
            "zhd",
            "dtrp",
            "az",
            "el"]

        # data["fq"] = [x[3] for x in data.iloc[:, 0]]
        data.iloc[:, 0] = [x[4:] for x in data.iloc[:, 0]]
        data.iloc[:, 2:] = data.iloc[:, 2:].astype(float)
        return data 
    
    
    def output2NPY(self, outPath):
        f = self.read()
        f = np.array(f)
        np.save(outPath, f)
        return True
    
#%%

if __name__ == '__main__':
    file = Path(r"\\meetingroom\Integrity\I2Gnew\result\doy302\JSCS_22336_intg.chk")
    p_data, s_data = ReadCHK(file).read()