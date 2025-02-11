import pyodbc

server = ''
database = ''
username = ''
password = ''
procedure = ''


# Configuración de la conexión
conn = pyodbc.connect(
    'DRIVER={SQL Server};'
    f'SERVER={server};'
    f'DATABASE={database};'
    f'UID={username};'
    f'PWD={password}'
)

# Crear un cursor
cursor = conn.cursor()

# Declarar las variables para almacenar los resultados
proceso_msg = ''
proceso_error = ''

# Cambiar a la base de datos deseada
cursor.execute(f"USE {database}")

# Declarar variables y ejecutar el procedimiento almacenado
cursor.execute(f"""
    DECLARE @Proceso_Msg nvarchar(max)
    DECLARE @Proceso_Error nvarchar(max)

    EXEC [dbo].[{procedure}] 
    @Proceso_Msg OUTPUT,
    @Proceso_Error OUTPUT

    SELECT @Proceso_Msg AS Proceso_Msg, @Proceso_Error AS Proceso_Error
""")

# Obtener los resultados
row = cursor.fetchone()
if row:
    proceso_msg = row.Proceso_Msg
    proceso_error = row.Proceso_Error

# Imprimir los resultados
print("Proceso Msg:", proceso_msg)
print("Proceso Error:", proceso_error)

# Cerrar el cursor y la conexión
cursor.close()
conn.close()
