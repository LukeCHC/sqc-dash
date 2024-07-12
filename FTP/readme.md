# FTP Package

This package contains many modules that encompass most things ftp.

### Modules

connection manager - connection and authentication to ftp servers
downloader - handles downloading of files and directories
uploader - I think you can guess
url downloader - for downloading files via http requests given a web url
sftp downloader - for downloading via secure ftp (I haven't tested this one)
workflow manager - see more details below

------

I have tried to make each of the functions within each class within each file as modular as I can.
Doing so results in the functions not being very capable, for example the downloader function will not connect to
the ftp. The benefits of this are that the purpose of each function is very clear. This is why I have also built the workflow manager.

-------

### Workflow Manager:

Serves as the control hub for FTP tasks. It doesn't perform tasks but orchestrates them. Below is a quick guide on how to use it:

1. Initialization: Instantiate FTPWorkflowManager with an optional logger for writing to log file.

2. Download: Use connect_and_download to connect, authenticate, download a file, and disconnect all in one call.

workflow_manager = FTPWorkflowManager(logger=my_logger) #1 

success = workflow_manager.connect_and_download(ip_address, remote_path, file_name, local_dir) #2 

    ip_address: FTP server IP
    remote_path: Remote folder path
    file_name: File to download
    local_dir: Local destination folder


The functions return True if successful, False otherwise.