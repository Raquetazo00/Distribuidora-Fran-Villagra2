"""Módulo de conexión para SQLite.

Comportamiento:
- Usa exclusivamente SQLite (archivo local `data/distribuidora.db`).
- Crea las tablas automáticamente si no existen.

Funciones exportadas:
- conectar() -> conexión SQLite o None
- cerrar_conexion(conexion)
- ejecutar_consulta(consulta, parametros=None) -> lista de filas (SELECT) o rowcount (DML)
"""

import os
import sqlite3
import traceback
from pathlib import Path

# Configuración SQLite
_SQLITE_DB_PATH = os.environ.get('SQLITE_DB_PATH', os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'distribuidora.db'))
_BACKEND = 'sqlite'


def _ensure_sqlite_db():
    """Asegura que exista el directorio y crea el esquema mínimo si es necesario."""
    db_path = Path(_SQLITE_DB_PATH)
    db_path.parent.mkdir(parents=True, exist_ok=True)

    conn = sqlite3.connect(str(db_path))
    try:
        cur = conn.cursor()
        # Crear tablas mínimas si no existen
        cur.execute("""
        CREATE TABLE IF NOT EXISTS Roles (
            RolID INTEGER PRIMARY KEY AUTOINCREMENT,
            Nombre TEXT NOT NULL
        )
        """)

        cur.execute("""
        CREATE TABLE IF NOT EXISTS Permisos (
            PermisoID INTEGER PRIMARY KEY AUTOINCREMENT,
            Nombre TEXT NOT NULL,
            Descripcion TEXT,
            Modulo TEXT
        )
        """)

        cur.execute("""
        CREATE TABLE IF NOT EXISTS Usuarios (
            UsuarioID INTEGER PRIMARY KEY AUTOINCREMENT,
            NombreUsuario TEXT NOT NULL,
            ClaveHash TEXT NOT NULL,
            RolID INTEGER,
            EmpleadoID INTEGER,
            Estado INTEGER NOT NULL DEFAULT 1
        )
        """)

        cur.execute("""
        CREATE TABLE IF NOT EXISTS RolPermisos (
            RolPermisoID INTEGER PRIMARY KEY AUTOINCREMENT,
            RolID INTEGER NOT NULL,
            PermisoID INTEGER NOT NULL
        )
        """)

        cur.execute("""
        CREATE TABLE IF NOT EXISTS Productos (
            ProductoID INTEGER PRIMARY KEY AUTOINCREMENT,
            Nombre TEXT NOT NULL,
            Descripcion TEXT,
            Precio REAL NOT NULL,
            Stock INTEGER NOT NULL DEFAULT 0,
            CodigoBarras TEXT,
            Activo INTEGER NOT NULL DEFAULT 1
        )
        """)

        cur.execute("""
        CREATE TABLE IF NOT EXISTS Facturas (
            FacturaID INTEGER PRIMARY KEY AUTOINCREMENT,
            NumeroFactura TEXT NOT NULL UNIQUE,
            FechaFactura DATETIME NOT NULL,
            ClienteNombre TEXT NOT NULL,
            ClienteCI TEXT,
            ClienteTelefono TEXT,
            ClienteEmail TEXT,
            Total REAL NOT NULL,
            UsuarioID INTEGER,
            CAE TEXT,
            VtoCae TEXT,
            Estado TEXT NOT NULL DEFAULT 'completada'
        )
        """)

        cur.execute("""
        CREATE TABLE IF NOT EXISTS DetallesFactura (
            DetalleID INTEGER PRIMARY KEY AUTOINCREMENT,
            FacturaID INTEGER NOT NULL,
            ProductoID INTEGER NOT NULL,
            Cantidad INTEGER NOT NULL,
            PrecioUnitario REAL NOT NULL,
            Subtotal REAL NOT NULL,
            FOREIGN KEY (FacturaID) REFERENCES Facturas(FacturaID),
            FOREIGN KEY (ProductoID) REFERENCES Productos(ProductoID)
        )
        """)

        conn.commit()
    finally:
        conn.close()


def conectar():
    """Devuelve una conexión al SQLite.

    Retorna None si no puede conectarse.
    """
    try:
        _ensure_sqlite_db()
        conn = sqlite3.connect(str(Path(_SQLITE_DB_PATH)))
        # Habilitar acceso por nombre de columna si se desea
        return conn
    except Exception as error:
        print(f"Error al conectar con SQLite: {error}")
        traceback.print_exc()
        return None


def cerrar_conexion(conexion):
    """Cierra la conexión (sqlite3)."""
    try:
        if conexion:
            conexion.close()
    except Exception:
        pass



def ejecutar_consulta(consulta, parametros=None):
    """Ejecuta una consulta genérica y devuelve filas para SELECT o rowcount para DML.

    parametros debe ser una tupla o lista. Usa '?' como placeholder (compatible con sqlite).
    """
    conexion = conectar()
    if not conexion:
        return None

    try:
        cur = conexion.cursor()
        if parametros:
            cur.execute(consulta, parametros)
        else:
            cur.execute(consulta)

        if consulta.strip().upper().startswith('SELECT'):
            resultados = cur.fetchall()
            return resultados
        else:
            conexion.commit()
            return cur.rowcount
    except Exception as error:
        print(f"Error al ejecutar consulta: {error}")
        try:
            conexion.rollback()
        except Exception:
            pass
        traceback.print_exc()
        return None
    finally:
        cerrar_conexion(conexion)

if __name__ == '__main__':
    # Prueba de conexión rápida
    conn = conectar()
    if conn:
        print(f"Conectado usando backend: {_BACKEND}")
        cerrar_conexion(conn)
