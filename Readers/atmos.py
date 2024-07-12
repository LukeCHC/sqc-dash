# -*- coding: utf-8 -*-
"""
Created on Fri Nov 11 14:15:57 2022

@author: chcuk
"""

import pandas as pd
import numpy as np

class readIono:
    def __init__(self, fPath):
        self.fPath = fPath  # ionosphere input file path

    def read(self):
        with open(self.fPath) as f:
            data = f.readlines()

        blockIdx = [i for i in range(len(data)) if '#' in data[i]]
        blkHeads = [data[i] for i in blockIdx]  # get block headers
       
        tt = [pd.to_datetime(i[5:27], yearfirst=True) for i in blkHeads]
        refPointFlag = [i[27:28] for i in blkHeads]  # 1 earth lon lat, 0 ipp lon lat
        modelTypeFlag = [i[29:30] for i in blkHeads] # 1 = slant model 2 = vertical model
        blocks = [data[blockIdx[i] + 1: blockIdx[i+1]-1]
                  for i in range(len(blockIdx) - 1)]  # seperate into blocks per timetag
        blocks.append(data[blockIdx[-1]+1:data.index(data[-1])])  # add last block

        arr = []

        for i in range(len(blocks)):
            for j in blocks[i]:
                line = j.split()
                del line[11:]  # remove useless info
                line.insert(0, tt[i])
                line.insert(1, refPointFlag[i])
                line.insert(2, modelTypeFlag[i])
                arr.append(line)

        df = pd.DataFrame(arr)
        df = df.drop([10,12], axis=1)
        df.columns = ["Timetag", "refFlag", "modelFlag", "prn", "a1", "a2", "a3", "a4", "a5", "a6",
                      "Ele", "Sigma"] 

        return df

    def output2NPY(self, outPath):
        df = np.array(self.read())
        np.save(df, outPath)
        return True


class readTropo:
    def __init__(self, fPath):
        self.fPath = fPath  # ionosphere input file path

    def read(self):
        with open(self.fPath) as f:
            data = f.readlines()

        data = [line.split() for line in data]
        df = pd.DataFrame(data)
        df = df[[1, 2, 3, 4, 5, 6, 7, 8, 9, 10]]
        df.columns = ["Date", "Time", "flag", "lat", "lon", "alt",
                      "flag2", "a1", "a2", "a3"]

        return df

    def output2NPY(self, outPath):
        df = np.array(self.read())
        np.save(df, outPath)
        return True
