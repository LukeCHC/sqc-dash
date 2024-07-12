# -*- coding: utf-8 -*-
"""
Created on Thu Sep 28 16:49:31 2023

@author: chcuk
"""

import paramiko
import os
import time

# Note: Import your SimpleLogger class from its respective module
# from your_logging_module import SimpleLogger

class SFTPDownloader:
    """
    A class to manage SFTP downloads including downloading a single file and a directory.
    
    Attributes:
        sftp (paramiko.SFTPClient): The SFTPClient object for the connection.
        logger (SimpleLogger): Logger for recording activities (Optional).
    """
    
    def __init__(self, sftp, logger=None):
        """
        Initialize the SFTPDownloader with an SFTP connection and an optional logger.
        
        Args:
            sftp (paramiko.SFTPClient): The SFTPClient object for the connection.
            logger (SimpleLogger, optional): The logger for recording activities. 
                                             If None, logging is disabled.
        """
        self.sftp = sftp
        self.logger = logger

    def write_log(self, message):
        """
        Write a log message if logging is enabled.

        Args:
            message (str): The log message.
        """
        if self.logger:
            self.logger.write_log(message)

    def download_file(self, remote_path, local_path, max_retries=3, retry_delay=5):
        """
        Download a single file from an SFTP server with optional retries.
        
        Args:
            remote_path (str): The remote file path.
            local_path (str): The local file path.
            max_retries (int): Maximum number of download retries.
            retry_delay (int): Delay between retries in seconds.
        
        Returns:
            bool: True if download is successful, False otherwise.
        """
        for attempt in range(1, max_retries + 1):
            try:
                self.sftp.get(remote_path, local_path)
                self.write_log(f"Successfully downloaded {remote_path} to {local_path}")
                return True
            except Exception as e:
                self.write_log(f"Failed to download {remote_path} to {local_path}, attempt {attempt} due to {str(e)}")
                time.sleep(retry_delay)
        return False
    
    def download_directory(self, remote_dir, local_dir, max_retries=3, retry_delay=5):
        """
        Download a directory from an SFTP server, including all subdirectories and files, with optional retries.
        
        Args:
            remote_dir (str): The remote directory path.
            local_dir (str): The local directory path.
            max_retries (int): Maximum number of download retries for each file.
            retry_delay (int): Delay between retries in seconds.
        
        Returns:
            bool: True if download of all contents is successful, False otherwise.
        """
        os.makedirs(local_dir, exist_ok=True)
        
        for item in self.sftp.listdir(remote_dir):
            remote_item_path = os.path.join(remote_dir, item)
            local_item_path = os.path.join(local_dir, item)
            
            if self.is_directory(remote_item_path):
                if not self.download_directory(remote_item_path, local_item_path, max_retries, retry_delay):
                    self.write_log(f"Failed to download directory {remote_dir} due to failure in downloading sub-directory {remote_item_path}")
                    return False
            else:
                if not self.download_file(remote_item_path, local_item_path, max_retries, retry_delay):
                    self.write_log(f"Failed to download directory {remote_dir} due to failure in downloading file {remote_item_path}")
                    return False
        
        self.write_log(f"Successfully downloaded directory {remote_dir} to {local_dir}")
        return True
    
    def is_directory(self, path):
        """
        Check if a given remote path is a directory.
        
        Args:
            path (str): The remote path.
        
        Returns:
            bool: True if the path is a directory, False otherwise.
        """
        try:
            return paramiko.SFTPAttributes.is_dir(self.sftp.stat(path))
        except IOError:
            return False
