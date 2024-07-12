# -*- coding: utf-8 -*-
"""
Decompress
Created on Tue Sep  7 2021
@author: Dr Hui Zhi
"""

import os
import gzip
from pathlib import Path
import subprocess

def decompress_gzip(input_path):
    """
    Decompress a .gz file. The output file will have the same name and location as the input file,
    but without the .gz extension. The original .gz file is removed after decompression.

    Parameters:
    - input_path (str or Path): The path to the .gz file to be decompressed.

    Returns:
    - output Path if successful
    - bool: False if decompression was unsuccessful.
    """
    # Convert input_path to Path object if it's not already one
    input_path = Path(input_path)

    # Infer the output path by removing the .gz extension
    output_path = input_path.with_suffix('')

    try:
        # Open the gzip file and write its contents to the output file
        with gzip.open(input_path, 'rb') as gz_file:
            with open(output_path, 'wb') as out_file:
                out_file.write(gz_file.read())

        # Remove the original gzip file
        input_path.unlink()

        return output_path
    except Exception as e:
        return e

def dGZIP(inPath, outPath):
    # decompress .gz file
    try:
        with gzip.open(inPath, 'rb') as g:
            with open(outPath, 'wb') as f:
                f.write(g.read())
        os.remove(inPath)
        return True
    except Exception as e:
        print(e)
        return False
    
def dZ(filePath):
    import unlzw
    # decompress .Z file
    newPath = os.path.splitext(filePath)[0]
    try:
        with open(filePath, 'rb') as z:
            with open(newPath, 'wb') as f:
                f.write(unlzw(z.read()))
        os.remove(filePath)
        return True
    except Exception as e:
        print(e)
        return False
                
def dRAR( filePath):
    # unzip .zip file (from SH RINEX computer)
    # need to install 7z for windows firstly
    folderPath = os.path.split(filePath)[0]
    fileName   = os.path.split(filePath)[1]
    try:
        cmd = '{} {} {} {}{}'.format('7z', 'x', fileName, '-o', folderPath)
        p   = subprocess.Popen(
            cmd, cwd=folderPath, shell=True, stderr=subprocess.PIPE)
        p.wait()
        os.remove(filePath)
        return True
    except Exception as e:
        print(e)
        return False

# def dGZIP(config, filePath):
#     # decompress .gz file
#     newPath = os.path.splitext(filePath)[0]
#     try:
#         with gzip.open(filePath, 'rb') as g:
#             with open(newPath, 'wb') as f:
#                 f.write(g.read())
#         os.remove(filePath)
#         st1 = '{} {}'.format(filePath, 'decompress successfully.')
#         INI.logRecord(config, st1)
#     except Exception:
#         st2 = '{} {} {}'.format('Error: ', filePath, 'decompress failed.')
#         INI.logRecord(config, st2)

# def dZ(config, filePath):
#     # decompress .Z file
#     newPath = os.path.splitext(filePath)[0]
#     try:
#         with open(filePath, 'rb') as z:
#             with open(newPath, 'wb') as f:
#                 f.write(unlzw(z.read()))
#         os.remove(filePath)
#         st1 = '{} {}'.format(filePath, 'decompress successfully.')
#         INI.logRecord(config, st1)
#     except Exception:
#         st2 = '{} {} {}'.format('Error: ', filePath, 'decompress failed.')
#         INI.logRecord(config, st2)
                
# def dRAR(config, filePath):
#     # unzip .zip file (from SH RINEX computer)
#     # need to install 7z for windows firstly
#     folderPath = os.path.split(filePath)[0]
#     fileName   = os.path.split(filePath)[1]
#     try:
#         cmd = '{} {} {} {}{}'.format('7z', 'x', fileName, '-o', folderPath)
#         p   = subprocess.Popen(
#             cmd, cwd=folderPath, shell=True, stderr=subprocess.PIPE)
#         p.wait()
#         os.remove(filePath)
#         st1 = '{} {}'.format(filePath, 'decompress successfully.')
#         INI.logRecord(config, st1)
#     except Exception:
#         st2 = '{} {} {}'.format('Error: ', filePath, 'decompress failed.')
#         INI.logRecord(config, st2)
    