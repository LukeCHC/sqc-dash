# -*- coding: utf-8 -*-
"""
Created on Fri Aug 19 16:03:34 2022

updated Mon 23 Jan

@author: chcuk
"""
# import pandas as pd
import numpy as np
from GNSS import GPSEphParam, GLOEphParam, GALEphParam, BDSEphParam
from pathlib import Path 


class ReadBRDC:
    def __init__(self, input_path):
        """
        inPath: Path to the BRDC file
        """
        self.input_path = Path(input_path)

        self.columns = [
                'epoch_observation',
                'system',
                'prn',
                'sv clock bias',  # Satellite clock bias
                'sv clock drift',  # Satellite clock drift
                'sv clock drift rate',  # Satellite clock drift rate
                'IODE',  # Issue of Data, Ephemeris
                'Crs',  # Amplitude of the Sine Harmonic Correction Term to the Orbit Radius
                'Delta n',  # Mean Motion Difference from Computed Value
                'M0',  # Mean Anomaly at Reference Time
                'Cuc',  # Amplitude of the Cosine Harmonic Correction Term to the Argument of Latitude
                'eccentricity',  # Eccentricity
                'Cus',  # Amplitude of the Sine Harmonic Correction Term to the Argument of Latitude
                'sqrtA',  # Square Root of the Semi-Major Axis
                'Toe',  # Reference Time Ephemeris (seconds into GPS week)
                'Cic',  # Amplitude of the Cosine Harmonic Correction Term to the Angle of Inclination
                'omega0',  # Longitude of Ascending Node of Orbit Plane at Weekly Epoch
                'Cis',  # Amplitude of the Sine Harmonic Correction Term to the Angle of Inclination
                'i0',  # Inclination Angle at Reference Time
                'Crc',  # Amplitude of the Cosine Harmonic Correction Term to the Orbit Radius
                'omega',  # Argument of Perigee
                'omega dot',  # Rate of Change of Right Ascension
                'IDOT',  # Rate of Change of Inclination Angle
                'codes on L2',  # Codes on L2 Channel
                'gps week',  # GPS Week Number
                'L2 P data flag',  # L2 P Data Flag
                'sv accuracy',  # Satellite User Range Accuracy
                'sv health',  # Satellite Health
                'TGD',  # Group Delay Differential
                'IODC',  # Issue of Data, Clock
                'transmission time',  # Transmission Time of Message
                'fit interval',  # Fit Interval in Hours
                'ref time',  # Reference Time
            ]

    def _get_end_of_header(self, brdc_lines):
        for index, line in enumerate(brdc_lines):
            if 'END OF HEADER' in line:
                return index
        return -1  # Return -1 if 'END OF HEADER' is not found in any line

        
    def read(self):

        with self.input_path.open("r") as f:
            brdc_lines_list = f.readlines()

        # get header data 
        header_end_idx = self._get_end_of_header(brdc_lines_list)
        header_list = brdc_lines_list[: (header_end_idx + 1)]
        for header_line in range(len(header_list) - 1, -1, -1):
            if "CORR" not in header_list[header_line]:
                del header_list[header_line]

        # get brdc data after end of header idx
        brdc_data_list = [x.strip("\n") for x in brdc_lines_list[header_end_idx + 1 :]]
        # remove empty lines
        brdc_data_list = [line for line in brdc_data_list if line.strip()]

        brdc_svs = list(set([x[:3] for x in brdc_data_list if x[:3] != " " * 3]))
        brdc_systems = list(set([x[0] for x in brdc_svs]))
        brdc_svs.sort()
        brdc_systems.sort()
        for sys in ["G", "R", "C", "E"]:
            if sys not in brdc_systems:
                raise ValueError(f"{sys}")
                    
                        
        g_data_list = np.array([])
        r_data_list = np.array([])
        c_data_list = np.array([])
        e_data_list = np.array([])
        for line_idx in range(len(brdc_data_list)):
            if brdc_data_list[line_idx][0] == "G":
                g_data_list = np.append(g_data_list , GPSEphParam(brdc_data_list, line_idx).res())
            if brdc_data_list[line_idx][0] == "R":
                r_data_list  = np.append(r_data_list , GLOEphParam(brdc_data_list, line_idx).res())
            if brdc_data_list[line_idx][0] == "C":
                c_data_list  = np.append(c_data_list , BDSEphParam(brdc_data_list, line_idx).res())
            if brdc_data_list[line_idx][0] == "E":
                e_data_list  = np.append(e_data_list , GALEphParam(brdc_data_list, line_idx).res())
        g_data_arr = g_data_list.reshape(-1, 33)
        r_data_arr = r_data_list.reshape(-1, 18)
        c_data_arr = c_data_list.reshape(-1, 30)
        e_data_arr = e_data_list.reshape(-1, 30)
        del g_data_list, r_data_list, c_data_list, e_data_list

        # header
        header_arr = np.full((4, 6), np.nan, dtype=object)
        header_arr[:, 0] = float(str(g_data_arr[0, 0])[:8] + "000000")
        header_arr[:, 1] = np.array(["BDUT", "GAGP", "GAUT", "GPUT"])
        for x in header_list:
            if x[:4] == "BDUT":
                header_arr[0, 2] = float(x[5:22].replace("D", "E"))
                header_arr[0, 3] = float(x[22:38].replace("D", "E"))
                header_arr[0, 4] = float(x[39:45].replace("D", "E"))
                header_arr[0, 5] = float(x[46:50].replace("D", "E"))
            if x[:4] == "GAGP":
                header_arr[1, 2] = float(x[5:22].replace("D", "E"))
                header_arr[1, 3] = float(x[22:38].replace("D", "E"))
                header_arr[1, 4] = float(x[39:45].replace("D", "E"))
                header_arr[1, 5] = float(x[46:50].replace("D", "E"))
            if x[:4] == "GAUT":
                header_arr[2, 2] = float(x[5:22].replace("D", "E"))
                header_arr[2, 3] = float(x[22:38].replace("D", "E"))
                header_arr[2, 4] = float(x[39:45].replace("D", "E"))
                header_arr[2, 5] = float(x[46:50].replace("D", "E"))
            if x[:4] == "GPUT":
                header_arr[3, 2] = float(x[5:22].replace("D", "E"))
                header_arr[3, 3] = float(x[22:38].replace("D", "E"))
                header_arr[3, 4] = float(x[39:45].replace("D", "E"))
                header_arr[3, 5] = float(x[46:50].replace("D", "E"))
            # NOTE some files use D instead of E for exponent so we replace

        return g_data_arr, r_data_arr, c_data_arr, e_data_arr, header_arr

                
if __name__ == "__main__":
    inPath = r"F:\test\BRDC00IGS_R_20210010000_01D_MN.rnx"
    ReadBRDC(inPath).read()