# -*- coding: utf-8 -*-
"""
Created on Thu Sep 28 16:15:38 2023

@author: chcuk
"""

from ftplib import FTP, error_perm
import os
import time


class FTPUploader:
    """
    A class to manage FTP uploads including uploading a single file and a directory.
    
    Attributes:
        ftp (FTP): The FTP object for the connection.
        logger (SimpleLogger): Logger for recording activities (Optional).
    """
    
    def __init__(self, ftp, logger=None):
        """
        Initialize the FTPUploader with an FTP connection and an optional logger.
        
        Args:
            ftp (FTP): The FTP object for the connection.
            logger (SimpleLogger, optional): The logger for recording activities. 
                                             If None, logging is disabled.
        """
        self.ftp = ftp
        self.logger = logger

    def write_log(self, message):
        """
        Write a log message if logging is enabled.

        Args:
            message (str): The log message.
        """
        if self.logger:
            self.logger.write_log(message)

    def upload_file(self, local_path, remote_path, max_retries=3, retry_delay=5):
        """
        Upload a single file to an FTP server with optional retries.
        
        Args:
            local_path (str): The local file path.
            remote_path (str): The remote file path.
            max_retries (int): Maximum number of upload retries.
            retry_delay (int): Delay between retries in seconds.
        
        Returns:
            bool: True if upload is successful, False otherwise.
        """
        for attempt in range(1, max_retries + 1):
            try:
                with open(local_path, 'rb') as f:
                    self.ftp.storbinary(f'STOR {remote_path}', f)
                self.write_log(f"Successfully uploaded {local_path} to {remote_path}")
                return True
            except Exception as e:
                self.write_log(f"Failed to upload {local_path} to {remote_path}, attempt {attempt} due to {str(e)}")
                time.sleep(retry_delay)
        return False
    
    def upload_directory(self, local_dir, remote_dir, max_retries=3, retry_delay=5):
        """
        Upload a directory to an FTP server, including all subdirectories and files, with optional retries.
        
        Args:
            local_dir (str): The local directory path.
            remote_dir (str): The remote directory path.
            max_retries (int): Maximum number of upload retries for each file.
            retry_delay (int): Delay between retries in seconds.
        
        Returns:
            bool: True if upload of all contents is successful, False otherwise.
        """
        for root, dirs, files in os.walk(local_dir):
            relative_path = os.path.relpath(root, local_dir)
            remote_root = os.path.join(remote_dir, relative_path)
            
            try:
                self.ftp.mkd(remote_root)
            except error_perm:
                pass  # Directory probably exists
            
            for file in files:
                local_file_path = os.path.join(root, file)
                remote_file_path = os.path.join(remote_root, file)
                
                if not self.upload_file(local_file_path, remote_file_path, max_retries, retry_delay):
                    self.write_log(f"Failed to upload directory {local_dir} due to failure in uploading file {local_file_path}")
                    return False
        
        self.write_log(f"Successfully uploaded directory {local_dir} to {remote_dir}")
        return True
