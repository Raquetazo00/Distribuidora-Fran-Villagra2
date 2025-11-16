# Integración AFIP - Guía de Configuración

## ¿Qué es AFIP?

AFIP (Administración Federal de Ingresos Públicos) es el organismo argentino que administra el sistema de facturación electrónica. La integración permite generar facturas con Código de Autorización Electrónica (CAE) válidas.

## Modos de Operación

El sistema tiene dos modos:

### 1. **Modo Homologación (Testing)** ⚙️

- Genera facturas de prueba sin validación real en AFIP
- Devuelve un CAE simulado: `12345678901234`
- **No requiere certificados**
- **Ideal para desarrollo y pruebas**

**Activación automática**: Cuando no hay certificados en `certificados/cert.crt` y `certificados/key.key`.

### 2. **Modo Producción** 🔒

- Conecta a los servidores reales de AFIP
- Genera facturas con CAE válido
- **Requiere certificados digitales válidos**
- **Requiere CUIT registrado**

---

## Instalación de Dependencias

Para usar AFIP en modo producción, instala `pyafipws`:

```bash
pip install pyafipws
```

---

## Configuración para Producción

### Paso 1: Obtener Certificados

Los certificados digitales se obtienen del AFIP. Necesitarás:

1. **Ir a**: https://www.afip.gob.ar/
2. **Obtener**: 
   - Certificado: `cert.crt` (certificado)
   - Clave privada: `key.key` (clave privada)

### Paso 2: Colocar Certificados

Copia los archivos en la carpeta del proyecto:

```
certificados/
├── cert.crt    (certificado)
└── key.key     (clave privada)
```

La carpeta `certificados/` debe estar en la raíz del proyecto.

### Paso 3: Configurar CUIT

En el archivo `mkdir_pantallas/facturacion.py`, busca la línea:

```python
cuit = "20123456789"  # Reemplazar con CUIT real
```

Reemplázala con tu CUIT (sin guiones):

```python
cuit = "20123456789"  # Tu CUIT real de 11 dígitos
```

### Paso 4: Probar Integración

Ejecuta el script de prueba:

```bash
python -c "
from mkdir_database.afip_wsfe import AFIPIntegration
import os

# Configurar rutas
cert_path = 'certificados/cert.crt'
key_path = 'certificados/key.key'
cuit = '20123456789'  # Tu CUIT

# Probar producción (requiere certificados válidos)
afip = AFIPIntegration(cuit, cert_path, key_path, homologacion=False)
if afip.conectar():
    print('✓ Conectado a AFIP (Producción)')
    numero = afip.obtener_proximo_numero_comprobante(1, 6)
    print(f'Próximo número de factura: {numero}')
else:
    print('✗ Error conectando a AFIP')
"
```

---

## Cómo Funciona la Integración

### Flujo de Facturación

1. **Usuario ingresa datos** en la pantalla de facturación:
   - Nombre cliente
   - CI/CUIT cliente
   - Selecciona productos
   - Cantidad y precio se calculan

2. **Sistema detecta certificados**:
   - Si existen `cert.crt` y `key.key` → Modo Producción
   - Si no existen → Modo Homologación (test)

3. **Genera factura en AFIP** (si hay conexión):
   - Obtiene próximo número de comprobante
   - Envía datos de factura
   - Recibe CAE (Código de Autorización Electrónica)

4. **Guarda en BD local**:
   - Factura con CAE y fecha de vencimiento
   - Detalles de líneas (productos, cantidades, precios)

5. **Muestra confirmación** al usuario:
   - "Factura #... generada"
   - "CAE: 12345678901234 válido hasta 2024-12-31"

### Campos Agregados a Base de Datos

Se agregaron dos nuevos campos a la tabla `Facturas`:

```sql
CREATE TABLE Facturas (
    ...
    CAE TEXT,           -- Código de Autorización Electrónica
    VtoCae TEXT,        -- Fecha de vencimiento del CAE
    ...
)
```

---

## Solución de Problemas

### Error: "pyafipws not installed"

**Solución**:
```bash
pip install pyafipws
```

### Error: "Certificado no válido"

**Causas**:
- Certificado expirado
- Archivos con nombre incorrecto (deben ser exactamente `cert.crt` y `key.key`)
- Ruta incorrecta

**Solución**:
- Verificar que archivos estén en `certificados/` con nombres exactos
- Renovar certificado en AFIP si está expirado
- Revisar logs en consola para mensaje de error específico

### Error: "Conexión rechazada a AFIP"

**Causas**:
- Servidor AFIP caído
- CUIT no registrado en AFIP
- Firewall bloqueando conexión

**Solución**:
- Verificar estado de AFIP: https://www.afip.gob.ar/
- Confirmar CUIT es válido
- Revisar configuración de firewall/proxy

### Sistema genera CAE de prueba: "12345678901234"

**Significa**: 
- Certificados NO encontrados
- Sistema operando en modo Homologación
- Esto es CORRECTO para desarrollo

**Para cambiar a producción**:
- Obtener certificados reales
- Colocar en `certificados/cert.crt` y `certificados/key.key`
- Reiniciar aplicación

---

## Información del Sistema

### Archivos Modificados

1. **`mkdir_pantallas/facturacion.py`**
   - Integración AFIP en método `generar_factura()`
   - Detecta certificados automáticamente
   - Maneja errores de conexión elegantemente

2. **`mkdir_database/afip_wsfe.py`** (nuevo)
   - Clase `AFIPIntegration` para conectar a AFIP
   - Métodos: `conectar()`, `obtener_proximo_numero_comprobante()`, `generar_factura()`
   - Soporte para ambos modos: homologación y producción

3. **`scripts/create_distribuidora_db.py`**
   - Actualizada tabla `Facturas` con campos CAE y VtoCae

4. **`mkdir_database/conexion.py`**
   - Incluye creación de tablas Facturas y DetallesFactura

---

## Datos de Ejemplo para Pruebas

### CUIT de Prueba AFIP
```
CUIT: 20123456789
Razón Social: Distribuidora Test
```

### Ambiente de Pruebas (Homologación)
- No requiere certificados
- CAE devuelto: `12345678901234`
- Válido por: 30 días desde emisión (simulado)

---

## Referencias

- **AFIP**: https://www.afip.gob.ar/
- **WSFEv1 (Web Service de Facturación)**: https://www.afip.gob.ar/webservicios/
- **pyafipws Documentation**: https://github.com/permisos/pyafipws

---

## Checklist de Implementación

- [ ] Instalar `pyafipws` (si usarás producción)
- [ ] Obtener certificados digitales de AFIP
- [ ] Colocar certificados en `certificados/` folder
- [ ] Actualizar CUIT en `facturacion.py`
- [ ] Probar en modo homologación (sin certificados)
- [ ] Probar en modo producción (con certificados)
- [ ] Validar que CAE se guarda en BD
- [ ] Probar generación de múltiples facturas

---

## FAQ

**P: ¿Puedo probar sin certificados?**
R: Sí, el modo homologación funciona automáticamente sin certificados.

**P: ¿Qué pasa si falla la conexión a AFIP?**
R: Se guarda la factura sin CAE. El usuario ve un mensaje de error pero puede reintentar.

**P: ¿Los certificados se guardaron en el repositorio?**
R: No, `certificados/` está en `.gitignore` por seguridad.

**P: ¿Cuánto cuesta usar AFIP?**
R: Es gratuito. Solo necesitas estar registrado en AFIP.

