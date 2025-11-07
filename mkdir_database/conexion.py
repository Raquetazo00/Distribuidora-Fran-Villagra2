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


def obtener_productos():
    """Obtiene todos los productos activos"""
    conn = conectar()  # ✅ corregido (antes decía conexion())
    if not conn:
        print("No se pudo conectar a la base de datos")
        return []

    try:
        cursor = conn.cursor()
        cursor.execute("SELECT ProductoID, Nombre, Precio, Stock FROM Productos")
        productos = cursor.fetchall()
        return productos
    except pyodbc.Error as error:
        print(f"Error al obtener productos: {error}")
        return []
    finally:
        conn.close()


def descontar_stock(producto_id, cantidad):
    """Descuenta stock de un producto"""
    conn = conectar()
    if not conn:
        print("No se pudo conectar a la base de datos")
        return

    try:
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE dbo.Productos
            SET Stock = Stock - ?
            WHERE ProductoID = ? AND Stock >= ?
        """, (cantidad, producto_id, cantidad))
        conn.commit()
    except pyodbc.Error as error:
        print(f"Error al descontar stock: {error}")
        conn.rollback()
    finally:
        conn.close()


# Prueba manual (solo si ejecutás este archivo directamente)
if __name__ == "__main__":
    conexion = conectar()
    if conexion:
        print("Conexión exitosa a SQL Server")
        cerrar_conexion(conexion)

    productos = obtener_productos()
    for p in productos:
        print(p)
