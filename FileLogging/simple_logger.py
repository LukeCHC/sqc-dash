# -*- coding: utf-8 -*-
"""
Created on Thu Sep 28 12:12:30 2023

@author: chcuk
"""
from pathlib import Path
from datetime import datetime

# Implementing error handling and context manager support in the SimpleLogger class

class SimpleLogger:
    """
    A simple logger class to write log messages to a specified log file.
    
    Attributes:
        logfile (Path): The path to the log file.
    """
    
    def __init__(self, logfile: str, print_to_console = False):
        """
        Initialize the logger and set the log file path.
        
        Args:
            logfile (str): The path to the log file where log messages will be written.
        """
        self.logfile = Path(logfile)
        self.print_to_console = print_to_console
        # Create the log file if it doesn't exist
        try:
            # Create the parent directories if they don't exist
            self.logfile.parent.mkdir(parents=True, exist_ok=True)
            
            #Create the file
            self.logfile.touch(exist_ok=True)
        except Exception as e:
            print(f"Failed to create or access log file: {e}")
        
    def write_log(self, message: str) -> None:
        """
        Write a log message to the log file with a timestamp.
        
        Args:
            message (str): The log message to be written.
        """
        # Get the current timestamp
        timestamp = datetime.now().strftime("%d-%m-%Y %H:%M:%S")
        # Format the log entry
        log_entry = f"{timestamp} - {message}\n"
        
        # Write the log entry to the log file
        try:
            with self.logfile.open("a") as f:
                f.write(log_entry)
            if self.print_to_console:
                print(log_entry)
        except Exception as e:
            print(f"Failed to write to log file: {e}")

    def rename_logfile(self, new_name: str):
        """
        Renames the current log file to the specified new name.

        Args:
            new_name (str): The new name for the log file.
        """
        try:
            new_path = self.logfile.parent / new_name
            self.logfile.rename(new_path)
        except Exception as e:
            self.write_log(f"Failed to rename log file: {e}")

    # Context Manager methods, allows for calling the class inside a 'with' 
    # statement to ensure memory is deleted.
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_value, traceback):
        # Optionally, handle exceptions here if you wish
        pass

# # Test the SimpleLogger class with context manager support and error handling
# with SimpleLogger("/mnt/data/sample_log_with_features.txt") as logger:
#     logger.write_log("This is a test log message with features.")
#     logger.write_log("Another test log message with features.")

# # Read the log file to check if the logs are correctly written
# try:
#     with open("/mnt/data/sample_log_with_features.txt", "r") as f:
#         log_contents = f.readlines()
# except Exception as e:
#     log_contents = f"Failed to read log file: {e}"

# log_contents
