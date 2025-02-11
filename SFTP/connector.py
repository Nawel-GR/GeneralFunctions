import paramiko
import pandas as pd
import io

class Connector:
    def __init__(self, host, username, password, port, download_path):
        self.host = host
        self.username = username
        self.password = password
        self.port = port
        self.ssh_client = paramiko.SSHClient()
        self.ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        self.ftp = None
        self.download_path = download_path

    def connect(self):
        self.ssh_client.connect(hostname=self.host, port=self.port, username=self.username, password=self.password)
        self.ftp = self.ssh_client.open_sftp()

    def close(self):
        print("Closing Connection...")
        self.ftp.close()
        self.ssh_client.close()

    def change_directory(self, path):
        self.ftp.chdir(path)

    def download_file(self, remote_path, filename):
        try:
            self.ftp.get(remote_path, f"{self.download_path}/{filename}")
        except Exception as e:
            print(f'Error downloading the file: {e}')
            self.close()
            return 0

    def put_file(self, local_path, remote_path):
        try:
            self.ftp.put(local_path, remote_path)
        except Exception as e:
            print(f'Error uploading the file: {e}')
            self.close()
            return 0

    def put_file_from_memory(self, file_content, remote_path, file_format="csv"):
        """
        Sube un archivo al servidor SFTP desde memoria.

        :param file_content: Contenido del archivo en memoria (StringIO para texto, BytesIO para binarios).
        :param remote_path: Ruta donde se guardará el archivo en el servidor.
        :param file_format: Formato del archivo ('csv' o 'excel').
        :return: 1 si tiene éxito, 0 si falla.
        """
        try:
            with self.ftp.file(remote_path, "w") as remote_file:
                if file_format == "csv":
                    remote_file.write(file_content.getvalue())  # Escribir como texto
                elif file_format == "excel":
                    remote_file.write(file_content.getvalue())  # Escribir como binario
                else:
                    raise ValueError("Formato no soportado, usa 'csv' o 'excel'.")
            return 1
        except Exception as e:
            print(f"Error subiendo el archivo desde memoria: {e}")
            return 0

    def list_files(self, path):
        return self.ftp.listdir(path)

    def move_file(self, original_path, new_path):
        try:
            self.ftp.posix_rename(original_path, new_path)
        except Exception as e:
            print(f'Error moving the file: {e}')
            self.close()
            return 0

    def download_file_to_dataframe(self, remote_path, file_format="csv", **kwargs):
        """
        Descarga un archivo desde el SFTP y lo carga en un DataFrame en memoria.

        :param remote_path: Ruta del archivo en el servidor SFTP.
        :param file_format: Formato del archivo (por defecto 'csv').
        :param kwargs: Argumentos adicionales para pandas (como `sep` para archivos CSV).
        :return: Pandas DataFrame con el contenido del archivo.
        """
        try:
            with self.ftp.file(remote_path, "r") as remote_file:
                file_content = remote_file.read().decode('utf-8')  # Leer y decodificar
                buffer = io.StringIO(file_content)  # Crear un buffer en memoria

                if file_format == "csv":
                    df = pd.read_csv(buffer, **kwargs)
                elif file_format == "excel":
                    df = pd.read_excel(io.BytesIO(remote_file.read()), **kwargs)
                else:
                    raise ValueError("Formato no soportado, usa 'csv' o 'excel'.")

                return df

        except Exception as e:
            print(f"Error al descargar el archivo como DataFrame: {e}")
            return None