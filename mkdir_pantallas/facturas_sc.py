from kivy.uix.screenmanager import Screen
from kivy.uix.label import Label
from kivy.uix.gridlayout import GridLayout
from kivy.uix.button import Button
from kivy.metrics import dp
from kivy.properties import NumericProperty, ListProperty
from kivy.clock import Clock

from mkdir_database.conexion import ejecutar_consulta, descontar_stock
from mkdir_servicios.arca_api import emitir_factura_simple
import datetime


class FacturaScreen(Screen):
    total_carrito = NumericProperty(0.0)
    cantidad_items = NumericProperty(0)
    productos_disponibles = ListProperty([])   # ← ← ← SOLUCIÓN PRINCIPAL
    carrito = ListProperty([])

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.carrito = []
        self.ids_creados = False

        # Cargar productos de la BD
        Clock.schedule_once(self.cargar_productos, 0.1)

        # Crear ids si no existen
        Clock.schedule_once(self._crear_ids_simulados, 0.2)

    # ---------------------------
    # Cargar productos desde SQLite
    # ---------------------------
    def cargar_productos(self, dt=None):
        try:
            consulta = "SELECT ProductoID, Nombre, Precio FROM Productos WHERE Estado = 1"
            filas = ejecutar_consulta(consulta)

            self.productos_disponibles = [
                {"id": f[0], "nombre": f[1], "precio": float(f[2])}
                for f in filas
            ]

            print("PRODUCTOS DISPONIBLES:", self.productos_disponibles)

        except Exception as e:
            print("ERROR cargando productos:", e)
            self.productos_disponibles = []

    # ---------------------------
    # Compatibilidad KV
    # ---------------------------
    def _crear_ids_simulados(self, dt):
        if hasattr(self, 'ids') and not self.ids_creados:
            self.ids_creados = True
            if 'carrito_grid' not in self.ids:
                self.ids['carrito_grid'] = GridLayout(cols=5, size_hint_y=None)
            if 'mensaje_label' not in self.ids:
                self.ids['mensaje_label'] = Label(text="")

    # ---------------------------
    # Agregar producto
    # ---------------------------
    def agregar_producto(self, nombre_producto, cantidad_texto):

        if not cantidad_texto.isdigit():
            self.mostrar_error("Cantidad inválida")
            return

        cantidad = int(cantidad_texto)
        if cantidad <= 0:
            self.mostrar_error("Cantidad debe ser mayor a 0")
            return

        prod = next((p for p in self.productos_disponibles if p["nombre"] == nombre_producto), None)
        if not prod:
            self.mostrar_error("Producto no encontrado")
            return

        subtotal = prod["precio"] * cantidad

        self.carrito.append({
            "id": prod["id"],
            "nombre": nombre_producto,
            "cantidad": cantidad,
            "precio": prod["precio"],
            "subtotal": subtotal
        })

        self.actualizar_totales()
        self.actualizar_tabla_carrito()

    # ---------------------------
    # Eliminar producto
    # ---------------------------
    def eliminar_producto_carrito(self, producto_id):
        self.carrito = [p for p in self.carrito if p["id"] != producto_id]
        self.actualizar_totales()
        self.actualizar_tabla_carrito()

    # ---------------------------
    # Actualizar totales
    # ---------------------------
    def actualizar_totales(self):
        self.total_carrito = sum(p["subtotal"] for p in self.carrito)
        self.cantidad_items = len(self.carrito)

    # ---------------------------
    # Actualizar tabla carrito
    # ---------------------------
    def actualizar_tabla_carrito(self):
        grid = self.ids.get('carrito_grid')
        if not grid:
            return

        grid.clear_widgets()

        encabezados = ["Producto", "Precio", "Cantidad", "Subtotal", "Acción"]
        for h in encabezados:
            grid.add_widget(Label(text=h, bold=True, size_hint_y=None, height=dp(35)))

        for item in self.carrito:
            grid.add_widget(Label(text=item['nombre']))
            grid.add_widget(Label(text=f"{item['precio']:.2f}"))
            grid.add_widget(Label(text=str(item['cantidad'])))
            grid.add_widget(Label(text=f"{item['subtotal']:.2f}"))
            grid.add_widget(Button(text="Eliminar", on_release=lambda b, pid=item['id']: self.eliminar_producto_carrito(pid)))

    # ---------------------------
    # Limpiar carrito
    # ---------------------------
    def limpiar_carrito(self):
        self.carrito = []
        self.actualizar_totales()
        self.actualizar_tabla_carrito()

    # ---------------------------
    # Generar factura
    # ---------------------------
    def generar_factura(self, nombre, apellido, telefono, email, ci):
        if not self.carrito:
            self.mostrar_error("El carrito está vacío")
            return

        cliente = {
            "nombre": nombre,
            "apellido": apellido,
            "telefono": telefono,
            "email": email,
            "ci": ci
        }

        factura = emitir_factura_simple(cliente, self.carrito, usuario_id=1)

        consulta = """
    SELECT ProductoID, Nombre, Precio 
    FROM Productos 
    WHERE Estado IS NULL OR Estado = 1
"""


        parametros = (
            factura["numero_factura"],
            factura["fecha_factura"],
            factura["cliente_nombre"],
            factura["cliente_ci"],
            factura["cliente_telefono"],
            factura["cliente_email"],
            factura["total"],
            factura["usuario_id"],
            factura["cae"],
            factura["vto_cae"],
            factura["estado"]
        )

        ejecutar_consulta(consulta, parametros)

        for item in self.carrito:
            descontar_stock(item["id"], item["cantidad"])

        self.mostrar_mensaje("Factura generada con éxito")
        self.limpiar_carrito()

    # ---------------------------
    # Mensajes
    # ---------------------------
    def mostrar_error(self, texto):
        lbl = self.ids.get("mensaje_label")
        if lbl:
            lbl.text = texto
            lbl.color = (1, 0, 0, 1)

    def mostrar_mensaje(self, texto):
        lbl = self.ids.get("mensaje_label")
        if lbl:
            lbl.text = texto
            lbl.color = (0, 1, 0, 1)
