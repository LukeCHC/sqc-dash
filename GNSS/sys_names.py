# -*- coding: utf-8 -*-
"""
Created on Thu May 10 2022

@author: chcuk
"""
from GNSS import GPS,GLO,BDS,GAL
import pandas as pd
import numpy as np

class SysNames:
    def __init__(self, sys):
        if isinstance(sys, str):
            if sys.lower() == "gps" or sys.lower() == "g":
                self.system = "GPS"
                self.sys = "G"
                self.sys_idx = 0
                self.sys_num = 1
            elif sys.lower() == "glo" or sys.lower() == "r" or sys.lower() == "glonass":
                self.system = "GLO"
                self.sys = "R"
                self.sys_idx = 1
                self.sys_num = 2
            elif sys.lower() == "bds" or sys.lower() == "c" or sys.lower() == "beidou":
                self.system = "BDS"
                self.sys = "C"
                self.sys_idx = 2
                self.sys_num = 3
            elif sys.lower() == "gal" or sys.lower() == "e" or sys.lower() == "galileo":
                self.system = "GAL"
                self.sys = "E"
                self.sys_idx = 3
                self.sys_num = 4
            elif sys.lower() == "sbas" or sys.lower() == "s":
                self.system = "SBAS"
                self.sys = "S"
                self.sys_idx = 4
                self.sys_num = 5
            elif sys.lower() == "qzss" or sys.lower() == "j":
                self.system = "QZSS"
                self.sys = "J"
                self.sys_idx = 5
                self.sys_num = 6
            elif sys.lower() == "irnss" or sys.lower() == "i":
                self.system = "IRNSS"
                self.sys = "I"
                self.sys_idx = 6
                self.sys_num = 7
            else:
                print("Not recognised GNSS system symbol")
        else:
            print("GNSS system initialisation failed")
            
    def isGPS(self):
        if (self.Sys == 'G'):
            flag = True
        else:
            flag = False
        return flag
        
    def isGLO(self):
        if (self.Sys == 'R'):
            flag = True
        else:
            flag = False
        return flag
    
    def isGAL(self):
        if (self.Sys == 'E'):
            flag = True
        else:
            flag = False
        return flag
    
    def isBDS(self):
        if (self.Sys == 'C'):
            flag = True
        else:
            flag = False
        return flag
    
    def isQZS(self):
        if (self.Sys == 'J'):
            flag = True
        else:
            flag = False
        return flag
    
    def isIRN(self):
        if (self.Sys == 'I'):
            flag = True
        else:
            flag = False
        return flag
    
    def isSBS(self):
        if (self.Sys == 'S'):
            flag = True
        else:
            flag = False
        return flag    
    
def sysNum2prn(sys, num):
    
    sys = int(sys)
    if sys not in [1,2,3,4]:
        raise Exception("sys not supported")
    
    # 1 2 3 4
    # G R C E
    lst = [GPS.MaxNoSV,GLO.MaxNoSV, BDS.MaxNoSV, GAL.MaxNoSV]
    
    if num > lst[sys-1]:
        raise Exception("SV num doesn't exist")
    
    prn = 0
    i = 0
    while i<sys-1:
        prn+= lst[i]
        i+=1
    prn+= num
    return prn
        

def prn2sys_num(prn, gpsst=32, glost=27, galst=36, qzsst=7, bdsst=64):
    """
    Convert PRN to system number and satellite number within that system.
    
    Args:
    - prn (int): The PRN number to convert.
    - gpsst (int, optional): Total satellites for GPS. Defaults to 32.
    - glost (int, optional): Total satellites for GLONASS. Defaults to 27.
    - galst (int, optional): Total satellites for Galileo. Defaults to 36.
    - qzsst (int, optional): Total satellites for QZSS. Defaults to 7.
    - bdsst (int, optional): Total satellites for BDS. Defaults to 64.
    
    Returns:
    - tuple: A tuple containing the system number (1-5) and the satellite number within that system.
    
    Raises:
    - Exception: If the PRN is outside the valid range.
    """
    # Ensure PRN is positive
    if prn <= 0:
        raise ValueError("PRN too low")
    
    # Satellite system identifiers and their total satellites
    systems = [(1, gpsst), (2, glost), (3, galst), (4, qzsst), (5, bdsst)]
    cumsum = 0  # Cumulative sum of satellites across systems
    
    for sys_id, total_sats in systems:
        if prn <= cumsum + total_sats:
            return sys_id, prn - cumsum
        cumsum += total_sats
    
    raise ValueError("PRN too high")

def prn2sysNum_vectorized(prn_array):
    # Create an array of cumulative maximums
    cumulative_maxs = np.array([GPS.MaxNoSV, GLO.MaxNoSV + 7, BDS.MaxNoSV, GAL.MaxNoSV]).cumsum()

    # Determine the satellite system for each PRN
    systems = np.select(
        [
            prn_array <= cumulative_maxs[0],
            prn_array <= cumulative_maxs[1],
            prn_array <= cumulative_maxs[2],
            prn_array <= cumulative_maxs[3]
        ], 
        [1, 2, 3, 4],
        default=np.nan  # Use NaN for invalid PRNs
    )

    # Calculate the satellite number within each system
    numbers = prn_array.copy()
    for sys in range(1, 5):
        mask = systems == sys
        offset = cumulative_maxs[sys - 2] if sys > 1 else 0
        numbers[mask] -= offset

    return systems, numbers

def name2sysNum(code):
    if type(code) != str:
        raise TypeError
    code = code.strip().upper()
    if len(code) != 3:
        raise Exception("Length must be 3")
    if code[0] == 'G':
        sys = 1
    elif code[0] == 'R':
        sys = 2
    elif code[0] == 'C':
        sys = 3
    elif code[0] == 'E':
        sys = 4
    prn = int(code[1:])
    return sys, prn

def split_prn_code(df, column_to_split):
    """ 
    This function splits a prn code column e.g. 'G11', 'C03' into its
    system and prn number columns i.e 1,11 3,3. 
    
    Args:
        df (DataFrame): The dataframe to process.
        column_to_split(str): The name of the column containing prn codes.
        
    Returns:
        (Dataframe): Returns the udpated dataframe with new columns.
    """
    
    
    # Mapping from letter to number
    letter_to_num = {'G': 1, 'R': 2, 'C': 3, 'E': 4}
    
    # Check if the column exists in the DataFrame
    if column_to_split not in df.columns:
        raise ValueError(f"Column '{column_to_split}' not found in DataFrame")

    # Extracting the first letter and mapping to a number
    df['sys'] = df[column_to_split].str[0].map(letter_to_num)

    # Extracting the two digit number
    df['num'] = df[column_to_split].str[1:].astype(int)
    
    # Remove old column
    df.drop(column_to_split, inplace=True, axis = 1)

    return df

def name2sysNum_vectorised(series):
    """
    Converts prn code e.g. 'G03' into 2 values system and number:
    G03 becomes 1, 3.
    Tried to use vectors calc instead of loops for processing speed, but it 
    is still quite slow, maybe a better method exists
    """
    
    
    if not isinstance(series, pd.Series):
        raise TypeError("Input must be a pandas Series")
    
    series = series.str.strip().str.upper()
    if not (series.str.len() == 3).all():
        raise Exception("All elements must have length 3")
    
    sys = pd.Series(index=series.index, dtype=int)
    sys[series.str[0] == 'G'] = 1
    sys[series.str[0] == 'R'] = 2
    sys[series.str[0] == 'C'] = 3
    sys[series.str[0] == 'E'] = 4

    prn = series.str[1:].astype(int)
    
    return sys, prn

def name2sysNum_series(prn_series):
    """
    Convert a Series of PRN strings to 'sys' and 'num' values.
    
    Parameters:
        prn_series (pd.Series): A Series containing PRN strings.
        
    Returns:
        pd.DataFrame: A DataFrame with two columns 'sys' and 'num'.
    """
    # Determine 'sys' based on the first character of 'prn'
    sys_series = prn_series.str[0].map({
        'G': 1,
        'R': 2,
        'C': 3,
        'E': 4
    })
    
    # Determine 'num' based on the remaining characters of 'prn'
    num_series = prn_series.str[1:].astype(int)
    
    # Combine 'sys' and 'num' into a DataFrame
    result_df = pd.DataFrame({
        'sys': sys_series,
        'num': num_series
    })
    
    return result_df

def sysNum2Name(sys,num):
    sys = int(sys)
    num = int(num)
    if sys == 1:
        code = 'G'
    elif sys == 2:
        code = 'R'
    elif sys == 3:
        code = 'C'
    elif sys == 4:
        code = 'E'
    else:
        raise Exception("Sys not accepted")
    code = code + "%02d"%num
    return code

def vectorized_sysNum2Name(sys, num):
    # Define system codes
    codes = np.array(['G', 'R', 'C', 'E'])
    
    # Handle NaN in sys: create a mask for valid indices, -1 for NaNs
    valid_sys_mask = ~np.isnan(sys)
    sys_int = np.where(valid_sys_mask, sys, -1).astype(int)
    
    # Subtract 1 to match zero-based indexing of arrays
    sys_index = sys_int - 1

    # Check if all sys values are valid (1 through 4)
    if np.any((sys_index < 0) & valid_sys_mask | (sys_index >= len(codes))):
        raise ValueError("Sys not accepted")

    # Replace invalid indices with NaN in sys_codes
    sys_codes = np.full(sys.shape, '', dtype='<U3')
    sys_codes[valid_sys_mask] = codes[sys_index[valid_sys_mask]]

    # Handle NaN in num: only convert non-NaNs to strings with leading zeros
    num_formatted = np.full(num.shape, '', dtype='<U3')
    valid_num_mask = ~np.isnan(num)
    num_formatted[valid_num_mask] = np.char.mod('%02d', num[valid_num_mask].astype(int))
    
    # Combine sys codes and formatted numbers, retaining NaN where input contained NaN
    combined = np.char.add(sys_codes, num_formatted)
    combined[~valid_sys_mask | ~valid_num_mask] = np.nan

    # Concatenate sys codes and formatted numbers
    return combined

def vectorized_sysNum2Name_old(sys, num):
    # old version cannot handle nan values
    # Define system codes
    codes = np.array(['G', 'R', 'C', 'E'])
    
    # Ensure sys is an integer array for indexing
    sys_int = sys.astype(int)
    
    # Subtract 1 to match zero-based indexing of arrays
    sys_index = sys_int - 1
    
    # Check if all sys values are valid (1 through 4)
    if np.any((sys_index < 0) | (sys_index >= len(codes))):
        raise ValueError("Sys not accepted")
    
    # Use sys as indexes to get corresponding codes
    sys_codes = codes[sys_index]
    
    # Format num with leading zeros
    num_formatted = np.char.mod('%02d', num.astype(int))
    
    # Concatenate sys codes and formatted numbers
    return np.core.defchararray.add(sys_codes, num_formatted)