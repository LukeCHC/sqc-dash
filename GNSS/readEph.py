# -*- coding: utf-8 -*-
"""
Read Ephemeris
Created on Sat Aug 22 2020
@author: Dr Hui Zhi
"""

# import INI_OCE as INI
from INI import readFolder
from TOOLS import decompress
import re
import os

class readEph():
    def __init__(self, config):
        """
        Parameters
        ----------
        config : dict
            variable of read ini file.
        """
        self.config = config
        
    def path(self):
        readfolder = readFolder(self.config)
        ephPath = []
        for l in readfolder[0]:
            if bool(re.match('.\d\dp', os.path.splitext(l)[1], re.I)):
                ephPath.append(l)
            elif '_MN.rnx' in l:
                ephPath.append(l)
        ephName = []
        for l in readfolder[2]:
            if bool(re.match('.\d\dp', l.split('.')[1], re.I)):
                ephName.append(l)
            elif '_MN.rnx' in l:
                ephName.append(l)
        # gz decompress
        ephNameGZ = [i for i in range(len(ephName)) 
                     if os.path.splitext(ephName[i])[1]=='.gz']
        if not not ephNameGZ:
            for x in ephNameGZ:
                decompress.dGZIP(self.config['IFP']+'/'  +ephName[x])
            
            readfolderM = readFolder.readFolder(self.config)
            ephPathM = []
            for l in readfolderM[0]:
                if bool(re.match('.\d\dp', os.path.splitext(l)[1], re.I)):
                    ephPathM.append(l)
                elif '_MN.rnx' in l:
                    ephPathM.append(l)
            ephNameM = []
            for l in readfolderM[2]:
                if bool(re.match('.\d\dp', l.split('.')[1], re.I)):
                    ephNameM.append(l)
                elif '_MN.rnx' in l:
                    ephNameM.append(l)
            ephPathM.sort()
            ephNameM.sort()
            return ephPathM, ephNameM
        else:
            ephPath.sort()
            ephName.sort()
            return ephPath, ephName
    
    def read(self, num):
        Path = self.path()
        # BRDC file
        BRDC_list = []
        with open(Path[0][num], 'r') as f:
            for l in f:
                BRDC_list.append(l)
        # BRDC header
        headerEndIndex = [i for i in range(len(BRDC_list)) if 'END OF HEADER' 
                          in BRDC_list[i]]
        header_list = BRDC_list[:(headerEndIndex[0]+1)]
        for l in header_list[:]:
            if not l:
                del l
        # BRDC data
        data_list = [x.strip('\n') for x in BRDC_list[headerEndIndex[-1]+1:]]
        for l in data_list[:]:
            if not l:
                del l
        return header_list, data_list
    