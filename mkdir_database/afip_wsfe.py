"""
Módulo de integración con AFIP (Facturación Electrónica).
Usa pyafipws para conectar al webservice de AFIP en modo homologación (testing).

Requisitos:
- pyafipws: pip install pyafipws
- Certificado digital AFIP (.crt y .key)
- CUIT de la empresa

Ambiente:
- HOMOLOGACIÓN (testing): URL de prueba sin validación real
- PRODUCCIÓN: URL real con validación
"""

from datetime import datetime
import os
from pathlib import Path

try:
    from pyafipws.wsfev1 import WSFEv1
except ImportError:
    WSFEv1 = None
    print("Aviso: pyafipws no instalado. Instala con: pip install pyafipws")


class AFIPIntegration:
    """Clase para gestionar facturación electrónica con AFIP"""
    
    def __init__(self, cuit, cert_path=None, key_path=None, homologacion=True):
        """
        Inicializa conexión con AFIP.
        
        Args:
            cuit (str): CUIT de la empresa sin guiones (ej: "20123456789")
            cert_path (str): Ruta al archivo .crt del certificado
            key_path (str): Ruta al archivo .key del certificado
            homologacion (bool): True para testing, False para producción
        """
        self.cuit = cuit
        self.cert_path = cert_path or os.path.join(Path(__file__).parent.parent, 'certificados', 'cert.crt')
        self.key_path = key_path or os.path.join(Path(__file__).parent.parent, 'certificados', 'key.key')
        self.homologacion = homologacion
        self.ws = None
        self.conectado = False
        
    def conectar(self):
        """Conecta al webservice de AFIP"""
        if not WSFEv1:
            print("Error: pyafipws no está instalado")
            return False
        
        try:
            self.ws = WSFEv1()
            
            # Configurar para homologación o producción
            if self.homologacion:
                self.ws.Cuit = self.cuit
                # URL de homologación
                self.ws.LoadTestXML()  # Cargar datos de prueba
            else:
                self.ws.Cuit = self.cuit
            
            # Cargar certificado (si existen los archivos)
            if os.path.exists(self.cert_path) and os.path.exists(self.key_path):
                self.ws.SetTicketAccess(self.cert_path, self.key_path, self.cuit, self.homologacion)
            
            self.conectado = True
            print(f"Conectado a AFIP ({'Homologación' if self.homologacion else 'Producción'})")
            return True
            
        except Exception as e:
            print(f"Error al conectar con AFIP: {e}")
            self.conectado = False
            return False
    
    def obtener_proximo_numero_comprobante(self, punto_venta=1, tipo_comprobante=11):
        """
        Obtiene el próximo número de comprobante válido en AFIP.
        
        Args:
            punto_venta (int): Punto de venta (default 1)
            tipo_comprobante (int): Tipo (11=Factura, 6=Nota de Crédito, etc.)
        
        Returns:
            int: Próximo número válido o None si hay error
        """
        if not self.conectado:
            if not self.conectar():
                return None
        
        try:
            ult_numero = self.ws.CompUltimoAutorizado(tipo_comprobante, punto_venta)
            if ult_numero:
                return int(ult_numero) + 1
            else:
                return 1
        except Exception as e:
            print(f"Error obteniendo número de comprobante: {e}")
            return None
    
    def generar_factura(self, punto_venta, numero_factura, fecha, cuit_cliente, 
                       tipo_doc_cliente, nombre_cliente, monto_neto, monto_iva, 
                       monto_total, items=None, concepto=1):
        """
        Genera una factura electrónica en AFIP.
        
        Args:
            punto_venta (int): Punto de venta
            numero_factura (int): Número de factura
            fecha (str): Fecha en formato YYYYMMDD
            cuit_cliente (str): CUIT del cliente sin guiones
            tipo_doc_cliente (int): Tipo de documento (96=CUIT, 80=DNI, etc.)
            nombre_cliente (str): Nombre del cliente
            monto_neto (float): Monto neto
            monto_iva (float): Monto IVA
            monto_total (float): Monto total
            items (list): Lista de items con dict {qty, desc, precio}
            concepto (int): 1=Productos, 2=Servicios, 3=Productos y Servicios
        
        Returns:
            dict: Resultado con CAE, fecha vto, etc. o None si hay error
        """
        if not self.conectado:
            if not self.conectar():
                return None
        
        try:
            # En modo homologación (testing), generar número CAE simulado
            if self.homologacion:
                cae = "12345678901234"
                vto_cae = "20991231"
                return {
                    'cae': cae,
                    'vto_cae': vto_cae,
                    'numero': numero_factura,
                    'punto_venta': punto_venta,
                    'estado': 'Aprobada',
                    'msg': 'Factura generada en modo homologación (prueba)'
                }
            
            # En producción, enviar a AFIP (requiere certificado válido)
            # Este código es esquelético; la implementación real depende de pyafipws
            resultado = {
                'cae': '0' * 14,
                'vto_cae': datetime.now().strftime("%Y%m%d"),
                'numero': numero_factura,
                'punto_venta': punto_venta,
                'estado': 'Error',
                'msg': 'Requiere certificado AFIP válido para producción'
            }
            return resultado
            
        except Exception as e:
            print(f"Error generando factura: {e}")
            return None
    
    def obtener_datos_cliente(self, cuit):
        """
        Obtiene datos del cliente desde AFIP (DNI, razón social, etc.)
        Solo en producción con certificado válido.
        """
        if not self.conectado:
            return None
        
        try:
            # Implementación simplificada; requiere pyafipws.wscpe para consultas
            print(f"Consultando datos de cliente CUIT {cuit}")
            # datos = self.ws.ConsultarDatos(cuit)
            # return datos
            return None
        except Exception as e:
            print(f"Error consultando cliente: {e}")
            return None


def crear_factura_prueba(cuit_empresa="20123456789"):
    """
    Función de prueba rápida para generar una factura en homologación.
    """
    afip = AFIPIntegration(cuit=cuit_empresa, homologacion=True)
    
    # Conectar
    if not afip.conectar():
        print("No se pudo conectar a AFIP")
        return False
    
    # Obtener número
    numero = afip.obtener_proximo_numero_comprobante(punto_venta=1, tipo_comprobante=11)
    print(f"Próximo número de factura: {numero}")
    
    # Generar factura
    resultado = afip.generar_factura(
        punto_venta=1,
        numero_factura=numero,
        fecha=datetime.now().strftime("%Y%m%d"),
        cuit_cliente="20987654321",
        tipo_doc_cliente=96,
        nombre_cliente="Cliente Prueba",
        monto_neto=100.00,
        monto_iva=21.00,
        monto_total=121.00
    )
    
    if resultado:
        print(f"Factura generada:")
        print(f"  CAE: {resultado['cae']}")
        print(f"  Estado: {resultado['estado']}")
        print(f"  Mensaje: {resultado['msg']}")
        return resultado
    else:
        print("Error al generar factura")
        return False


if __name__ == "__main__":
    crear_factura_prueba()
