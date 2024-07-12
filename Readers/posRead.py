# -*- coding: utf-8 -*-
"""
Created on Wed Sep  6 13:49:51 2023

@author: chcuk
"""

import pandas as pd

def read_pos(file_path):
    
    
    # Define the column names based on the observed structure of the file
    column_names = [
        'Date', 'Time', 'x-ecef(m)', 'y-ecef(m)', 'z-ecef(m)',
        'Q', 'ns', 'sdx(m)', 'sdy(m)', 'sdz(m)', 'sdxy(m)', 'sdyz(m)',
        'sdzx(m)', 'age(s)', 'ratio', 'nw', 'nn'
    ]
    
    # Read the file into a DataFrame using a regular expression as the delimiter
    # Skip the first two rows as they contain metadata and irregularly formatted headers
    df = pd.read_csv(file_path, delimiter=r'\s+', skiprows=2, names=column_names)
    
    return df

