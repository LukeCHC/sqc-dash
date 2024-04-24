import numpy as np
from datetime import datetime
import streamlit as st

def extract_eph_attributes(data):
    # Initialize an empty dictionary to store attribute values
    attributes = {}
    
    # Loop through each attribute in the dir() of the data object
    for attr in dir(data):
        # Ignore private and built-in attributes/methods
        if not attr.startswith('__'):
            # Try to get the value of the attribute and add it to the dictionary
            try:
                value = getattr(data, attr)
                attributes[attr] = value
            except AttributeError:
                print(f"Attribute {attr} could not be accessed")
    
    return attributes

def eph_attributes_to_arr(gps_eph_data):

    data_list = []
    for i in range(32):
        try:
            gps_prn_data = gps_eph_data[i]
            gps_prn_data = extract_eph_attributes(gps_prn_data)

            eph_parameters = {
            'obs_unix_timestamp':datetime.now().timestamp(), 
            'system':1,
            'prn': int(gps_prn_data['sat_id'][1:]),
            'bias': np.nan,
            'drift': np.nan,
            'driftRate': np.nan ,
            'iode': gps_prn_data['iode'],
            'crs': gps_prn_data['crs'],
            'delta_n':gps_prn_data['dn'] ,
            'mean_anomaly_0': gps_prn_data['m0'], 
            'cuc': gps_prn_data['cuc'], 
            'e': gps_prn_data['ecc'], 
            'cus': gps_prn_data['cus'], 
            'sqrt_a': gps_prn_data['root_a'] ,
            'toe_sow': gps_prn_data['toe'] ,
            'cic': gps_prn_data['cic'] ,
            'omega_0': gps_prn_data['omega_0'] ,
            'cis': gps_prn_data['cis'] ,
            'i_0': gps_prn_data['i0'] ,
            'crc': gps_prn_data['crc'] ,
            'omega': gps_prn_data['omega'] ,
            'omega_dot': gps_prn_data['omega_dot'],
            'i_dot' : gps_prn_data['idot']
            }
            

            values = eph_parameters.values()

            data_list.append(list(eph_parameters.values()))
        except Exception as e:
            # data_list.append([None] * 23)
            st.info(f"G{int(i+1):02d} not available")

    gps_eph_arr = np.array(data_list)
    return gps_eph_arr