from kivy.uix.screenmanager import Screen
from kivy.properties import NumericProperty, ListProperty
from kivy.metrics import dp
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.popup import Popup
from kivy.clock import Clock
from kivymd.uix.menu import MDDropdownMenu

import sys, os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from mkdir_database.conexion import ejecutar_consulta
except:
    from conexion import ejecutar_consulta


class FacturaScreen(Screen):
    total_carrito = NumericProperty(0.0)
    cantidad_items = NumericProperty(0)
    carrito = ListProperty([])               # [{'id', 'nombre', 'precio', 'cantidad', 'subtotal'}, ...]
    productos_disponibles = ListProperty([]) # [{'id', 'nombre', 'precio'}, ...]

    def on_pre_enter(self, *args):
        # Para evitar errores si se llama muy temprano
        self._producto_seleccionado = None
        try:
            Clock.schedule_once(lambda dt: self.actualizar_tabla_carrito(), 0)
        except Exception as e:
            print("Error al actualizar tabla carrito en on_pre_enter:", e)

    # ==========================================================
    # VOLVER AL MENÚ (si usás ScreenManager)
    # ==========================================================
    def volver_menu(self):
        if self.manager:
            self.manager.current = "menu_principal"

    # ==========================================================
    # RECIBIR CARRITO DESDE MENÚ PRINCIPAL (LUCAS)
    # ==========================================================
    def set_carrito_inicial(self, carrito):
        """
        carrito: lista de dicts con:
        {
          "id": ProductoID,
          "nombre": str,
          "precio": float,
          "cantidad": int,
          "subtotal": float
        }
        """
        self.carrito = carrito
        self.actualizar_totales()
        # Esperamos 1 frame para asegurar que el kv cargó los ids
        Clock.schedule_once(lambda dt: self.actualizar_tabla_carrito(), 0)

    # ==========================================================
    # WRAPPER PARA AGREGAR DESDE EL KV
    # ==========================================================
    def _agregar_wrapper(self):
        cantidad = self.ids.cantidad_producto.text.strip()

        if not hasattr(self, "_producto_seleccionado") or self._producto_seleccionado is None:
            self.mostrar_error("Debes seleccionar un producto de la lista de resultados.")
            return

        if not cantidad.isdigit() or int(cantidad) <= 0:
            self.mostrar_error("Cantidad inválida.")
            return

        self.agregar_producto_factura(
            self._producto_seleccionado["id"],
            self._producto_seleccionado["nombre"],
            self._producto_seleccionado["precio"],
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
    def agregar_producto_factura(self, producto_id, nombre_producto, precio_unitario, cantidad_txt):
        if not cantidad_txt.isdigit() or int(cantidad_txt) <= 0:
            self.mostrar_error("Cantidad inválida.")
            return

        cantidad = int(cantidad_txt)
        precio = float(precio_unitario)
        subtotal = precio * cantidad

        # Si ya existe en el carrito, sumamos cantidad
        for item in self.carrito:
            if item["id"] == producto_id:
                item["cantidad"] += cantidad
                item["subtotal"] += subtotal
                break
        else:
            self.carrito.append({
                "id": producto_id,
                "nombre": nombre_producto,
                "precio": precio,
                "cantidad": cantidad,
                "subtotal": subtotal
            })

        self.actualizar_totales()
        self.actualizar_tabla_carrito()

    # ==========================================================
    # BUSCADOR DE PRODUCTOS (EN MEMORIA)
    # ==========================================================
    def buscar_producto_factura(self, texto):
        cont = self.ids.resultados_busqueda
        cont.clear_widgets()

        texto = (texto or "").strip()
        if not texto:
            return

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
        if "carrito_grid" not in self.ids:
            # Aún no está cargado el kv
            return

        tabla = self.ids.carrito_grid
        tabla.clear_widgets()

        if not self.carrito:
            # Solo encabezados vacíos
            encabezados = ["Producto", "Precio", "Cantidad", "Subtotal", "Acción"]
            for titulo in encabezados:
                tabla.add_widget(Label(text=titulo, bold=True, size_hint_y=None, height=dp(30)))
            return

        # Encabezados
        encabezados = ["Producto", "Precio", "Cantidad", "Subtotal", "Acción"]
        for titulo in encabezados:
            tabla.add_widget(Label(text=titulo, bold=True, size_hint_y=None, height=dp(30)))

        # Filas
        for item in self.carrito:
            tabla.add_widget(Label(text=item["nombre"], color=(0, 0, 0, 1)))
            tabla.add_widget(Label(text=f"${item['precio']:.2f}", color=(0, 0, 0, 1)))
            tabla.add_widget(Label(text=str(item["cantidad"]), color=(0, 0, 0, 1)))
            tabla.add_widget(Label(text=f"${item['subtotal']:.2f}", color=(0, 0, 0, 1)))

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
    #   → Usa Compradores + Ventas + VentaDetalle (SQL Server)
    # ==========================================================
    def generar_factura(self, nombre, apellido, telefono, email, ci_rut):

        if not self.carrito:
            self.mostrar_error("El carrito está vacío.")
            return

        # Validar cliente seleccionado
        cliente_id = getattr(self, "cliente_id_seleccionado", None)
        if not cliente_id:
            self.mostrar_error("Debes seleccionar un cliente.")
            return

        nombre_completo = f"{nombre} {apellido}".strip()

        # 1) Insertar en Compradores
        try:
            ejecutar_consulta("""
                INSERT INTO Compradores (Nombre, TipoComprador, Telefono, Email, Direccion, Estado)
                VALUES (?, ?, ?, ?, ?, 1)
            """, (nombre_completo, "Minorista", telefono or "", email or "", ci_rut or ""))

            filas = ejecutar_consulta("SELECT MAX(CompradorID) FROM Compradores", ())
            comprador_id = filas[0][0] if filas and filas[0][0] is not None else None
        except Exception as e:
            self.mostrar_error(f"Error al guardar comprador: {e}")
            return

        if not comprador_id:
            self.mostrar_error("No se pudo obtener el CompradorID.")
            return

        # 2) Insertar en Ventas
        try:
            tipo_pago = "Sin especificar"
            ejecutar_consulta("""
                INSERT INTO Ventas (ClienteID, TipoPago, Total)
                VALUES (?, ?, ?)
            """, (cliente_id, tipo_pago, self.total_carrito))

            filas = ejecutar_consulta("SELECT MAX(VentaID) FROM Ventas", ())
            venta_id = filas[0][0] if filas and filas[0][0] is not None else None

        except Exception as e:
            self.mostrar_error(f"Error al guardar venta: {e}")
            return



        if not venta_id:
            self.mostrar_error("No se pudo obtener el VentaID.")
            return

        # 3) Insertar detalles + actualizar stock
        try:
            for item in self.carrito:
                ejecutar_consulta("""
                    INSERT INTO VentaDetalle (VentaID, ProductoID, Cantidad, PrecioUnitario, Descuento)
                    VALUES (?, ?, ?, ?, 0)
                """, (venta_id, item["id"], item["cantidad"], item["precio"]))

                ejecutar_consulta("""
                    UPDATE Productos
                    SET Stock = Stock - ?
                    WHERE ProductoID = ?
                """, (item["cantidad"], item["id"]))
        except Exception as e:
            self.mostrar_error(f"Error al guardar detalle de venta: {e}")
            return

        # 4) Limpiar
        self.limpiar_carrito()
        self.mostrar_mensaje(f"Venta registrada con éxito. VentaID: {venta_id}")

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
            "", 
            self.ids.cliente_telefono.text,
            self.ids.cliente_email.text,
            self.ids.cliente_ci.text,
        )


    def volver_menu(self):
        from mkdir_pantallas.menu_principal import MenuPrincipalScreen

        contenedor = self.parent
        if contenedor:
            contenedor.clear_widgets()
            contenedor.add_widget(MenuPrincipalScreen())

        # ================================================================
    # ABRIR PANTALLA DE GESTIÓN DE CLIENTES
    # ================================================================
    def abrir_gestion_clientes(self):
        from mkdir_pantallas.clientes import ClientesScreen

        clientes = ClientesScreen()
        clientes.pantalla_factura = self  # ← Le pasamos la referencia

        if self.parent:
            contenedor = self.parent
            contenedor.clear_widgets()
            contenedor.add_widget(clientes)

    # ================================================================
    # ABRIR POPUP PARA SELECCIONAR CLIENTE
    # ================================================================
    def abrir_selector_cliente(self):
        try:
            filas = ejecutar_consulta("""
                SELECT ClienteID, Nombre, Telefono, Email, CUIT
                FROM Clientes
            """, ())
        except Exception as e:
            print("Error al ejecutar consulta:", e)
            filas = []

        # Si filas viene vacío o None
        if not filas:
            Popup(
                title="Sin clientes",
                content=Label(text="No hay clientes registrados.", color=(1, 1, 1, 1)),
                size_hint=(None, None),
                size=(350, 150)
            ).open()
            return

        # Crear lista para mostrar en el popup
        opciones = []
        for cid, nombre, tel, email, cuit in filas:
            opciones.append(f"{cid} - {nombre}")

        # ---------- Popup de selección ----------
        content = BoxLayout(orientation="vertical", spacing=dp(10), padding=dp(10))

        from kivy.uix.spinner import Spinner
        selector = Spinner(
            text="Seleccionar cliente...",
            values=opciones,
            size_hint_y=None,
            height=dp(40)
        )
        content.add_widget(selector)

        botones = BoxLayout(size_hint_y=None, height=dp(45), spacing=dp(10))

        btn_ok = Button(
            text="Seleccionar",
            background_color=(0, 0.6, 0.2, 1),
            color=(1, 1, 1, 1),
            on_release=lambda x: self._cliente_seleccionado(selector.text, popup)
        )

        btn_cancel = Button(
            text="Cancelar",
            background_color=(0.6, 0.1, 0.1, 1),
            color=(1, 1, 1, 1),
            on_release=lambda x: popup.dismiss()
        )

        botones.add_widget(btn_ok)
        botones.add_widget(btn_cancel)
        content.add_widget(botones)

        popup = Popup(
            title="Seleccionar Cliente",
            content=content,
            size_hint=(None, None),
            size=(450, 300),
            auto_dismiss=False
        )
        popup.open()

    def _cliente_seleccionado(self, texto, popup):
        """
        texto viene en formato: 'ID - Nombre'
        ejemplo: '3 - Juan Perez'
        """
        if not texto or " - " not in texto:
            popup.dismiss()
            return

        cliente_id = texto.split(" - ")[0]

        self.cliente_id_seleccionado = int(cliente_id)

        try:
            fila = ejecutar_consulta("""
                SELECT Nombre, Telefono, Email, CUIT
                FROM Clientes
                WHERE ClienteID = ?
            """, (cliente_id,))
        except Exception as e:
            print("Error al obtener cliente:", e)
            popup.dismiss()
            return

        if fila:
            nombre, telefono, email, cuit = fila[0]

            # Rellenar los campos del formulario
            self.ids.cliente_nombre.text = nombre or ""
            self.ids.cliente_telefono.text = telefono or ""
            self.ids.cliente_email.text = email or ""
            self.ids.cliente_ci.text = cuit or ""

        popup.dismiss()

    # ================================================================
    # CARGAR CLIENTE EN FORMULARIO
    # ================================================================
    def cargar_cliente_en_formulario(self, cliente, popup):
        cid, nom, ape, tel, email, ci = cliente

        self.ids.cliente_nombre.text = nom
        self.ids.cliente_apellido.text = ape
        self.ids.cliente_telefono.text = tel
        self.ids.cliente_email.text = email
        self.ids.cliente_ci.text = ci

        popup.dismiss()
    def abrir_menu_facturas(self, textfield):
        menu_items = [
            {"text": "Factura A", "on_release": lambda: self._set_tipo_factura("Factura A")},
            {"text": "Factura B", "on_release": lambda: self._set_tipo_factura("Factura B")},
    ]

        self.menu_factura = MDDropdownMenu(
            caller=textfield,
            items=menu_items,
            width_mult=3
        )
        self.menu_factura.open()

    def _set_tipo_factura(self, tipo):
        self.ids.tipo_factura.text = tipo
        self.menu_factura.dismiss()
