# -*- coding: utf-8 -*-
"""
Created on Thu Sep 28 16:10:44 2023

@author: chcuk
"""

from ftplib import  error_perm
import os
import time

# Note: Import your SimpleLogger class from its respective module
# from your_logging_module import SimpleLogger

class FTPDownloader:
    """
    A class to manage FTP downloads including downloading a single file and a directory.
    
    Attributes:
        ftp (FTP): The FTP object for the connection.
        logger (SimpleLogger): Logger for recording activities (Optional).
    """
    
    def __init__(self, ftp, logger=None):
        """
        Initialize the FTPDownloader with an FTP connection and an optional logger.
        
        Args:
            ftp (FTP): The FTP object for the connection.
            logger (SimpleLogger, optional): The logger for recording activities. 
                                             If None, logging is disabled.
        """
        self.ftp = ftp
        self.logger = logger

    def _log(self, message):
        """
        Write a log message if logging is enabled.

        Args:
            message (str): The log message.
        """
        if self.logger:
            self.logger.write_log(message)
        else:
            print(message)

    def download_file(self, remote_path, local_path, max_retries=3, retry_delay=5):
        """
        Download a single file from an FTP server with optional retries.
        
        Args:
            remote_path (str): The remote file path containing both directory and filename.
            local_path (str): The local file path.
            max_retries (int): Maximum number of download retries.
            retry_delay (int): Delay between retries in seconds.
        
        Returns:
            bool: True if download is successful, False otherwise.
        """
        # Separate the directory and file name from the remote_path (Pathlib)
        remote_dir = str(remote_path.parent).replace("\\", "/") # slashes cause issues
        remote_file_name = remote_path.name
        local_save_path = local_path / remote_file_name
        local_path.mkdir(parents=True, exist_ok=True)

        for attempt in range(1, max_retries + 1):
            try:
                # Change to the directory where the file is located
                self.ftp.cwd(remote_dir)
                
                with open(local_save_path, 'wb') as f:
                    self.ftp.retrbinary(f"RETR {remote_file_name}", f.write)
                    
                self._log(f"Successfully downloaded {remote_file_name} to {local_path}")
                return True
            except Exception as e:
                self._log(f"Failed to download {remote_file_name} to {local_path}, attempt {attempt} due to {str(e)}")
                time.sleep(retry_delay)
        return False
    
    def download_file_secure(self, remote_path, local_path, max_retries=3, retry_delay=5):
        """
        Securely download a single file from an FTP server with optional retries.
        
        Args:
            remote_path (str): The remote file path containing both directory and filename.
            local_path (str): The local file path.
            max_retries (int): Maximum number of download retries.
            retry_delay (int): Delay between retries in seconds.
        
        Returns:
            bool: True if secure download is successful, False otherwise.
        """
        # Assuming self.ftp is an instance of FTP_TLS
        self.ftp.prot_p()  # Set up secure data connection
        
        # Separate the directory and file name from the remote_path (Pathlib)
        remote_dir = str(remote_path.parent).replace("\\", "/")  # slashes cause issues
        remote_file_name = remote_path.name
        local_save_path = local_path / remote_file_name
        local_path.mkdir(parents=True, exist_ok=True)
        # local_save_path = local_save_path.replace("\\", "/")  # slashes cause issues

        for attempt in range(1, max_retries + 1):
            try:
                # Change to the directory where the file is located
                self.ftp.cwd(remote_dir)
                
                with open(local_save_path, 'wb') as f:
                    self.ftp.retrbinary(f"RETR {remote_file_name}", f.write)
                    
                self._log(f"Successfully downloaded {remote_file_name} to {local_path}")
                return True
            
            except Exception as e:
                self._log(f"Failed to download {remote_file_name} to {local_path}, attempt {attempt} due to {str(e)}")
                time.sleep(retry_delay)
        return False

    
    def download_directory(self, remote_dir, local_dir, max_retries=3, retry_delay=5):
        """
        Download a directory from an FTP server, including all subdirectories and files, with optional retries.
        
        Args:
            remote_dir (str): The remote directory path.
            local_dir (Path): The local directory path.
            max_retries (int): Maximum number of download retries for each file.
            retry_delay (int): Delay between retries in seconds.
        
        Returns:
            bool: True if download of all contents is successful, False otherwise.
        """
        local_dir_path = Path(local_dir)
        local_dir_path.mkdir(parents=True, exist_ok=True)
    
        for item in self.ftp.nlst(remote_dir):
            remote_item_path = Path(remote_dir) / item
            local_item_path = local_dir_path / item
    
            if self.is_directory(str(remote_item_path)):
                if not self.download_directory(str(remote_item_path), local_item_path, max_retries, retry_delay):
                    self._log(f"Failed to download directory {remote_dir} due to failure in downloading sub-directory {remote_item_path}")
                    return False
            else:
                if not self.download_file(str(remote_item_path), local_item_path, max_retries, retry_delay):
                    self._log(f"Failed to download directory {remote_dir} due to failure in downloading file {remote_item_path}")
                    return False
    
        self._log(f"Successfully downloaded directory {remote_dir} to {local_dir}")
        return True
    
    def is_directory(self, path):
        """
        Check if a given remote path is a directory.
        
        Args:
            path (str): The remote path.
        
        Returns:
            bool: True if the path is a directory, False otherwise.
        """
        current = self.ftp.pwd()
        try:
            self.ftp.cwd(path)
        except error_perm:
            return False
        else:
            self.ftp.cwd(current)
            return True
