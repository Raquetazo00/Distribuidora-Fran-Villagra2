# Sistema de Distribuidora

Sistema de gestión para distribuidora desarrollado con Python, Kivy y SQL Server.

## 📋 Requisitos del Sistema

### Software Requerido

1. **Python 3.13.7** o superior
   - Descarga desde: https://www.python.org/downloads/
   - Durante la instalación, marca la opción "Add Python to PATH"

2. **SQL Server Express** (o superior)
   - Descarga desde: https://www.microsoft.com/sql-server/sql-server-downloads
   - Incluye SQL Server Management Studio (SSMS)

3. **ODBC Driver para SQL Server**
   - Descarga desde: https://learn.microsoft.com/sql/connect/odbc/download-odbc-driver-for-sql-server
   - Necesario para la conexión con pyodbc

## 🚀 Instalación

### 1. Clonar o descargar el repositorio

git clone <url-del-repositorio>
cd Distribuidora-Fran-Villagra2### 2. Instalar dependencias de Python

Abre PowerShell o CMD en la carpeta del proyecto y ejecuta:

# Instalar Kivy (framework de interfaz gráfica)
pip install kivy

# Instalar pyodbc (conector para SQL Server)
pip install pyodbc

# O instalar todas las dependencias de una vez
pip install kivy pyodbc**Nota:** Si tienes problemas con pyodbc, asegúrate de tener instalado el ODBC Driver para SQL Server.

### 3. Configurar SQL Server

1. **Asegúrate de que SQL Server esté ejecutándose:**
   - Abre "Servicios" en Windows
   - Busca "SQL Server (SQLEXPRESS)" o el nombre de tu instancia
   - Verifica que esté "En ejecución"

2. **Crear la base de datos:**
   - Abre SQL Server Management Studio (SSMS)
   - Conéctate a tu servidor (ej: `DESKTOP-1RNSV4J\SQLEXPRESS`)
   - Ejecuta el script SQL que crea la base de datos `DistribuidoraDB`
   - Ejecuta el script que crea todas las tablas

3. **Configurar permisos:**
   - Ejecuta el script SQL para crear la tabla de Permisos y RolPermisos
   - Asigna los permisos a los roles correspondientes

### 4. Configurar la conexión

Edita el archivo `mkdir_database/conexion.py` y ajusta los siguientes parámetros:
ython
'SERVER=DESKTOP-1RNSV4J\\SQLEXPRESS;'  # Cambia por tu servidor
'DATABASE=DistribuidoraDB;'            # Nombre de tu base de datos
'Trusted_Connection=yes;'               # O usa usuario/contraseña**Si usas autenticación de SQL Server en lugar de Windows:**n
'UID=tu_usuario;'
'PWD=tu_contraseña;'## 📦 Dependencias de Python

El proyecto requiere las siguientes librerías:

- **kivy** (>=2.3.0) - Framework para interfaces gráficas
- **pyodbc** (>=5.0.0) - Conector ODBC para SQL Server

### Instalación con requirements.txt (recomendado)

Crea un archivo `requirements.txt` con el siguiente contenido:

```
kivy>=2.3.0
pyodbc>=5.0.0
```

### 2. Instalar dependencias de Python

Abre PowerShell o CMD en la carpeta del proyecto y ejecuta:


**Nota:** Si tienes problemas con pyodbc, asegúrate de tener instalado el ODBC Driver para SQL Server.

### 3. Configurar SQL Server

1. **Asegúrate de que SQL Server esté ejecutándose:**
   - Abre "Servicios" en Windows
   - Busca "SQL Server (SQLEXPRESS)" o el nombre de tu instancia
   - Verifica que esté "En ejecución"

2. **Crear la base de datos:**
   - Abre SQL Server Management Studio (SSMS)
   - Conéctate a tu servidor (ej: `DESKTOP-1RNSV4J\SQLEXPRESS`)
   - Ejecuta el script SQL que crea la base de datos `DistribuidoraDB`
   - Ejecuta el script que crea todas las tablas

3. **Configurar permisos:**
   - Ejecuta el script SQL para crear la tabla de Permisos y RolPermisos
   - Asigna los permisos a los roles correspondientes

### 4. Configurar la conexión

Edita el archivo `mkdir_database/conexion.py` y ajusta los siguientes parámetros:
ython
'SERVER=DESKTOP-1RNSV4J\\SQLEXPRESS;'  # Cambia por tu servidor
'DATABASE=DistribuidoraDB;'            # Nombre de tu base de datos
'Trusted_Connection=yes;'               # O usa usuario/contraseña
cación de Windows** por defecto. Si usas autenticación de SQL Server, cambia `Trusted_Connection=yes` por `UID` y `PWD`.
- Las contraseñas se almacenan con hash SHA256 en la base de datos.
- El sistema requiere que existan roles y permisos en la base de datos antes de iniciar sesión.

## 👥 Roles del Sistema

Los roles disponibles son:
- **Administrador**: Acceso completo al sistema
- **Vendedor**: Puede ver y crear ventas
- **Almacenista**: Gestiona inventario y compras
- **Gerente**: Acceso a reportes y configuración

## 📄 Licencia

[Especificar licencia si aplica]

## 👨‍💻 Desarrollo

Para contribuir al proyecto:
1. Fork el repositorio
2. Crea una rama para tu feature
3. Realiza tus cambios
4. Envía un pull request

'UID=tu_usuario;'
'PWD=tu_contraseña;'

Distribuidora-Fran-Villagra2/
├── main.py                          # Punto de entrada principal
├── App.kv                           # Archivo KV principal (opcional)
├── README.md                        # Este archivo
├── mkdir_database/                  # Módulo de base de datos
│   ├── conexion.py                  # Conexión a SQL Server
│   └── permisos.py                  # Gestión de permisos y roles
└── mkdir_pantallas/                 # Pantallas/interfaces
    ├── login.py                     # Pantalla de login
    └── login_sc.kv                  # Interfaz gráfica del login



