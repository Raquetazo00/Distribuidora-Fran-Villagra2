import sqlite3
from hashlib import sha256
import os

DB_PATH = os.path.join(os.path.dirname(__file__), "data", "distribuidora.db")

hash_admin = sha256("admin123".encode()).hexdigest()

conn = sqlite3.connect(DB_PATH)
cur = conn.cursor()

# Crear rol si no existe
cur.execute("INSERT INTO Roles (Nombre) VALUES ('Administrador');")

# Crear usuario admin
cur.execute("""
INSERT INTO Usuarios (NombreUsuario, ClaveHash, RolID, Estado)
VALUES ('admin', ?, 1, 1);
""", (hash_admin,))

conn.commit()
conn.close()

print("✔ Usuario admin creado con éxito")
