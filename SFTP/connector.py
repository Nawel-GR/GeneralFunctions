import paramiko


"""Connector class to connect to a SFTP server and manage files

"""

# Conector class
class Connector:
    def __init__(self, host, username, password, port, download_path, DEBUG=False):
        """ Constructor
        host: str -> Hostname or IP address of the SFTP server
        username: str -> Username to connect to the SFTP server
        password: str -> Password to connect to the SFTP server
        port: int -> Port to connect to the SFTP server
        download_path: str -> Local Path to download the files        
        """
        self.host = host
        self.username = username
        self.password = password
        self.port = port
        self.ssh_client = paramiko.SSHClient()
        self.ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        self.ftp = None
        self.download_path = download_path
        self.DEBUG = DEBUG

    def connect(self):
        """ Connect to the SFTP server """
        if self.DEBUG: print("Connecting to SFTP Server...")
    
        try:
            self.ssh_client.connect(hostname=self.host, port=self.port, username=self.username, password=self.password)
            self.ftp = self.ssh_client.open_sftp()
            return 1
        
        except Exception as e:
            print(f'Error connecting to the SFTP server: {e}')
            self.close()
            return 0

    def close(self):
        """ Close the connection """
        if self.DEBUG: print("Clossing Connection...")

        try:
            self.ftp.close()
            self.ssh_client.close()
            return 1
        
        except Exception as e:
            print(f'Error closing the connection: {e}')
            return 0

    def change_directory(self, path):
        """ Change the ftp directory 
    
        path: str -> Path to change the directory
        """
        if self.DEBUG: print(f"Changing directory to {path}")

        try:
            self.ftp.chdir(path)
            return 1
        
        except Exception as e:
            print(f'Error changing the directory: {e}')
            return 0

    def download_file(self, remote_path):
        """Download a file from the SFTP server
        remote_path: str -> Path of the file in the SFTP server (with the filename)
        """
        if self.DEBUG: print(f"Downloading file {remote_path}")

        try:
            self.ftp.get(remote_path, self.download_path)
            return 1
        
        except Exception as e:
            print(f'Error downloading the file: {e}')
            self.close()
            return 0
        
    def put_file(self, local_path, remote_path):
        """Upload a file to the SFTP server
        local_path: str -> Local path of the file to upload
        remote_path: str -> Path of the file in the SFTP server"""
        if self.DEBUG: print(f"Uploading file {local_path} to {remote_path}")

        try:
            self.ftp.put(local_path, remote_path)   
            return 1
        
        except Exception as e:
            print(f'Error uploading the file: {e}')
            self.close()
            return 0

    def list_files(self, path):
        """List the files in the SFTP server"""
        if self.DEBUG: print(f"Listing files in {path}")
        
        try:
            return self.ftp.listdir(path)

        except Exception as e:
            print(f'Error listing the files: {e}')
            return 0