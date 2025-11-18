from kivy.uix.screenmanager import Screen
from kivy.properties import NumericProperty, ListProperty
from kivy.metrics import dp
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.popup import Popup

import sys, os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from mkdir_database.conexion import ejecutar_consulta


class FacturaScreen(Screen):

    total_carrito = NumericProperty(0.0)
    cantidad_items = NumericProperty(0)
    carrito = ListProperty([])
    productos_disponibles = ListProperty([])

    # ==========================================================
    # AL ENTRAR A LA PANTALLA
    # ==========================================================
    def on_pre_enter(self, *args):
        # Aseguramos que exista el atributo de selección
        self._producto_seleccionado = None
        # Si ya hay carrito (viene del menú principal), lo pintamos
        try:
            self.actualizar_tabla_carrito()
        except Exception as e:
            print("Error al actualizar tabla carrito en on_pre_enter:", e)

    # ==========================================================
    # VOLVER AL MENÚ
    # ==========================================================
    def volver_menu(self):
        self.manager.current = "menu_principal"

    # ==========================================================
    # RECIBIR CARRITO DESDE MENÚ PRINCIPAL
    # ==========================================================
    def set_carrito_inicial(self, carrito):
        self.carrito = carrito
        self.actualizar_totales()
        self.actualizar_tabla_carrito()

    # ==========================================================
    # WRAPPER PARA AGREGAR (DESDE EL KV)
    # ==========================================================
    def _agregar_wrapper(self):
        cantidad = self.ids.cantidad_producto.text.strip()

        if not hasattr(self, "_producto_seleccionado") or self._producto_seleccionado is None:
            self.mostrar_error("Debes seleccionar un producto de la lista de resultados.")
            return

        if not cantidad.isdigit() or int(cantidad) <= 0:
            self.mostrar_error("Cantidad inválida.")
            return

        # Agregar usando el producto seleccionado
        self.agregar_producto_factura(
            self._producto_seleccionado["nombre"],
            cantidad
        )

        # limpiar selección
        self.ids.buscar_producto.text = ""
        self.ids.cantidad_producto.text = "1"
        self._producto_seleccionado = None
        self.ids.resultados_busqueda.clear_widgets()

    # ==========================================================
    # AGREGAR PRODUCTO AL CARRITO
    # ==========================================================
    def agregar_producto_factura(self, nombre_producto, cantidad_txt):
        if not cantidad_txt.isdigit() or int(cantidad_txt) <= 0:
            self.mostrar_error("Cantidad inválida.")
            return

        cantidad = int(cantidad_txt)

        # buscar producto en la lista disponible
        for p in self.productos_disponibles:
            if p["nombre"] == nombre_producto:
                producto = {
                    "id": p["id"],
                    "nombre": p["nombre"],
                    "precio": float(p["precio"]),
                    "cantidad": cantidad,
                    "subtotal": float(p["precio"]) * cantidad
                }
                break
        else:
            self.mostrar_error("Producto no encontrado.")
            return

        self.carrito.append(producto)
        self.actualizar_totales()
        self.actualizar_tabla_carrito()

    # ==========================================================
    # BUSCADOR DE PRODUCTOS (BARRA DE BÚSQUEDA)
    # ==========================================================
    def buscar_producto_factura(self, texto):
        cont = self.ids.resultados_busqueda
        cont.clear_widgets()

        texto = (texto or "").strip()
        if not texto:
            return

        # Filtrar productos por nombre (en memoria)
        resultados = [
            p for p in self.productos_disponibles
            if texto.lower() in p["nombre"].lower()
        ]

        for prod in resultados:
            btn = Button(
                text=f"{prod['nombre']} - ${float(prod['precio']):.2f}",
                size_hint_y=None,
                height=dp(35),
                background_color=(0.85, 0.85, 0.85, 1),
                color=(0, 0, 0, 1),
                on_release=lambda x, p=prod: self.seleccionar_producto(p)
            )
            cont.add_widget(btn)

    # ==========================================================
    # GUARDAR PRODUCTO SELECCIONADO
    # ==========================================================
    def seleccionar_producto(self, producto):
        self._producto_seleccionado = producto
        self.ids.buscar_producto.text = producto["nombre"]
        self.ids.resultados_busqueda.clear_widgets()

    # ==========================================================
    # TABLA CARRITO
    # ==========================================================
    def actualizar_tabla_carrito(self):
        tabla = self.ids.carrito_grid
        tabla.clear_widgets()

        # Encabezados
        encabezados = ["Producto", "Precio", "Cantidad", "Subtotal", "Acción"]
        for titulo in encabezados:
            tabla.add_widget(Label(text=titulo, bold=True, size_hint_y=None, height=dp(30)))

        # Filas
        for item in self.carrito:
            tabla.add_widget(Label(text=item["nombre"]))
            tabla.add_widget(Label(text=f"${item['precio']:.2f}"))
            tabla.add_widget(Label(text=str(item["cantidad"])))
            tabla.add_widget(Label(text=f"${item['subtotal']:.2f}"))

            btn = Button(
                text="X",
                size_hint_y=None,
                height=dp(28),
                background_color=(0.9, 0.2, 0.2, 1),
                color=(1, 1, 1, 1),
                on_release=lambda x, i=item: self.eliminar_item(i)
            )
            tabla.add_widget(btn)

    # ==========================================================
    # ELIMINAR ITEM DEL CARRITO
    # ==========================================================
    def eliminar_item(self, item):
        if item in self.carrito:
            self.carrito.remove(item)
        self.actualizar_totales()
        self.actualizar_tabla_carrito()

    # ==========================================================
    # TOTAL Y CANTIDAD
    # ==========================================================
    def actualizar_totales(self):
        total = sum(i["subtotal"] for i in self.carrito)
        cantidad = sum(i["cantidad"] for i in self.carrito)
        self.total_carrito = total
        self.cantidad_items = cantidad

    # ==========================================================
    # LIMPIAR CARRITO
    # ==========================================================
    def limpiar_carrito(self):
        self.carrito = []
        self.actualizar_totales()
        self.actualizar_tabla_carrito()

    # ==========================================================
    # GUARDAR FACTURA EN LA BD
    # ==========================================================
    def generar_factura(self, nombre, apellido, telefono, email, ci):

        if not self.carrito:
            self.mostrar_error("El carrito está vacío.")
            return

        if not nombre or not apellido:
            self.mostrar_error("Nombre y apellido son obligatorios.")
            return

        # Insert cliente
        consulta_cliente = """
            INSERT INTO Clientes (Nombre, Apellido, Telefono, Email, CI)
            VALUES (?, ?, ?, ?, ?)
        """
        ejecutar_consulta(consulta_cliente, (nombre, apellido, telefono, email, ci))

        cliente_id = ejecutar_consulta("SELECT last_insert_rowid()")[0][0]

        # Insert factura
        consulta_factura = """
            INSERT INTO Facturas (ClienteID, Total, Fecha)
            VALUES (?, ?, datetime('now'))
        """
        ejecutar_consulta(consulta_factura, (cliente_id, self.total_carrito))

        factura_id = ejecutar_consulta("SELECT last_insert_rowid()")[0][0]

        # Insert detalles + actualizar stock
        for item in self.carrito:
            ejecutar_consulta("""
                INSERT INTO FacturaDetalle 
                (FacturaID, ProductoID, Cantidad, PrecioUnitario, Subtotal)
                VALUES (?, ?, ?, ?, ?)
            """, (factura_id, item["id"], item["cantidad"], item["precio"], item["subtotal"]))

            ejecutar_consulta("""
                UPDATE Productos SET Stock = Stock - ?
                WHERE ProductoID = ?
            """, (item["cantidad"], item["id"]))

        self.limpiar_carrito()
        self.mostrar_mensaje("Factura generada con éxito")

    # ==========================================================
    # POPUPS
    # ==========================================================
    def mostrar_error(self, mensaje):
        box = BoxLayout(orientation="vertical", padding=dp(10), spacing=dp(10))
        box.add_widget(Label(text=mensaje, color=(1, 0, 0, 1)))
        btn = Button(text="Cerrar", size_hint_y=None, height=dp(40),
                     on_release=lambda x: popup.dismiss())
        box.add_widget(btn)

        popup = Popup(title="Error", content=box,
                      size_hint=(None, None), size=(350, 200))
        popup.open()

    def mostrar_mensaje(self, mensaje):
        box = BoxLayout(orientation="vertical", padding=dp(10), spacing=dp(10))
        box.add_widget(Label(text=mensaje, color=(0, 0.4, 0, 1)))
        btn = Button(text="OK", size_hint_y=None, height=dp(40),
                     on_release=lambda x: popup.dismiss())
        box.add_widget(btn)

        popup = Popup(title="Información", content=box,
                      size_hint=(None, None), size=(350, 200))
        popup.open()

    # ==========================================================
    # WRAPPER PARA GENERAR FACTURA (DESDE KV)
    # ==========================================================
    def _generar_wrapper(self):
        self.generar_factura(
            self.ids.cliente_nombre.text,
            self.ids.cliente_apellido.text,
            self.ids.cliente_telefono.text,
            self.ids.cliente_email.text,
            self.ids.cliente_ci.text
        )
