"""
Created on Tue Sep 26 15:27:57 2023

@author: chcuk
"""

# Improved readIono class
import pandas as pd
import numpy as np

class ReadIono:
    def __init__(self, fPath):
        self.fPath = fPath  # ionosphere input file path

    def read(self):
        with open(self.fPath) as f:
            data = f.readlines()

        block_idx = [i for i in range(len(data)) if '#' in data[i]]
        block_headers = [data[i] for i in block_idx]  # get block headers

        time_strings = [i[14:22] for i in block_headers]

        # Vectorized conversion of time to seconds of the day
        time_parts = np.array([i.split(':') for i in time_strings]).astype(int)
        sod = time_parts[:,0] * 3600 + time_parts[:,1] * 60 + time_parts[:,2]

        refPointFlag = [i[27:28] for i in block_headers]  # 1 earth lon lat, 0 ipp lon lat
        modelTypeFlag = [i[29:30] for i in block_headers] # 1 = slant model 2 = vertical model

        # Used list slicing instead of deleting elements
        blocks = [data[block_idx[i] + 1: block_idx[i+1]-1] for i in range(len(block_idx) - 1)]  # separate into blocks per timetag
        blocks.append(data[block_idx[-1]+1:data.index(data[-1])])  # add last block

        arr = []

        for i in range(len(blocks)):
            for j in blocks[i]:
                line = j.split()
                # Used list slicing instead of deleting elements
                line = line[:11]  # remove useless info
                line.insert(0, sod[i])
                line.insert(1, refPointFlag[i])
                line.insert(2, modelTypeFlag[i])
                arr.append(line)

        df = pd.DataFrame(arr)
        # Used list slicing for column selection
        df = df.iloc[:, [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 11, 13]]
        df.columns = ["SoD", "refFlag", "modelFlag", "prn", "a1", "a2", "a3", "a4", "a5", "a6", "Ele", "Sigma"] 

        return df

    def output2NPY(self, outPath):
        df = self.read()
        # Corrected the np.save arguments
        np.save(outPath, np.array(df))
        return True

#%%

# test

if __name__ == '__main__':
    from datetime import datetime
    st = datetime.now()
    df2 = ReadIono(r"\\meetingroom\Integrity\SHAtmos\PPPRTK\Iono_Model_030.518-120.655_10_29_00_IONOMODEL.log").read()
    end = datetime.now()
    print(f"r: {end-st}")    
    