# -*- coding: utf-8 -*-
"""
Created on Thu Sep 28 16:34:17 2023

@author: chcuk
"""

import requests
import time

# Note: Import your SimpleLogger class from its respective module
# from your_logging_module import SimpleLogger

class URLDownloader:
    """
    A class to manage downloads from URLs.
    
    Attributes:
        logger (SimpleLogger): Logger for recording activities (Optional).
    """
    
    def __init__(self, logger=None):
        """
        Initialize the URLDownloader with an optional logger.
        
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

    def download_from_url(self, url, local_path, max_retries=3, retry_delay=5):
        """
        Download a file from a URL with optional retries.
        
        Args:
            url (str): The URL to download from.
            local_path (str): The local file path to save the downloaded file.
            max_retries (int): Maximum number of download retries.
            retry_delay (int): Delay between retries in seconds.
        
        Returns:
            bool: True if download is successful, False otherwise.
        """
        for attempt in range(1, max_retries + 1):
            try:
                response = requests.get(url)
                response.raise_for_status()  # Raise an exception for HTTP errors
                with open(local_path, 'wb') as f:
                    f.write(response.content)
                self.write_log(f"Successfully downloaded from {url} to {local_path}")
                return True
            except Exception as e:
                self.write_log(f"Failed to download from {url} to {local_path}, attempt {attempt} due to {str(e)}")
                time.sleep(retry_delay)
        return False
