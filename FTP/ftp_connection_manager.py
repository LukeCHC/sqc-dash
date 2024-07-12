from ftplib import FTP, FTP_TLS, error_perm
import time


class FTPConnectionManager:
    """
    A class to manage FTP connections including connecting, authenticating, and disconnecting.
    
    Attributes:
        server (str): The FTP server address.
        port (int): The FTP server port.
        ftp (FTP_TLS): The FTP object for the secure connection.
        logger (SimpleLogger): Logger for recording activities (Optional).
    """
    
    def __init__(self, logger=None):
        """
        Initialize the FTPConnectionManager with an optional logger.
        
        Args:
            logger (SimpleLogger, optional): The logger for recording activities. 
                                             This should be an instance of the SimpleLogger class.
                                             If None, logging is disabled.
        """
        self.server = None
        self.port = None
        self.ftp = None
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

    def connect(self, server, port, max_retries=3, retry_delay=5):
        """Connect to an FTP server with optional retries."""
        
        self.server = server
        self.port = port
        for attempt in range(1, max_retries + 1):
            try:
                self.ftp = FTP()
                self.ftp.connect(self.server, self.port)
                self._log(f"Successfully connected to {self.server}:{self.port}")
                return True
            except Exception as e:
                self._log(f"Failed to connect to {self.server}:{self.port}, attempt {attempt} due to {str(e)}")
                time.sleep(retry_delay)

    def connect_secure(self, server, port, max_retries=3, retry_delay=5):
        """
        Connect securely to an FTP server with optional retries.
        
        Args:
            server (str): The FTP server address.
            port (int): The FTP server port.
            max_retries (int): Maximum number of connection retries.
            retry_delay (int): Delay between retries in seconds.
        
        Returns:
            bool: True if secure connection is successful, False otherwise.
        """
        self.server = server
        self.port = port
        for attempt in range(1, max_retries + 1):
            try:
                self.ftp = FTP_TLS()
                self.ftp.connect(self.server, self.port)
                self.ftp.auth()  # secure the data connection
                self.ftp.prot_p()  # Switch to secure data connection
                self._log(f"Successfully connected securely to {self.server}:{self.port}")
                return True
            except Exception as e:
                self._log(f"Failed to connect securely to {self.server}:{self.port}, attempt {attempt} due to {str(e)}")
                time.sleep(retry_delay)
        return False

    def authenticate(self, username, password, use_auth=True):
        """
        Authenticate with the FTP server.
        
        Args:
            username (str): The username for authentication.
            password (str): The password for authentication.
            use_auth (bool): Flag to toggle authentication.
        
        Returns:
            bool: True if authentication is successful, False otherwise.
        """
        if not use_auth:
            self._log("Authentication is toggled off. Skipping.")
            return True
        try:
            self.ftp.login(username, password)
            self._log(f"Successfully authenticated as {username}")
            return True
        except error_perm as e:
            self._log(f"Authentication failed: {str(e)}")
            return False

    def disconnect(self):
        """
        Disconnect from the FTP server.
        
        Returns:
            bool: True if disconnection is successful, False otherwise.
        """
        try:
            self.ftp.quit()
            self._log(f"Successfully disconnected from {self.server}:{self.port}")
            return True
        except Exception as e:
            self._log(f"Failed to disconnect from {self.server}:{self.port} due to {str(e)}")
            return False

    def list_files(self, remote_path):
        """
        List files in the given remote directory.

        Args:
            remote_path (str): The remote directory path.

        Returns:
            list: List of filenames in the remote directory.
        """
        try:
            self.ftp.cwd(remote_path)
            filenames = self.ftp.nlst()
            return filenames
        except Exception as e:
            self._log(f"Failed to list files in {remote_path} due to {str(e)}")
            return []

    def download_file(self, remote_file_path, local_file_path):
        """
        Download a file from the FTP server.

        Args:
            remote_file_path (str): The path of the remote file to download.
            local_file_path (str): The local path to save the downloaded file.
        
        Returns:
            bool: True if the file is successfully downloaded, False otherwise.
        """
        try:
            with open(local_file_path, 'wb') as local_file:
                self.ftp.retrbinary(f"RETR {remote_file_path}", local_file.write)
            self._log(f"Successfully downloaded {remote_file_path} to {local_file_path}")
            return True
        except Exception as e:
            self._log(f"Failed to download {remote_file_path} due to {str(e)}")
            return False
