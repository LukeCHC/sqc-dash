# -*- coding: utf-8 -*-
"""
Created on Mon Oct  2 11:46:17 2023

@author: chcuk
"""
import FTP

class FTPWorkflowManager:
    """
    This class acts as a centralized manager to handle various FTP workflows.
    It utilizes other classes within the FTP package for connecting, downloading, and disconnecting.
    
    Attributes:
        logger (SimpleLogger): An instance of the SimpleLogger class for logging activities.
    """
    
    def __init__(self, logger=None):
        """
        Initialize the GNSSWorkflowManager with an optional logger.
        
        Args:
            logger (SimpleLogger, optional): The logger for recording activities. 
                                             If None, logging is disabled.
        """
        self.logger = logger
        
    def write_log(self, message):
        """
        Write a log message if logging is enabled.

        Args:
            message (str): The log message.
        """
        if self.logger:
            self.logger.write_log(message)

    def connect_and_download(self, ip_address, remote_path, file_name, local_dir, username=None, password=None):
        """
        Execute a standard FTP workflow for file downloading.
        
        Args:
            ip_address (str): The FTP server IP address.
            remote_path (str): The remote directory path where the file is located.
            file_name (str): The name of the file to download.
            local_dir (str): The local directory to save the downloaded file.
        
        Returns:
            bool: True if the FTP workflow is successful, False otherwise.
        """
        # Initialize FTPConnectionManager and connect to the FTP server
        connection_manager = FTP.FTPConnectionManager(logger=self.logger)
        if not connection_manager.connect(ip_address, 21):
            return False
        
        # Authenticate if username and password are provided
        if username is not None or password is not None:
            if not connection_manager.authenticate(username, password):
                connection_manager.disconnect()
                return False
        
        # Initialize FTPDownloader and download the file
        downloader = FTP.FTPDownloader(connection_manager.ftp, logger=self.logger)
        if not downloader.download_file(remote_path / file_name, local_dir):
            connection_manager.disconnect()  # Disconnect before exiting
            return False
        
        # Disconnect from the FTP server
        connection_manager.disconnect()
        return True
    
    def connect_and_download_secure(self, ip_address, remote_path, file_name, local_dir, username=None, password=None):
        """
        Execute a standard secure FTP workflow for file downloading.
        
        Args:
            ip_address (str): The FTP server IP address.
            remote_path (str): The remote directory path where the file is located.
            file_name (str): The name of the file to download.
            local_dir (str): The local directory to save the downloaded file.
            username (str, optional): Username for FTP server authentication.
            password (str, optional): Password for FTP server authentication.
        
        Returns:
            bool: True if the FTP workflow is successful, False otherwise.
        """
        # Initialize FTPConnectionManager and connect to the FTP server securely
        connection_manager = FTP.FTPConnectionManager(logger=self.logger)
        
        # Use the secure connection method here
        if not connection_manager.connect_secure(ip_address, 21):
            return False
        
        # Authenticate if username and password are provided
        if username is not None and password is not None:
            if not connection_manager.authenticate(username, password):
                connection_manager.disconnect()
                return False
        
        # Initialize FTPDownloader and download the file
        downloader = FTP.FTPDownloader(connection_manager.ftp, logger=self.logger)
        if not downloader.download_file_secure(remote_path / file_name, local_dir):
            connection_manager.disconnect()  # Disconnect before exiting
            return False
        
        # Disconnect from the FTP server
        connection_manager.disconnect()
        return True


