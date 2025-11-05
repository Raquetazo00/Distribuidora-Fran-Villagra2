import pyodbc

def conectar():
    """Establece conexión con SQL Server"""
    try:
        conexion = pyodbc.connect(
            'DRIVER={ODBC Driver 17 for SQL Server};'
            'SERVER=localhost\\SQLEXPRESS;'
            'DATABASE=Distribuidora;'
            'Trusted_Connection=yes;'
        )
        return conexion
    except pyodbc.Error as error:
        print(f"Error al conectar con SQL Server: {error}")
        return None
    except Exception as error:
        print(f"Error inesperado: {error}")
        return None

def cerrar_conexion(conexion):
    """Cierra la conexión"""
    if conexion:
        conexion.close()
        print("Conexión cerrada")

def ejecutar_consulta(consulta, parametros=None):
    """
    Ejecuta una consulta SQL genérica
    
    Args:
        consulta: Consulta SQL a ejecutar
        parametros: Tupla o lista de parámetros (opcional)
    
    Returns:
        Resultados de la consulta si es SELECT, o número de filas afectadas
    """
    conexion = conectar()
    if not conexion:
        return None
    
    try:
        cursor = conexion.cursor()
        if parametros:
            cursor.execute(consulta, parametros)
        else:
            cursor.execute(consulta)
        
        if consulta.strip().upper().startswith('SELECT'):
            resultados = cursor.fetchall()
            return resultados
        else:
            conexion.commit()
            return cursor.rowcount
    except pyodbc.Error as error:
        print(f"Error al ejecutar consulta: {error}")
        conexion.rollback()
        return None
    finally:
        cerrar_conexion(conexion)

# Ejemplo de uso
if __name__ == "__main__":
    # Prueba la conexión
    conexion = conectar()
    if conexion:
        print("Conexión exitosa a SQL Server")
        cerrar_conexion(conexion)
    
    # Ejemplo de consulta
    # resultados = ejecutar_consulta("SELECT * FROM Usuarios")
    # print(resultados)