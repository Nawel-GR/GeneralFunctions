import json
import pandas as pd
import subprocess
import os

def subir_dataframe_a_postgres_shell_windows(df, cred_file="sql_cred.json", table_name="public.transaccion"):
    """
    Sube un DataFrame de Pandas a una tabla en PostgreSQL sin generar un archivo CSV, usando `psql` desde la shell.

    Parámetros:
    - df: pandas.DataFrame con los datos a subir.
    - cred_file: Ruta al archivo JSON con las credenciales ('host', 'user', 'password', 'dbname').
    - table_name: Nombre de la tabla en PostgreSQL (ejemplo: 'public.transaccion').

    Retorna:
    - True si la operación fue exitosa, False si hubo un error.
    """

    # Cargar credenciales desde el archivo JSON
    try:
        with open(cred_file, "r") as f:
            credentials = json.load(f)
    except Exception as e:
        print("Error al cargar credenciales:", e)
        return False

    # Convertir el DataFrame a CSV en formato STRING
    csv_data = df.to_csv(index=False, sep=";", header=True, encoding="utf-8", na_rep="NULL")

    # Construir el comando `psql`
    command = [
        "psql",
        "-h", credentials["host"],
        "-U", credentials["user"],
        "-d", credentials["dbname"],
        "-c",
        f"COPY {table_name} FROM STDIN WITH DELIMITER ';' CSV HEADER NULL 'NULL' ENCODING 'UTF8';"
    ]

    # Configurar el entorno para usar `PGPASSWORD`
    env = os.environ.copy()
    env["PGPASSWORD"] = credentials["password"]

    # Ejecutar `psql` usando `subprocess.run` con `input`
    process = subprocess.run(
        command,
        input=csv_data,  # Ahora es una cadena `str`
        text=True,
        env=env,
        capture_output=True
    )

    # Verificar el resultado
    if process.returncode == 0:
        print("Datos subidos correctamente a", table_name)
        return True
    else:
        print("Error al subir los datos:")
        print("STDERR:", process.stderr)
        print("STDOUT:", process.stdout)
        return False


def subir_dataframe_a_postgres_shell_linux(df, cred_file="sql_cred.json", table_name="public.transaccion"):
    """
    Sube un DataFrame de Pandas a una tabla en PostgreSQL sin generar un archivo CSV, usando `psql` desde la shell.
    
    Modificaciones para Linux:
    - Se pasa `PGPASSWORD` en línea con `psql` para evitar problemas de permisos.
    - Se usa `shell=True` para manejar correctamente la ejecución del comando.
    - Se usa `capture_output=True` para capturar errores correctamente.
    """

    # Cargar credenciales desde el archivo JSON
    try:
        with open(cred_file, "r") as f:
            credentials = json.load(f)
    except Exception as e:
        print("Error al cargar credenciales:", e)
        return False

    # Convertir el DataFrame a CSV en formato STRING
    csv_data = df.to_csv(index=False, sep=";", header=True, encoding="utf-8", na_rep="NULL")

    # Construir el comando `psql` con `PGPASSWORD`
    command = f"PGPASSWORD='{credentials['password']}' psql -h {credentials['host']} -U {credentials['user']} -d {credentials['dbname']} -c \"COPY {table_name} FROM STDIN WITH DELIMITER ';' CSV HEADER NULL 'NULL' ENCODING 'UTF8';\""

    # Ejecutar `psql` usando `subprocess.run`
    process = subprocess.run(
        command,
        input=csv_data,
        text=True,
        shell=True,
        capture_output=True
    )

    # Verificar el resultado
    if process.returncode == 0:
        print("Datos subidos correctamente a", table_name)
        return True
    else:
        print("Error al subir los datos:")
        print("STDERR:", process.stderr)
        print("STDOUT:", process.stdout)
        return False
