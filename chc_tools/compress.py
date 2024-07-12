#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Compress files
Created on Tue Sep  7 2021
@author: Dr Hui Zhi
"""

import gzip
import shutil
from pathlib import Path 

def cGZIP(filePath: str) -> bool:
    """
    Compresses a file using gzip and deletes the original file.
    
    Args:
        filePath (str): The path to the file to be compressed.
        
    Returns:
        bool: True if the file was successfully compressed and deleted, False otherwise.
    """
    file_path = Path(filePath)
    new_path = file_path.with_suffix(file_path.suffix + '.gz')

    try:
        with file_path.open('rb') as f:
            with gzip.open(new_path, 'wb') as g:
                g.write(f.read())
        file_path.unlink()  # Remove the original file
        return True
    except Exception as e:
        print(e)
        return False
    
def compress_directory(directory_path, archive_name):
    """
    Compress a directory into a zip archive.

    Args:
        directory_path (str or Path): Path to the directory to be compressed.
        archive_name (str or Path): Name of the output archive file (without extension).

    Returns:
        bool: True if compression is successful, False otherwise.
    """
    try:
        directory_path = Path(directory_path)
        archive_name = Path(archive_name)
        
        # Check if the directory exists
        if not directory_path.is_dir():
            raise ValueError(f"The specified directory does not exist: {directory_path}")
        
        # Create the archive
        shutil.make_archive(str(archive_name), 'zip', root_dir=str(directory_path))
        return True
    except ValueError as ve:
        print(f"ValueError: {ve}")
        return False
    except OSError as oe:
        print(f"OSError: {oe}")
        return False
    except Exception as e:
        # Catch any other unexpected exceptions
        print(f"Unexpected error: {e}")
        return False
        