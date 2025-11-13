from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.spinner import Spinner
from kivy.uix.popup import Popup
from kivy.metrics import dp
from kivy.properties import StringProperty, NumericProperty, ListProperty
from kivy.clock import Clock
from datetime import datetime
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from mkdir_database.conexion import ejecutar_consulta, conectar, cerrar_conexion
from mkdir_database.afip_wsfe import AFIPIntegration


class FacturacionScreen(BoxLayout):
    """Pantalla de facturación con carrito y cálculos"""
    
    total_carrito = NumericProperty(0.0)
    cantidad_items = NumericProperty(0)
    productos_disponibles = ListProperty([])
    
    def __init__(self, productos_iniciales=None, cantidades_iniciales=None, **kwargs):
        """
        Inicializa la pantalla de facturación.
        
        Args:
            productos_iniciales: Lista de tuplas (pid, nombre, desc, precio, stock) del menú principal
            cantidades_iniciales: Dict de {pid: cantidad} del carrito del menú principal
        """
        super().__init__(**kwargs)
        self.orientation = 'vertical'
        self.carrito = []
        self.productos_disponibles = []
        self.cliente_actual = None
        self.numero_factura = 1
        
        # Datos del cliente
        self.cliente_nombre = ""
        self.cliente_apellido = ""
        self.cliente_telefono = ""
        self.cliente_email = ""
        
        # Productos del menú principal
        self.productos_iniciales = productos_iniciales or []
        self.cantidades_iniciales = cantidades_iniciales or {}
        
        self.cargar_productos()
        self.cargar_productos_iniciales()
        self.generar_numero_factura()
    
    # ========================
    # Cargar datos de la BD
    # ========================
    
    def cargar_productos(self):
        """Carga los productos disponibles desde la BD"""
        try:
            resultado = ejecutar_consulta(
                "SELECT ProductoID, Nombre, Precio, Stock FROM Productos WHERE Activo = 1"
            )
            if resultado:
                self.productos_disponibles = [
                    {'id': row[0], 'nombre': row[1], 'precio': row[2], 'stock': row[3]}
                    for row in resultado
                ]
                print(f"Cargados {len(self.productos_disponibles)} productos desde la BD")
            else:
                print("No hay productos en la BD")
                self.productos_disponibles = []
        except Exception as e:
            print(f"Error al cargar productos: {e}")
            # Si falla, usar productos de ejemplo
            self.productos_disponibles = [
                {'id': 1, 'nombre': 'Producto A', 'precio': 100.00, 'stock': 50},
                {'id': 2, 'nombre': 'Producto B', 'precio': 250.00, 'stock': 30},
                {'id': 3, 'nombre': 'Producto C', 'precio': 75.50, 'stock': 100},
                {'id': 4, 'nombre': 'Producto D', 'precio': 500.00, 'stock': 10},
                {'id': 5, 'nombre': 'Producto E', 'precio': 150.00, 'stock': 45},
            ]
    
    def cargar_productos_iniciales(self):
        """Carga los productos que vienen del menú principal"""
        if not self.productos_iniciales:
            return
        
        for producto in self.productos_iniciales:
            pid, nombre, desc, precio, stock = producto
            cantidad = self.cantidades_iniciales.get(pid, 1)
            
            # Agregar al carrito
            self.carrito.append({
                'id': pid,
                'nombre': nombre,
                'precio': float(precio),
                'cantidad': cantidad,
                'subtotal': float(precio) * cantidad
            })
        
        self.actualizar_totales()
        self.actualizar_tabla_carrito()
        print(f"Cargados {len(self.carrito)} productos del menú principal")
    
    def generar_numero_factura(self):
        """Genera número de factura automático"""
        self.numero_factura = int(datetime.now().strftime("%Y%m%d%H%M%S"))
    
    # ========================
    # Operaciones del Carrito
    # ========================
    
    def agregar_producto(self, producto_id, cantidad_str):
        """Agrega un producto al carrito"""
        try:
            cantidad = int(cantidad_str)
            if cantidad <= 0:
                self.mostrar_error("Cantidad debe ser mayor a 0")
                return
        except ValueError:
            self.mostrar_error("Cantidad inválida")
            return

        # producto_id puede ser nombre (string) o id (int)
        producto = None
        if isinstance(producto_id, str):
            # intentar convertir a int
            try:
                pid = int(producto_id)
                producto = next((p for p in self.productos_disponibles if p['id'] == pid), None)
            except Exception:
                # buscar por nombre
                producto = next((p for p in self.productos_disponibles if p['nombre'] == producto_id), None)
        else:
            producto = next((p for p in self.productos_disponibles if p['id'] == producto_id), None)
        if not producto:
            self.mostrar_error("Producto no encontrado")
            return
        
        if cantidad > producto['stock']:
            self.mostrar_error(f"Stock insuficiente. Disponible: {producto['stock']}")
            return
        
        # Buscar si el producto ya está en el carrito
        item_existente = next((i for i in self.carrito if i['id'] == producto_id), None)
        
        if item_existente:
            item_existente['cantidad'] += cantidad
        else:
            self.carrito.append({
                'id': producto_id,
                'nombre': producto['nombre'],
                'precio': producto['precio'],
                'cantidad': cantidad,
                'subtotal': producto['precio'] * cantidad
            })

        # Normalizar id en el carrito (usar entero)
        for it in self.carrito:
            try:
                it['id'] = int(it['id'])
            except Exception:
                # si estaba el nombre, reemplazar por id real
                if it['id'] == producto['nombre']:
                    it['id'] = producto['id']

        self.actualizar_totales()
        self.actualizar_tabla_carrito()
        self.mostrar_mensaje(f"Producto agregado al carrito")
    
    def eliminar_producto_carrito(self, producto_id):
        """Elimina un producto del carrito"""
        self.carrito = [i for i in self.carrito if i['id'] != producto_id]
        self.actualizar_totales()
        self.actualizar_tabla_carrito()
    
    def actualizar_cantidad_carrito(self, producto_id, nueva_cantidad_str):
        """Actualiza la cantidad de un producto en el carrito"""
        try:
            nueva_cantidad = int(nueva_cantidad_str)
            if nueva_cantidad <= 0:
                self.eliminar_producto_carrito(producto_id)
                return
        except ValueError:
            return
        
        item = next((i for i in self.carrito if i['id'] == producto_id), None)
        if item:
            producto = next((p for p in self.productos_disponibles if p['id'] == producto_id), None)
            if nueva_cantidad > producto['stock']:
                self.mostrar_error(f"Stock insuficiente. Disponible: {producto['stock']}")
                return
            item['cantidad'] = nueva_cantidad
            item['subtotal'] = item['precio'] * nueva_cantidad
            self.actualizar_totales()
            self.actualizar_tabla_carrito()
    
    def actualizar_totales(self):
        """Actualiza los totales del carrito"""
        self.total_carrito = sum(item['subtotal'] for item in self.carrito)
        self.cantidad_items = len(self.carrito)
    
    def limpiar_carrito(self):
        """Limpia el carrito"""
        self.carrito = []
        self.actualizar_totales()
        self.actualizar_tabla_carrito()

    def actualizar_tabla_carrito(self):
        """Renderiza la tabla del carrito en la interfaz (ids.carrito_grid)"""
        if not hasattr(self, 'ids') or 'carrito_grid' not in self.ids:
            return
        grid = self.ids.carrito_grid
        # Limpiar y volver a crear encabezados
        grid.clear_widgets()
        headers = ['Producto', 'Precio', 'Cantidad', 'Subtotal', 'Acción']
        for h in headers:
            lbl = Label(text=h, bold=True, size_hint_y=None, height=dp(35))
            grid.add_widget(lbl)

        for item in self.carrito:
            nombre = item.get('nombre', '')
            precio = item.get('precio', 0)
            cantidad = item.get('cantidad', 0)
            subtotal = item.get('subtotal', 0)

            grid.add_widget(Label(text=str(nombre), size_hint_y=None, height=dp(35)))
            grid.add_widget(Label(text=f"{float(precio):.2f}", size_hint_y=None, height=dp(35)))
            # cantidad simple
            grid.add_widget(Label(text=str(cantidad), size_hint_y=None, height=dp(35)))
            grid.add_widget(Label(text=f"{float(subtotal):.2f}", size_hint_y=None, height=dp(35)))
            btn = Button(text="Eliminar", size_hint_y=None, height=dp(35),
                         on_release=lambda x, pid=item['id']: self.eliminar_producto_carrito(pid))
            grid.add_widget(btn)
    
    # ========================
    # Facturación
    # ========================
    
    def generar_factura(self, cliente_nombre, cliente_apellido, cliente_telefono, cliente_email, ci_cliente):
        """Genera una factura con los datos del carrito, integrando AFIP"""
        if not self.carrito:
            self.mostrar_error("El carrito está vacío")
            return False
        
        # Validar datos del cliente
        if not cliente_nombre.strip():
            self.mostrar_error("Debe ingresar el nombre del cliente")
            return False
        
        if not cliente_apellido.strip():
            self.mostrar_error("Debe ingresar el apellido del cliente")
            return False
        
        if not cliente_telefono.strip():
            self.mostrar_error("Debe ingresar el teléfono del cliente")
            return False
        
        if not cliente_email.strip() or '@' not in cliente_email:
            self.mostrar_error("Debe ingresar un email válido")
            return False
        
        if not ci_cliente.strip():
            self.mostrar_error("Debe ingresar C.I. / RUT")
            return False
        
        try:
            conexion = conectar()
            if not conexion:
                self.mostrar_error("Error al conectar con la BD")
                return False
            
            cur = conexion.cursor()
            
            # Nombre completo del cliente
            nombre_cliente_completo = f"{cliente_nombre} {cliente_apellido}"
            
            # Insertar factura
            fecha_factura = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            numero_factura = str(self.numero_factura)
            
            # ====== INTEGRACIÓN CON AFIP ======
            cae = None
            vto_cae = None
            
            try:
                # Verificar si existen certificados AFIP
                cert_path = os.path.join(os.path.dirname(__file__), '..', 'certificados', 'cert.crt')
                key_path = os.path.join(os.path.dirname(__file__), '..', 'certificados', 'key.key')
                
                # Verificar si los certificados existen
                if os.path.exists(cert_path) and os.path.exists(key_path):
                    # Usar AFIP en modo producción (requiere CUIT válido)
                    # IMPORTANTE: Cambiar CUIT y modo según necesidad
                    cuit = "20123456789"  # Reemplazar con CUIT real
                    afip = AFIPIntegration(cuit, cert_path, key_path, homologacion=False)
                    
                    # Conectar a AFIP
                    if afip.conectar():
                        try:
                            # Obtener próximo número de comprobante
                            punto_venta = 1  # o el punto de venta que uses
                            tipo_comprobante = 6  # Factura B
                            
                            numero_comprobante = afip.obtener_proximo_numero_comprobante(punto_venta, tipo_comprobante)
                            
                            # Generar factura en AFIP
                            resultado_afip = afip.generar_factura(
                                punto_venta=punto_venta,
                                numero_comprobante=numero_comprobante,
                                tipo_comprobante=tipo_comprobante,
                                fecha=fecha_factura.split(' ')[0],  # YYYY-MM-DD
                                cliente_razon_social=nombre_cliente_completo,
                                cliente_cuit=ci_cliente if len(ci_cliente) == 11 else f"23{ci_cliente}",
                                importe_total=self.total_carrito,
                                importe_gravado=self.total_carrito,
                                importe_iva=0,
                                importe_no_gravado=0
                            )
                            
                            if resultado_afip:
                                cae = resultado_afip.get('cae')
                                vto_cae = resultado_afip.get('vto_cae')
                                print(f"CAE obtenido: {cae}, válido hasta: {vto_cae}")
                        except Exception as e:
                            print(f"Error generando factura en AFIP (producción): {e}")
                            # Continuar con inserción local sin CAE
                    else:
                        print("No se pudo conectar a AFIP (producción)")
                        # Continuar con inserción local
                else:
                    # Usar AFIP en modo homologación (test)
                    cuit = "20123456789"  # CUIT de prueba
                    afip = AFIPIntegration(cuit, None, None, homologacion=True)
                    
                    if afip.conectar():
                        try:
                            punto_venta = 1
                            tipo_comprobante = 6  # Factura B
                            
                            numero_comprobante = afip.obtener_proximo_numero_comprobante(punto_venta, tipo_comprobante)
                            
                            resultado_afip = afip.generar_factura(
                                punto_venta=punto_venta,
                                numero_comprobante=numero_comprobante,
                                tipo_comprobante=tipo_comprobante,
                                fecha=fecha_factura.split(' ')[0],
                                cliente_razon_social=nombre_cliente_completo,
                                cliente_cuit=ci_cliente if len(ci_cliente) == 11 else f"23{ci_cliente}",
                                importe_total=self.total_carrito,
                                importe_gravado=self.total_carrito,
                                importe_iva=0,
                                importe_no_gravado=0
                            )
                            
                            if resultado_afip:
                                cae = resultado_afip.get('cae')
                                vto_cae = resultado_afip.get('vto_cae')
                                print(f"CAE de prueba: {cae}, válido hasta: {vto_cae}")
                        except Exception as e:
                            print(f"Error en modo homologación: {e}")
                            # Sin CAE, seguir sin validación
            except Exception as e:
                print(f"Error en proceso AFIP: {e}")
                # Continuar sin AFIP, insertar solo en BD local
            
            # ====== FIN INTEGRACIÓN AFIP ======
            
            # Insertar factura en BD local (con o sin CAE de AFIP)
            cur.execute("""
                INSERT INTO Facturas (NumeroFactura, FechaFactura, ClienteNombre, ClienteCI, ClienteTelefono, ClienteEmail, Total, CAE, VtoCae, Estado)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, 'completada')
            """, (numero_factura, fecha_factura, nombre_cliente_completo, ci_cliente, cliente_telefono, cliente_email, self.total_carrito, cae, vto_cae))
            
            factura_id = cur.lastrowid
            
            # Insertar detalles de factura
            for item in self.carrito:
                cur.execute("""
                    INSERT INTO DetallesFactura (FacturaID, ProductoID, Cantidad, PrecioUnitario, Subtotal)
                    VALUES (?, ?, ?, ?, ?)
                """, (factura_id, item['id'], item['cantidad'], item['precio'], item['subtotal']))
            
            conexion.commit()
            cerrar_conexion(conexion)
            
            mensaje = f"Factura #{numero_factura} generada exitosamente"
            if cae:
                mensaje += f"\nCAE: {cae} (válido hasta {vto_cae})"
            
            self.mostrar_mensaje(mensaje)
            self.limpiar_carrito()
            self.generar_numero_factura()
            return True
            
        except Exception as e:
            self.mostrar_error(f"Error al generar factura: {str(e)}")
            try:
                conexion.rollback()
                cerrar_conexion(conexion)
            except:
                pass
            return False
    
    # ========================
    # Mensajes
    # ========================
    
    def mostrar_error(self, mensaje):
        """Muestra un mensaje de error"""
        if hasattr(self, 'ids') and 'mensaje_label' in self.ids:
            label = self.ids.mensaje_label
            label.text = mensaje
            label.color = (1, 0, 0, 1)
    
    def mostrar_mensaje(self, mensaje):
        """Muestra un mensaje de éxito"""
        if hasattr(self, 'ids') and 'mensaje_label' in self.ids:
            label = self.ids.mensaje_label
            label.text = mensaje
            label.color = (0, 1, 0, 1)
    
    def volver_menu(self):
        """Vuelve al menú principal"""
        from mkdir_pantallas.menu_principal import MenuPrincipalScreen
        self.clear_widgets()
        self.add_widget(MenuPrincipalScreen())
