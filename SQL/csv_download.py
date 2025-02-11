import json
import os
import subprocess

def descargar(fecha_hoy, output_path, DEBUG=True):
    """Descarga la información de la base de datos y la guarda en un archivo CSV."""

    # Cargar las credenciales desde el archivo JSON
    with open('credentials.json') as f:
        credentials = json.load(f)

    # crea la ruta si no existe
    try:
        os.mkdir(f"{output_path}/csv")
    except FileExistsError:
        pass

    # Nombre del archivo CSV de salida
    output_file = f'{output_path}/csv/cartera_experiencia_{fecha_hoy}.csv'

    # Comando a ejecutar
    command = f'psql -h {credentials["host"]} -U {credentials["user"]} -d {credentials["dbname"]} -c "\\COPY (SELECT * FROM stg_comercial.v_cartera_experiencia LIMIT 10) TO \'{output_file}\' WITH CSV HEADER ENCODING \'LATIN1\'"' # Windows
    #command = f"PGPASSWORD={credentials['password']} psql -h {credentials['host']} -U {credentials['user']} -d {credentials['dbname']} -c \"\\COPY (SELECT * FROM stg_comercial.v_cartera_experiencia WHERE email IS NOT NULL AND email ~ '^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\\.[A-Za-z]{{2,}}$') TO STDOUT WITH CSV HEADER\" > {output_file}"
    try:
        # Ejecutar el comando
        subprocess.run(command, shell=True, check=True)
        if DEBUG: print(f'Datos exportados a {output_file} exitosamente.')

    except subprocess.CalledProcessError as e:
        print(f'Error al ejecutar el comando: {e}')
        return 0, e

    except Exception as e:
        print(f'Error: {e}')
        return 0, e

    if DEBUG: print(f'Archivo CSV generado con éxito en {output_file}')

    return 1, 'Exito'