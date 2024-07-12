# -*- coding: utf-8 -*-
"""
Created on Tue Sep 26 15:27:57 2023

@author: chcuk
"""

# Improved readTropo class
import pandas as pd
import numpy as np
from pathlib import Path
from datetime import datetime

from GNSS import prn2sysNum_vectorized

class readTrop:
    def __init__(self, fPath):
        self.fPath = Path(fPath)  # troposphere input file path

    def read(self):
        
        try:
        
            data = []
            with open(self.fPath) as file:
                for line in file:
                    # Remove the leading '#' and strip any leading/trailing whitespaces
                    line = line.lstrip('#').strip()
                    parts = line.split()
    
                    # Extract the required fields
                    date = parts[1]
                    time = parts[2]
                    lat = parts[4]
                    lon = parts[5]
                    alt = parts[6]
                    a1 = parts[8]
                    a2 = parts[9]
                    a3 = parts[10]
    
                    # Combine extracted fields into a list
                    cor_data = [date, time, lat, lon, alt, a1, a2, a3]
    
                    # Add to the data list
                    data.append(cor_data)
    
            # Convert the list to a DataFrame
            columns = ['Date', 'Time', 'Lat', 'Lon', 'Alt', 'a1', 'a2', 'a3']
            df = pd.DataFrame(data, columns=columns)
            
            # result = prn2sysNum_vectorized(df['Sat'].values.astype(int))
            # df = df.join(result)
            
            # df.drop(columns = ['Unknown','Sat'], inplace=True)
            
            df[['Lon', 'Lat', 'Alt', 'a1', 'a2', 'a3']] = df[['Lon', 'Lat', 'Alt', 'a1', 'a2', 'a3']].astype(float)
            
        except Exception as e:
            print(f"Coultn't read file {self.fPath} due to {e}")
        
        return df
    
    def str2sod(self, string):
        hour = float(string[:2])
        mins = float(string[3:5])
        secs = float(string[6:8])
        return 3600 * hour + 60 * mins + secs

    def output2NPY(self, outPath):
        
        outPath = Path(outPath)
        
        df = self.read()
        
        try:
            date = self.fPath.stem.split('_')[3:5] 
            grid = self.fPath.stem.split('_')[2]
            df['SoD']= df['Time'].apply(self.str2sod)
            df.drop(columns = ['Date', 'Time'], inplace=True)
            #####NOTE currently year not included in fName
            date = datetime(2022,int(date[0]), int(date[1]))
            #############################################
            
            doy = date.timetuple().tm_yday
    
            save_name = f"Trop_{grid}_{date.year}_{doy}.npy"
            
            # Corrected the np.save arguments
            np.save(outPath/ save_name, np.array(df))
        
        except Exception as e:
            print(f"Couldn't output {self.fPath} to npy due to {e}")
        
        return True
    
#%%

if __name__ == '__main__':
    fPath = r"\\meetingroom\Integrity\SHAtmos\PPPRTK\Trop_Model_029.500-119.500_10_29_00_TROPMODEL.log"
    out = r"C:\Users\chcuk\OneDrive\Desktop\test"
    # test = readTrop(fPath).read()
    test = readTrop(fPath).output2NPY(out)
