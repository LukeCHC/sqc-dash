# -*- coding: utf-8 -*-
"""
Created on Wed Aug 12 2020
@author: Dr Hui Zhi
"""

import os
import gzip
from unlzw import unlzw
from datetime import datetime

def decompress2(config, tarF, tarN):
    # decompress .gzip file
    """
    Parameters
    ----------
    tarF : path + filename (.gz)
    tarN : path + filename (decompressed)
    -------
    """
    now     = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    logFile = '{}{}'.format(config['OFP'], '/logFile.txt')
    try:
        with gzip.open(config['IFP'] + '/' + tarF, 'rb') as g:
            with open(config['IFP'] + '/' + tarN, 'wb') as f:
                f.write(g.read())
        os.remove(config['IFP'] + '/' + tarF)
        st1 = '{}\t{} {}\n'.format(now, tarF, 'decompress successfully.')
        print(st1)
        with open(logFile, 'a') as f:
                f.write(st1)
    except Exception:
        st2 = '{}\t{} {} {}\n'.format(now, 'Error: ',tarF,'decompress failed.')
        print(st2)
        with open(logFile, 'a') as f:
                f.write(st2)

def upzip2(tarF, tarN, localPath):
    # decompress .Z file
    """
    Parameters
    ----------
    tarF : path + filename (.Z)
    tarN : path + filename (decompressed)
    localPath : folder path
    -------
    """
    try:
        with open(localPath + '/' + tarF, 'rb') as z:
            with open(localPath + '/' + tarN, 'wb') as f:
                f.write(unlzw(z.read()))
        os.remove(localPath + '/' + tarF)
        print(tarF + ' decompress successful.')
    except Exception:
        print(tarF + ' decompress failed.')
