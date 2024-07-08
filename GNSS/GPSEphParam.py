# -*- coding: utf-8 -*-
"""
GPS Ephemeris Parameter
Created on Thu Jun  4 2020
@author: Dr Hui Zhi
"""

from GNSS import Dummy
from time_transform import time_format as tf
import numpy as np
from datetime import datetime

class GPSEphParam():
    """
    A class for parsing and handling GPS ephemeris parameters from an array of observations.

    This class extracts satellite parameters necessary for GPS orbit determination and
    positioning calculations.

    Attributes:
    -----------
    brdc_block_data : list or array-like
        Contains data from one block of the broadcast ephemeris file.
        This contains one epoch and one satellites observations.
    block_start_idx : int
        The index in `brdc_block_data` from which to start extracting satellite information.

    Methods:
    --------
    __init__(self, brdc_block_data, block_start_idx):
        Initializes the GPSEphParam instance, extracting satellite parameters from `brdc_block_data`.
    
    res(self):
        Generates and returns a comprehensive list of the satellite's parameters for further processing or analysis.
    
    Parameters (Extracted and Calculated):
    --------------------------------------
    - Satellite system type
    - PRN number
    - Time of Clock (toc)
    - Observed time
    - Clock bias, drift, drift rate
    - Orbital parameters including IODE, Crs, Deltan, M0, Cuc, e, Cus, sqrtA, and many others.

    """

    dType_o = np.dtype([
        ('time', np.float64), ('sys', np.float64), ('PRN', np.float64), 
        ('description', np.float64)])
    
    def __init__(self, brdc_block_data, block_start_idx):
        self.brdc_block_data = brdc_block_data
        self.block_start_idx       = block_start_idx
                   
        # SV/EPOCH/SV CLK
        self.sat_sys = self.brdc_block_data[self.block_start_idx][0]
        self.prn     = int(self.brdc_block_data[self.block_start_idx][1:3])
        self.toc     = self.brdc_block_data[self.block_start_idx][4:8]
        self.obs_t   = self.brdc_block_data[self.block_start_idx][4:23]
        self.bias    = float(self.brdc_block_data[self.block_start_idx][23:42])
        self.drift   = float(self.brdc_block_data[self.block_start_idx][42:61])
        self.driftRate = float(self.brdc_block_data[self.block_start_idx][61:80])
        
        # Broadcast orbit - 1
        self.IODE   = float(self.brdc_block_data[self.block_start_idx+1][4:23])
        self.Crs    = float(self.brdc_block_data[self.block_start_idx+1][23:42])
        self.Deltan = float(self.brdc_block_data[self.block_start_idx+1][42:61])
        self.M0     = float(self.brdc_block_data[self.block_start_idx+1][61:80])
        
        # Broadcast orbit - 2
        self.Cuc   = float(self.brdc_block_data[self.block_start_idx+2][4:23])
        self.e     = float(self.brdc_block_data[self.block_start_idx+2][23:42])
        self.Cus   = float(self.brdc_block_data[self.block_start_idx+2][42:61])
        self.sqrtA = float(self.brdc_block_data[self.block_start_idx+2][61:80])
        
        # Broadcast orbit - 3
        self.Toe_SOW = float(self.brdc_block_data[self.block_start_idx+3][4:23])
        self.Cic     = float(self.brdc_block_data[self.block_start_idx+3][23:42])
        self.omega0  = float(self.brdc_block_data[self.block_start_idx+3][42:61])
        self.Cis     = float(self.brdc_block_data[self.block_start_idx+3][61:80])
        
        # Broadcast orbit - 4
        self.i0       = float(self.brdc_block_data[self.block_start_idx+4][4:23])
        self.Crc      = float(self.brdc_block_data[self.block_start_idx+4][23:42])
        self.omega    = float(self.brdc_block_data[self.block_start_idx+4][42:61])
        self.omegaDOT = float(self.brdc_block_data[self.block_start_idx+4][61:80])
        
        # Broadcast orbit - 5
        self.IDOT        = float(self.brdc_block_data[self.block_start_idx+5][4:23])
        self.CodesOnL2   = float(self.brdc_block_data[self.block_start_idx+5][23:42])
        self.Toe_GPSWeek = float(self.brdc_block_data[self.block_start_idx+5][42:61])
        self.L2PDataFlag = float(self.brdc_block_data[self.block_start_idx+5][61:80])
        
        # Broadcast orbit - 6
        self.SVaccuracy = float(self.brdc_block_data[self.block_start_idx+6][4:23])
        self.SVhealth   = float(self.brdc_block_data[self.block_start_idx+6][23:42])
        self.TGD        = float(self.brdc_block_data[self.block_start_idx+6][42:61])
        self.IODC       = float(self.brdc_block_data[self.block_start_idx+6][61:80])

        # Broadcast orbit - 7
        self.TransmissionTime = float(self.brdc_block_data[self.block_start_idx+7][4:23])
        self.FitInterval      = float(self.brdc_block_data[self.block_start_idx+7][23:42])
        # 
    def format_block_time_to_unixstamp(self):
        year = int(self.brdc_block_data[self.block_start_idx][4:8])
        month = int(self.brdc_block_data[self.block_start_idx][9:11])
        day = int(self.brdc_block_data[self.block_start_idx][12:14])
        hour = int(self.brdc_block_data[self.block_start_idx][15:17])
        minute = int(self.brdc_block_data[self.block_start_idx][18:20])
        second = int(self.brdc_block_data[self.block_start_idx][21:23])

        return datetime(year, month, day, hour, minute, second).timestamp()
        
    def res(self):
        # Obs time
        observation_time_unix_stamp  = self.format_block_time_to_unixstamp()
        # Reference time
        reference_time_unix_stamp = tf.GpsTime([self.Toe_GPSWeek, self.Toe_SOW, 0]).datetime.timestamp()

        resList = [
            observation_time_unix_stamp, Dummy.sys[self.sat_sys], self.prn,
            self.bias, self.drift, self.driftRate, self.IODE, self.Crs, 
            self.Deltan, self.M0, self.Cuc, self.e, self.Cus, self.sqrtA, 
            self.Toe_SOW, self.Cic, self.omega0, self.Cis, self.i0, self.Crc, 
            self.omega, self.omegaDOT, self.IDOT, self.CodesOnL2, 
            self.Toe_GPSWeek, self.L2PDataFlag, self.SVaccuracy, self.SVhealth,
            self.TGD, self.IODC, self.TransmissionTime, self.FitInterval, 
            reference_time_unix_stamp]
        
        
        return resList
    