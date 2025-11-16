"""
Script para crear y poblar la base de datos SQLite usada por la aplicación.
Crea: data/distribuidora.db
- Tablas: Roles, Permisos, Usuarios, RolPermisos
- Inserta permisos básicos, rol Administrador, usuario admin (admin/admin123) y un usuario de ejemplo

Ejecución:
    python scripts/create_distribuidora_db.py

"""
import sqlite3
import hashlib
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DB_PATH = ROOT / 'data' / 'distribuidora.db'

PERMISOS = [
    ('ver_ventas', 'Ver ventas', 'ventas'),
    ('crear_ventas', 'Crear ventas', 'ventas'),
    ('editar_ventas', 'Editar ventas', 'ventas'),
    ('eliminar_ventas', 'Eliminar ventas', 'ventas'),
    ('ver_compras', 'Ver compras', 'compras'),
    ('crear_compras', 'Crear compras', 'compras'),
    ('editar_compras', 'Editar compras', 'compras'),
    ('eliminar_compras', 'Eliminar compras', 'compras'),
    ('ver_productos', 'Ver productos', 'inventario'),
    ('crear_productos', 'Crear productos', 'inventario'),
    ('editar_productos', 'Editar productos', 'inventario'),
    ('eliminar_productos', 'Eliminar productos', 'inventario'),
    ('ver_usuarios', 'Ver usuarios', 'usuarios'),
    ('crear_usuarios', 'Crear usuarios', 'usuarios'),
    ('editar_usuarios', 'Editar usuarios', 'usuarios'),
    ('eliminar_usuarios', 'Eliminar usuarios', 'usuarios'),
    ('ver_reportes', 'Ver reportes', 'reportes'),
    ('ver_configuracion', 'Ver configuración', 'configuracion'),
    ('editar_configuracion', 'Editar configuración', 'configuracion'),
    ('admin_completo', 'Acceso completo de administrador', 'sistema'),
]


def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()


def ensure_db():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(DB_PATH))
    cur = conn.cursor()

    # Crear tablas
    cur.execute('''
    CREATE TABLE IF NOT EXISTS Roles (
        RolID INTEGER PRIMARY KEY AUTOINCREMENT,
        Nombre TEXT NOT NULL
    )
    ''')

    cur.execute('''
    CREATE TABLE IF NOT EXISTS Permisos (
        PermisoID INTEGER PRIMARY KEY AUTOINCREMENT,
        Nombre TEXT NOT NULL,
        Descripcion TEXT,
        Modulo TEXT
    )
    ''')

    cur.execute('''
    CREATE TABLE IF NOT EXISTS Usuarios (
        UsuarioID INTEGER PRIMARY KEY AUTOINCREMENT,
        NombreUsuario TEXT NOT NULL,
        ClaveHash TEXT NOT NULL,
        RolID INTEGER,
        EmpleadoID INTEGER,
        Estado INTEGER NOT NULL DEFAULT 1
    )
    ''')

    cur.execute('''
    CREATE TABLE IF NOT EXISTS RolPermisos (
        RolPermisoID INTEGER PRIMARY KEY AUTOINCREMENT,
        RolID INTEGER NOT NULL,
        PermisoID INTEGER NOT NULL
    )
    ''')

    cur.execute('''
    CREATE TABLE IF NOT EXISTS Productos (
        ProductoID INTEGER PRIMARY KEY AUTOINCREMENT,
        Nombre TEXT NOT NULL,
        Descripcion TEXT,
        Precio REAL NOT NULL,
        Stock INTEGER NOT NULL DEFAULT 0,
        CodigoBarras TEXT,
        Activo INTEGER NOT NULL DEFAULT 1
    )
    ''')

    cur.execute('''
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
    ''')

    cur.execute('''
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
    ''')

    conn.commit()
    conn.close()


def seed_data():
    conn = sqlite3.connect(str(DB_PATH))
    cur = conn.cursor()

    # Insertar permisos
    cur.execute("SELECT COUNT(*) FROM Permisos")
    if cur.fetchone()[0] == 0:
        cur.executemany(
            "INSERT INTO Permisos (Nombre, Descripcion, Modulo) VALUES (?, ?, ?)",
            PERMISOS
        )
        print(f"Insertados {len(PERMISOS)} permisos")
    else:
        print("Permisos ya existentes, no se insertaron nuevos")

    # Crear rol Administrador si no existe
    cur.execute("SELECT RolID FROM Roles WHERE Nombre = ?", ('Administrador',))
    r = cur.fetchone()
    if r:
        rol_admin_id = r[0]
        print("Rol Administrador ya existe (ID={})".format(rol_admin_id))
    else:
        cur.execute("INSERT INTO Roles (Nombre) VALUES (?)", ('Administrador',))
        rol_admin_id = cur.lastrowid
        print("Rol Administrador creado (ID={})".format(rol_admin_id))

    # Asignar todos los permisos al rol Administrador
    cur.execute("SELECT PermisoID FROM Permisos")
    permisos_ids = [row[0] for row in cur.fetchall()]
    asignados = 0
    for pid in permisos_ids:
        cur.execute("SELECT COUNT(*) FROM RolPermisos WHERE RolID = ? AND PermisoID = ?", (rol_admin_id, pid))
        if cur.fetchone()[0] == 0:
            cur.execute("INSERT INTO RolPermisos (RolID, PermisoID) VALUES (?, ?)", (rol_admin_id, pid))
            asignados += 1
    if asignados:
        print(f"Asignados {asignados} permisos al rol Administrador")
    else:
        print("Rol Administrador ya tenía asignados los permisos")

    # Crear usuario admin
    cur.execute("SELECT UsuarioID FROM Usuarios WHERE NombreUsuario = ?", ('admin',))
    if cur.fetchone():
        print("Usuario 'admin' ya existe")
    else:
        password = 'admin123'
        h = hash_password(password)
        cur.execute("INSERT INTO Usuarios (NombreUsuario, ClaveHash, RolID, Estado) VALUES (?, ?, ?, 1)",
                    ('admin', h, rol_admin_id))
        print("Usuario 'admin' creado con contraseña: admin123")

    # Crear usuario de ejemplo 'juan'
    cur.execute("SELECT UsuarioID FROM Usuarios WHERE NombreUsuario = ?", ('juan',))
    if not cur.fetchone():
        password = 'miPassword123'
        h = hash_password(password)
        # crear rol Empleado si no existe
        cur.execute("SELECT RolID FROM Roles WHERE Nombre = ?", ('Empleado',))
        rr = cur.fetchone()
        if rr:
            rol_emp = rr[0]
        else:
            cur.execute("INSERT INTO Roles (Nombre) VALUES (?)", ('Empleado',))
            rol_emp = cur.lastrowid
            print(f"Rol Empleado creado (ID={rol_emp})")

        cur.execute("INSERT INTO Usuarios (NombreUsuario, ClaveHash, RolID, Estado) VALUES (?, ?, ?, 1)",
                    ('juan', h, rol_emp))
        print("Usuario 'juan' creado con contraseña: miPassword123")
    else:
        print("Usuario 'juan' ya existe")

    # Crear productos de ejemplo
    cur.execute("SELECT COUNT(*) FROM Productos")
    if cur.fetchone()[0] == 0:
        productos = [
            ('Producto A', 'Descripción del producto A', 100.00, 50, 'BAR001', 1),
            ('Producto B', 'Descripción del producto B', 250.00, 30, 'BAR002', 1),
            ('Producto C', 'Descripción del producto C', 75.50, 100, 'BAR003', 1),
            ('Producto D', 'Descripción del producto D', 500.00, 10, 'BAR004', 1),
            ('Producto E', 'Descripción del producto E', 150.00, 45, 'BAR005', 1),
        ]
        cur.executemany(
            "INSERT INTO Productos (Nombre, Descripcion, Precio, Stock, CodigoBarras, Activo) VALUES (?, ?, ?, ?, ?, ?)",
            productos
        )
        print(f"Insertados {len(productos)} productos de ejemplo")
    else:
        print("Productos ya existentes, no se insertaron nuevos")

    conn.commit()
    conn.close()


def verify():
    conn = sqlite3.connect(str(DB_PATH))
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM Roles")
    roles = cur.fetchone()[0]
    cur.execute("SELECT COUNT(*) FROM Permisos")
    permisos = cur.fetchone()[0]
    cur.execute("SELECT COUNT(*) FROM Usuarios")
    usuarios = cur.fetchone()[0]
    cur.execute("SELECT COUNT(*) FROM RolPermisos")
    rp = cur.fetchone()[0]
    cur.execute("SELECT COUNT(*) FROM Productos")
    productos = cur.fetchone()[0]
    cur.execute("SELECT COUNT(*) FROM Facturas")
    facturas = cur.fetchone()[0]
    conn.close()
    print('\nResumen:')
    print(f"Roles: {roles}")
    print(f"Permisos: {permisos}")
    print(f"Usuarios: {usuarios}")
    print(f"RolPermisos: {rp}")
    print(f"Productos: {productos}")
    print(f"Facturas: {facturas}")


if __name__ == '__main__':
    ensure_db()
    seed_data()
    verify()
    print("\nBase de datos creada en:", DB_PATH)
