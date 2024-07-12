from pathlib import Path
from chc_tools.decompress import decompress_gzip
import FTP

class DownloadBrdc:
    def __init__(self, epoch, download_dir, logger = None):
        """
        epoch: datetime of file to download
        download_dir: path object of directory to download file to
        """
        self.epoch = epoch
        self.download_dir = Path(download_dir)
        self.logger = logger

    def _log(self, message):
        if self.logger:
            self.logger.write_log(message)
        else:
            print(message)

    def generate_remote_path(self):
        """Converts datetime to ftp remote path"""

        epoch = self.epoch
        year = epoch.year
        doy = epoch.timetuple().tm_yday

        remote_file_path = Path(f"/gps/data/daily/{year}/brdc/")
        remote_file_name = f"BRDC00IGS_R_{year}{doy:03d}0000_01D_MN.rnx.gz"
        return remote_file_path, remote_file_name

    def download(self):
    
        remote_path, remote_file = self.generate_remote_path()
        local_file_path = self.download_dir / remote_file
        local_file_path_check = self.download_dir / remote_file.replace(".gz", "")
        if not local_file_path_check.exists():
            success_flag = FTP.FTPWorkflowManager(self.logger).connect_and_download_secure("gdc.cddis.eosdis.nasa.gov", remote_path, remote_file, self.download_dir, 'anonymous', '')
            if success_flag:
                self._log(f"File {local_file_path} downloaded successfully")
                decompress_check = decompress_gzip(local_file_path)
                if isinstance(decompress_check, Path):
                    self._log(f"File {local_file_path} decompressed successfully")
                    return local_file_path_check
                else:
                    self._log(f"File {local_file_path} decompression failed: {decompress_check}")
            else:
                self._log(f"File {local_file_path} download failed")


        else:
            self._log(f"File {local_file_path} already exists")

            return local_file_path_check


if __name__ == "__main__":
    from datetime import datetime
    epoch = datetime(2021, 1, 1)
    download_dir = Path(r"F:\test")
    DownloadBrdc(epoch, download_dir).download()