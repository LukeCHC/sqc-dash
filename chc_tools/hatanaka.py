# -*- coding: utf-8 -*-
"""
Hatanaka convert
Created on Tue Mar  9 2021
@author: Dr Hui Zhi

Instructions
----------
Before running this, please put crx2rnx and rnx2crx executable 
files into your system variable path.
"""

import os
import subprocess

def rnx2crx(filePath):
    folderPath = os.path.split(filePath)[0]
    fileName   = os.path.split(filePath)[1]
    try:
        p = subprocess.Popen(
            '{} {}'.format('rnx2crx', fileName), cwd=folderPath, 
            shell=True, stderr=subprocess.PIPE)
        p.wait()
        os.remove(filePath)
        return True
    except Exception as e:
        print(e)
        return False
    
def crx2rnx(filePath):
    folderPath = os.path.split(filePath)[0]
    fileName   = os.path.split(filePath)[1]
    try:
        p = subprocess.Popen(
            '{} {}'.format('crx2rnx', fileName), cwd=folderPath, 
            shell=True, stderr=subprocess.PIPE)
        p.wait()
        os.remove(filePath)
        return True
    except Exception as e:
        print(e)
        return False