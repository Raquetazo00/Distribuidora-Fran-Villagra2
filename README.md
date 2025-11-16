# Sistema de Distribuidora - Guía de Uso

Sistema de gestión para distribuidora desarrollado con **Python**, **Kivy** y **SQLite**.

## ✅ Estado del Sistema

**¡Completamente funcional y listo para usar!**

Características implementadas:
- ✅ Autenticación de usuarios
- ✅ Búsqueda de productos en tiempo real
- ✅ Carrito de compras con cantidades
- ✅ Transferencia de productos menú → facturación
- ✅ Datos del cliente (nombre, apellido, teléfono, email, C.I.)
- ✅ Generación de facturas con BD SQLite
- ✅ Integración AFIP (modo testing)
- ✅ Sistema de validaciones

---

## 🚀 Inicio Rápido

### 1. Requisitos Previos

```bash
# Python 3.13.7 o superior
python --version

# Instalar dependencias
pip install kivy
```

### 2. Ejecutar la aplicación

```bash
python main.py
```

### 3. Credenciales de prueba

```
Usuario: admin
Contraseña: admin123
```

O

```
Usuario: juan
Contraseña: miPassword123
```

---

## 📖 Guía de Uso

### Menú Principal
1. **Buscar productos**: Escribe el nombre o código de barras
2. **Agregar al carrito**: Haz clic en "Agregar"
3. **Ajustar cantidades**: Usa botones +/-
4. **Previsualizar**: Haz clic en "Previsualizar Venta"

### Facturación
1. **Datos del cliente**: 
   - Nombre (requerido)
   - Apellido (requerido)
   - Teléfono (requerido)
   - Email (requerido, debe tener @)
   - C.I./RUT (requerido)

2. **Generar factura**: Haz clic en "Generar Factura"
   - Se guardará en la BD SQLite
   - Se mostrará el número de factura generado
   - Incluye CAE (en testing: "12345678901234")

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
'PWD=tu_contraseña;'

---

## 📦 Dependencias

### Instaladas y Funcionando
```
kivy>=2.3.0          # UI Framework
sqlite3              # Base de datos (built-in)
hashlib              # SHA256 (built-in)
datetime             # Timestamps (built-in)
```

### Instalar
```bash
pip install kivy
```

---

## 🗄️ Base de Datos

### Ubicación
```
data/distribuidora.db
```

### Tablas principales
- **Usuarios**: Cuentas de login
- **Roles**: Admin, Empleado
- **Permisos**: Control de acceso
- **Productos**: Catálogo
- **Facturas**: Histórico de ventas
- **DetallesFactura**: Líneas de facturas

### Campos de Cliente (Facturas)
- ClienteNombre
- ClienteCI
- **ClienteTelefono** (Nuevo)
- **ClienteEmail** (Nuevo)
- Total
- CAE (AFIP)
- VtoCae (Vencimiento AFIP)

---

## 🔧 Troubleshooting

### "Error al conectar con la BD"
```bash
# Regenerar BD
python scripts/create_distribuidora_db.py
```

### Productos no aparecen
- Prueba con búsquedas exactas: "Producto A"
- Verifica stock > 0

### Limpiar caché Kivy
```bash
Remove-Item -Path "$env:USERPROFILE\.kivy" -Recurse -Force
python main.py
```

---

## 🧪 Testing

Ejecutar tests de integración:
```bash
python test_afip_integration.py
```

Verifica:
- ✅ Importación módulos
- ✅ Esquema BD
- ✅ Campos CAE/VtoCae
- ✅ Integración facturación

---

## 🔐 Seguridad

- Contraseñas: SHA256 hash
- BD local: Sin credenciales SQL Server
- Validaciones: Todos los inputs
- AFIP modo testing (sin conexión real)

---

## 📋 Estructura de Archivos

```
.
├── main.py                    # Punto de entrada
├── App.kv                     # Config UI global
│
├── mkdir_database/
│   ├── conexion.py           # SQLite
│   ├── afip_wsfe.py          # AFIP (testing)
│   ├── permisos.py           # Sistema permisos
│   └── verificar_usuarios.py # Auth
│
├── mkdir_pantallas/
│   ├── login*                # Login
│   ├── menu_principal*       # Menú
│   ├── facturacion*          # Facturas
│   ├── panel_admin*          # Admin
│   ├── styles.kv             # Estilos
│   └── crear_usuario*        # Usuarios
│
├── scripts/
│   └── create_distribuidora_db.py  # Init BD
│
├── data/
│   └── distribuidora.db      # SQLite
│
├── certificados/             # AFIP producción (futuro)
│   ├── cert.crt
│   └── key.key
│
├── AFIP_SETUP.md            # AFIP docs
└── test_afip_integration.py # Tests
```

---

## 👨‍💻 Desarrollo

### Para extender:
1. Edita archivos `.kv` para UI
2. Edita archivos `.py` para lógica
3. Ejecuta `python main.py` para probar

### Para agregar productos:
```bash
# Edita create_distribuidora_db.py
python scripts/create_distribuidora_db.py
```

---

## 📞 Notas Importantes

- **AFIP**: Actualmente en modo testing (CAE simulado)
- **Certificados**: Para producción, coloca en `certificados/`
- **pyafipws**: Tiene issue en Windows, funciona sin él
- **SQLite**: No requiere servidor externo
- **Base de datos**: Se crea automáticamente en primera ejecución

---

## ✅ Checklist de Funcionalidades

- [x] Login con autenticación
- [x] Búsqueda de productos
- [x] Carrito de compras
- [x] Transferencia menú → facturación
- [x] Datos cliente (nombre, apellido, teléfono, email)
- [x] Generación de facturas
- [x] BD SQLite
- [x] CAE (testing)
- [x] Validaciones completas
- [x] Sistema de estilos

---

**Versión**: 1.0 Stable  
**Base de datos**: SQLite (incluyendo certificados para AFIP futuro)  
**Estado**: ✅ Listo para producción (testing mode)


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



