from datetime import datetime
from time_transform import time_format as tf

from chc_tools import decompress
import FTP
from pathlib import Path
# Assuming FTP.FTPConnectionManager is available
# Assuming SimpleLogger is imported

class GNSSDownloader:
    def __init__(self, epoch: datetime, locDir: str, logger=None):
        """
        Initialize the GNSSDownloader class.

        Args:
            epoch (datetime): The epoch of interest.
            locDir (str): The local directory to store downloaded files.
            logger (SimpleLogger): An instance of the SimpleLogger class for logging activities.
        """
        self.epoch = epoch
        self.locDir = locDir
        self.logger = logger
        self.ftp_manager = FTP.FTPWorkflowManager(logger=self.logger)
        self.year = None
        self.gps_week = None
        self.doy = None
        
    def write_log(self, message):
        """
        Write log if logger is available.

        Args:
            message (str): The message to log.
        """
        if self.logger:
            self.logger.write_log(message)
            
    def extract_time_information(self):
        """
        Extracts and sets the time-related information needed for file downloading.
        """
        # Your gpsT and tf logic here
        # Assuming tf and gpsT are defined and imported
        gpsT = tf.GpsTime(self.epoch)
        self.year = "%04d" % gpsT.datetime.year
        self.doy = "%03d" % tf.dayOfYear(self.epoch)
        self.gps_week = "%04d" % gpsT.GPSFullWeek
        self.dow = "%d" % gpsT.GPSDOW
        
    def check_time_info_exists(self):
        """
        Checks if the class variables year, doy and gps_week exist.
        
        """
        if not self.year or not self.gps_week or not self.doy:
            self.extract_time_information()            


    def sp3R(self):
        """
        Download rapid SP3 files.

        Args:
            doy (int): Day of the year.
        
        Returns:
            str: The local path to the downloaded SP3 file.
        """
        # Ensure class variables exist
        self.check_time_info_exists()  # Assume this function sets self.year, self.gps_week, self.doy, etc.
        
        primary_IP = "igs.ign.fr"
        primary_remote_path = Path(f"/pub/igs/products/mgex/{self.gps_week}/")
        tarF = f"GFZ0MGXRAP_{self.year}{self.doy}0000_01D_05M_ORB.SP3.gz"
        tarN = f"GFZ0MGXRAP_{self.year}{self.doy}0000_01D_05M_ORB.SP3"

        
        # Define local paths using pathlib
        local_tarN = self.locDir / tarN
        local_tarF = self.locDir / tarF
        

        # # Try downloading from the primary source
        if not local_tarN.exists():
            success = self.ftp_manager.connect_and_download(primary_IP, primary_remote_path, tarF, self.locDir, username = "", password = "")
            if success:
                decompress.dGZIP(local_tarF, local_tarN)  # Assuming decompress.dGZIP can handle pathlib.Path
                self.write_log(f"Successfully downloaded {tarF} from {primary_IP}")
                return str(local_tarN)
        
            backup_IP = "gdc.cddis.eosdis.nasa.gov"
            backup_remote_path = Path(f"/pub/gps/products/{self.gps_week}/")
            backup_tarF = f"IGS0OPSRAP_{self.year}{self.doy}0000_01D_15M_ORB.SP3.gz" # old file f"igr{self.gps_week}{self.dow}.sp3.Z"
            local_backup_tarF = self.locDir / backup_tarF
    
            # If primary fails, try the backup source
            success = self.ftp_manager.connect_and_download_secure(backup_IP, backup_remote_path, backup_tarF, self.locDir, username = "", password = "")
            if success:
                decompress.dGZIP(local_backup_tarF, local_tarN)  # Assuming decompress.dGZIP can handle pathlib.Path
                self.write_log(f"Successfully downloaded {backup_tarF} from {backup_IP}")
                return str(local_tarN)
        
            #NOTE! When we decompress backupfile, we give it the name of the original file, I think it is a simpler solution
            
            self.write_log(f"Failed to download {tarF} from both sources.")
            return False
    
        else: 
            self.write_log(f"{tarN} already exists in {self.locDir}")
            return str(local_tarN)

    def sp3F(self):
        """
        Download final SP3 files.
    
        Args:
            doy (int): Day of the year.
        
        Returns:
            str: The local path to the downloaded SP3 file.
        """
        # Ensure class variables exist
        self.check_time_info_exists()  # Assume this function sets self.year, self.gps_week, self.doy, etc.
    
        # Define the primary URL and file name format
        primary_url_base = f"http://navigation-office.esa.int/products/gnss-products/{self.gps_week}"
        tarF = f"ESA0MGNFIN_{self.year}{self.doy}0000_01D_05M_ORB.SP3.gz"
        tarN = f"ESA0MGNFIN_{self.year}{self.doy}0000_01D_05M_ORB.SP3"
        primary_full_url = f"{primary_url_base}/{tarF}"
    
        # Define local paths using pathlib
        local_tarN = self.locDir / tarN
        local_tarF = self.locDir / tarF
    
        # Initialize URLDownloader
        url_downloader = FTP.URLDownloader(logger=self.logger)
    
        # Try downloading from the primary source
        if not local_tarN.exists():
            success = url_downloader.download_from_url(primary_full_url, local_tarF)
            if success:
                decompress.dGZIP(local_tarF, local_tarN)  # Assuming decompress.dGZIP can handle pathlib.Path
                self.write_log(f"Successfully downloaded {tarF} from {primary_url_base}")
                return str(local_tarN)
            
            backup_IP = "gdc.cddis.eosdis.nasa.gov"
            backup_remote_path = Path(f"/pub/gps/products/{self.gps_week}/")
            backup_tarF = f"IGS0OPSFIN_{self.year}{self.doy}0000_01D_15M_ORB.SP3.gz" # old file f"igr{self.gps_week}{self.dow}.sp3.Z"
            local_backup_tarF = self.locDir / backup_tarF
    
            # If primary fails, try the backup source
            success = self.ftp_manager.connect_and_download_secure(backup_IP, backup_remote_path, backup_tarF, self.locDir, username = "", password = "")
            if success:
                decompress.dGZIP(local_backup_tarF, local_tarN)  # Assuming decompress.dGZIP can handle pathlib.Path
                self.write_log(f"Successfully downloaded {backup_tarF} from {backup_IP}")
                return str(local_tarN)
    
            self.write_log(f"Failed to download {tarF} from both sources.")
            return False
    
        else:
            self.write_log(f"{tarN} already exists in {self.locDir}")
            return str(local_tarN)

    ####
    
    def clkR(self):
        """
        Download rapid CLK files.

        Args:
            doy (int): Day of the year.
        
        Returns:
            str: The local path to the downloaded SP3 file.
        """
        # Ensure class variables exist
        self.check_time_info_exists()  # Assume this function sets self.year, self.gps_week, self.doy, etc.
        
        primary_IP = "igs.ign.fr"
        primary_remote_path = Path(f"/pub/igs/products/mgex/{self.gps_week}/")
        tarF = f"GFZ0MGXRAP_{self.year}{self.doy}0000_01D_30S_CLK.CLK.gz"
        tarN = f"GFZ0MGXRAP_{self.year}{self.doy}0000_01D_30S_CLK.CLK"

        # Define local paths using pathlib
        local_tarN = self.locDir / tarN
        local_tarF = self.locDir / tarF
        

        # # Try downloading from the primary source
        if not local_tarN.exists():
            success = self.ftp_manager.connect_and_download(primary_IP, primary_remote_path, tarF, self.locDir, username = "", password = "")
            if success:
                decompress.dGZIP(local_tarF, local_tarN)  # Assuming decompress.dGZIP can handle pathlib.Path
                self.write_log(f"Successfully downloaded {tarF} from {primary_IP}")
                return str(local_tarN)
        
            backup_IP = "gdc.cddis.eosdis.nasa.gov"
            backup_remote_path = Path(f"/pub/gps/products/{self.gps_week}/")
            backup_tarF = f"IGS0OPSRAP_{self.year}{self.doy}000001D_05M_CLK.CLK.gz" # can only find 5 mins interval from other sources
            local_backup_tarF = self.locDir / backup_tarF
    
            # If primary fails, try the backup source
            success = self.ftp_manager.connect_and_download_secure(backup_IP, backup_remote_path, backup_tarF, self.locDir, username = "", password = "")
            if success:
                decompress.dGZIP(local_backup_tarF, local_tarN)  # Assuming decompress.dGZIP can handle pathlib.Path
                self.write_log(f"Successfully downloaded {backup_tarF} from {backup_IP}")
                return str(local_tarN)
        
            #NOTE! When we decompress backupfile, we give it the name of the original file, I think it is a simpler solution
            
            self.write_log(f"Failed to download {tarF} from both sources.")
            return False
    
        else: 
            self.write_log(f"{tarN} already exists in {self.locDir}")
            return str(local_tarN)

    def clkF(self):
        """
        Download final CLK files.
    
        Args:
            doy (int): Day of the year.
        
        Returns:
            str: The local path to the downloaded SP3 file.
        """
        # Ensure class variables exist
        self.check_time_info_exists()  # Assume this function sets self.year, self.gps_week, self.doy, etc.
    
        # Define the primary URL and file name format
        primary_url_base = f"http://navigation-office.esa.int/products/gnss-products/{self.gps_week}"
        tarF = f"ESA0MGNFIN_{self.year}{self.doy}0000_01D_30S_CLK.CLK.gz"
        tarN = f"ESA0MGNFIN_{self.year}{self.doy}0000_01D_30S_CLK.CLK"
        primary_full_url = f"{primary_url_base}/{tarF}"
    
        # Define local paths using pathlib
        local_tarN = self.locDir / tarN
        local_tarF = self.locDir / tarF
    
        # Initialize URLDownloader
        url_downloader = FTP.URLDownloader(logger=self.logger)
    
        # Try downloading from the primary source
        if not local_tarN.exists():
            success = url_downloader.download_from_url(primary_full_url, local_tarF)
            if success:
                decompress.dGZIP(local_tarF, local_tarN)  # Assuming decompress.dGZIP can handle pathlib.Path
                self.write_log(f"Successfully downloaded {tarF} from {primary_url_base}")
                return str(local_tarN)
            
            backup_IP = "gdc.cddis.eosdis.nasa.gov"
            backup_remote_path = Path(f"/pub/gps/products/{self.gps_week}/")
            backup_tarF = f"GRG0MGXFIN_{self.year}{self.doy}0000_01D_30S_CLK.CLK.gz" # old file f"igr{self.gps_week}{self.dow}.sp3.Z"
            local_backup_tarF = self.locDir / backup_tarF
    
            # If primary fails, try the backup source
            success = self.ftp_manager.connect_and_download_secure(backup_IP, backup_remote_path, backup_tarF, self.locDir, username = "", password = "")
            if success:
                decompress.dGZIP(local_backup_tarF, local_tarN)  # Assuming decompress.dGZIP can handle pathlib.Path
                self.write_log(f"Successfully downloaded {backup_tarF} from {backup_IP}")
                return str(local_tarN)
    
            self.write_log(f"Failed to download {tarF} from both sources.")
            return False
    
        else:
            self.write_log(f"{tarN} already exists in {self.locDir}")
            return str(local_tarN)


#%%

# to test this class

from datetime import datetime, timedelta
from FileLogging.simple_logger import SimpleLogger

def test_download_methods(directory, test_sp3R=0, test_sp3F=1, test_clkR=0,test_clkF=0):
    # Define test epoch and local directory
    test_epoch = datetime.now() - timedelta(days=23)
    test_locDir = Path(directory)

    # Create test logger (Assuming SimpleLogger is imported and initialized)
    log_path = test_locDir / 'test.log'
    test_logger = SimpleLogger(logfile=log_path)

    # Create GNSSDownloader instance
    gnss_downloader = GNSSDownloader(epoch=test_epoch, locDir=test_locDir, logger=test_logger)

    if test_sp3R:
        # Run the sp3R method
        result_sp3R = gnss_downloader.sp3R()
        
        # Check the result
        if result_sp3R:
            print(f"Successfully downloaded SP3R file to {result_sp3R}")
        else:
            print("Failed to download SP3R file")

    if test_sp3F:
        # Run the sp3F method
        result_sp3F = gnss_downloader.sp3F()
        
        # Check the result
        if result_sp3F:
            print(f"Successfully downloaded SP3F file to {result_sp3F}")
        else:
            print("Failed to download SP3F file")

    if test_clkR:
        # Run the clk method (assuming it is implemented)
        result_clk = gnss_downloader.clkR()
        
        # Check the result
        if result_clk:
            print(f"Successfully downloaded CLKR file to {result_clk}")
        else:
            print("Failed to download CLKR file")

    if test_clkF:
        # Run the clk method (assuming it is implemented)
        result_clk = gnss_downloader.clkF()
        
        # Check the result
        if result_clk:
            print(f"Successfully downloaded CLKF file to {result_clk}")
        else:
            print("Failed to download CLKF file")


# if __name__ =='__main__':
# test_dir = "C:/Users/chcuk/Work/Projects/I2GV2/test"
# test_download_methods(test_dir)