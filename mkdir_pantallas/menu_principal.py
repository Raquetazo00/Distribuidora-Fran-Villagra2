from kivy.uix.boxlayout import BoxLayout
from kivy.clock import Clock
from kivy.properties import StringProperty
from datetime import datetime
from kivy.uix.label import Label
from kivy.uix.boxlayout import BoxLayout as Bx
from kivy.uix.button import Button
from kivy.metrics import dp
from kivy.uix.popup import Popup  # Popup para confirmaciones
from kivy.uix.scrollview import ScrollView  # <-- agregado para la tabla desplazable

# Intentamos importar la conexión SQL
try:
    from mkdir_database.conexion import ejecutar_consulta
except Exception:
    try:
        from conexion import ejecutar_consulta
    except Exception:
        ejecutar_consulta = None


class MenuPrincipalScreen(BoxLayout):
    hora_actual = StringProperty("00:00:00")
    _reloj_iniciado = False
    _evento_busqueda = None

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if not self._reloj_iniciado:
            Clock.schedule_interval(self._actualizar_hora, 1)
            self._reloj_iniciado = True
        self.carrito = []
        self.cantidades = {}
        self.stock_productos = {}

    # ---------------------------
    # Reloj
    # ---------------------------
    def _actualizar_hora(self, dt):
        self.hora_actual = datetime.now().strftime("%H:%M:%S")

    # ---------------------------
    # Autobúsqueda
    # ---------------------------
    def programar_busqueda(self, texto):
        if self._evento_busqueda:
            self._evento_busqueda.cancel()
        self._evento_busqueda = Clock.schedule_once(lambda dt: self.buscar_producto(texto), 0.6)

    # ---------------------------
    # Buscar productos
    # ---------------------------
    def buscar_producto(self, texto):
        texto = (texto or "").strip()
        contenedor = self.ids.tabla_productos
        contenedor.clear_widgets()

        if not texto:
            contenedor.add_widget(Label(text="Escribe algo para buscar...", color=(0, 0, 0, 1)))
            return

        if ejecutar_consulta is None:
            contenedor.add_widget(Label(text="(Sin conexión configurada)", color=(0, 0, 0, 1)))
            return

        try:
            consulta = """
                SELECT TOP 50 ProductoID, Nombre, Descripcion, Precio, Stock
                FROM Productos
                WHERE Nombre LIKE ? OR CodigoBarras LIKE ?
                ORDER BY Nombre
            """
            param = f"%{texto}%"
            filas = ejecutar_consulta(consulta, (param, param))
        except Exception as e:
            contenedor.add_widget(Label(text=f"Error al buscar: {e}", color=(0, 0, 0, 1)))
            return

        if not filas:
            contenedor.add_widget(Label(text="No se encontraron productos.", color=(0, 0, 0, 1)))
            return

        for fila in filas:
            pid, nombre, desc, precio, stock = fila
            self.stock_productos[pid] = int(stock)

            fila_layout = Bx(size_hint_y=None, height=dp(35), spacing=dp(10))
            fila_layout.add_widget(Label(text=str(pid), color=(0, 0, 0, 1)))
            fila_layout.add_widget(Label(text=nombre, color=(0, 0, 0, 1)))
            fila_layout.add_widget(Label(text=f"${float(precio):.2f}", color=(0, 0, 0, 1)))
            fila_layout.add_widget(Label(text=f"Stock: {stock}", color=(0, 0, 0, 1)))

            btn_agregar = Button(
                text="Agregar",
                size_hint_x=None,
                width=dp(100),
                background_color=(0, 0.6, 0.2, 1),
                color=(1, 1, 1, 1),
                on_release=lambda x, p=(pid, nombre, desc, precio, stock): self.agregar_a_venta(p)
            )
            fila_layout.add_widget(btn_agregar)

            contenedor.add_widget(fila_layout)

    # ---------------------------
    # Agregar producto al carrito
    # ---------------------------
    def agregar_a_venta(self, producto):
        pid = producto[0]
        stock = self.stock_productos.get(pid, 0)

        if pid not in self.cantidades:
            if stock > 0:
                self.carrito.append(producto)
                self.cantidades[pid] = 1
        else:
            if self.cantidades[pid] < stock:
                self.cantidades[pid] += 1

        self.actualizar_tabla_carrito()

    # ---------------------------
    # Confirmar eliminación
    # ---------------------------
    def confirmar_eliminar(self, producto):
        pid, nombre, _, _, _ = producto

        box = Bx(orientation="vertical", padding=dp(15), spacing=dp(10))
        box.add_widget(Label(text=f"¿Deseas eliminar '{nombre}' del carrito?", color=(1, 1, 1, 1)))

        botones = Bx(size_hint_y=None, height=dp(40), spacing=dp(10))
        btn_si = Button(
            text="Sí", background_color=(0.8, 0.1, 0.1, 1), color=(1, 1, 1, 1),
            on_release=lambda x: self._confirmar_si(producto, popup)
        )
        btn_no = Button(
            text="No", background_color=(0.3, 0.3, 0.3, 1), color=(1, 1, 1, 1),
            on_release=lambda x: popup.dismiss()
        )
        botones.add_widget(btn_si)
        botones.add_widget(btn_no)
        box.add_widget(botones)

        popup = Popup(
            title="Confirmar eliminación",
            content=box,
            size_hint=(None, None),
            size=(400, 200),
            auto_dismiss=False
        )
        popup.open()

    def _confirmar_si(self, producto, popup):
        popup.dismiss()
        self.quitar_de_venta(producto)

    # ---------------------------
    # Quitar producto del carrito
    # ---------------------------
    def quitar_de_venta(self, producto):
        pid = producto[0]
        if producto in self.carrito:
            self.carrito.remove(producto)
        if pid in self.cantidades:
            del self.cantidades[pid]
        self.actualizar_tabla_carrito()

    # ---------------------------
    # Incrementar / Decrementar cantidad (respetando stock)
    # ---------------------------
    def inc_cantidad(self, pid):
        stock_max = self.stock_productos.get(pid, 0)
        actual = self.cantidades.get(pid, 1)
        if actual < stock_max:
            self.cantidades[pid] = actual + 1
            self.actualizar_tabla_carrito()

    def dec_cantidad(self, pid):
        actual = self.cantidades.get(pid, 1)
        if actual > 1:
            self.cantidades[pid] = actual - 1
            self.actualizar_tabla_carrito()

    # ---------------------------
    # Actualizar tabla carrito
    # ---------------------------
    def actualizar_tabla_carrito(self):
        contenedor = self.ids.tabla_carrito
        contenedor.clear_widgets()
        total = 0

        if not self.carrito:
            contenedor.add_widget(Label(text="No hay productos agregados", color=(1, 1, 1, 1)))
            self.ids.lbl_total.text = "Total: $0.00"
            return

        for producto in self.carrito:
            pid, nombre, desc, precio, stock = producto
            qty = self.cantidades.get(pid, 1)
            stock_disp = self.stock_productos.get(pid, 0)

            fila = Bx(size_hint_y=None, height=dp(35), spacing=dp(10))
            fila.add_widget(Label(text=str(pid), color=(0, 0, 0, 1)))
            fila.add_widget(Label(text=nombre, color=(0, 0, 0, 1)))

            cont = Bx(size_hint_x=None, width=dp(140), spacing=dp(4))
            btn_menos = Button(
                text="-", size_hint_x=None, width=dp(40),
                background_color=(0.9, 0.2, 0.2, 1), color=(1, 1, 1, 1),
                on_release=lambda x, _pid=pid: self.dec_cantidad(_pid)
            )
            lbl_qty = Label(text=f"{qty}/{stock_disp}", size_hint_x=None, width=dp(60), color=(0, 0, 0, 1))
            btn_mas = Button(
                text="+", size_hint_x=None, width=dp(40),
                background_color=(0.1, 0.7, 0.6, 1), color=(1, 1, 1, 1),
                on_release=lambda x, _pid=pid: self.inc_cantidad(_pid)
            )
            cont.add_widget(btn_menos)
            cont.add_widget(lbl_qty)
            cont.add_widget(btn_mas)
            fila.add_widget(cont)

            fila.add_widget(Label(text=f"${float(precio) * qty:.2f}", color=(0, 0, 0, 1)))

            btn_quitar = Button(
                text="Eliminar", size_hint_x=None, width=dp(100),
                background_color=(0.8, 0.1, 0.1, 1), color=(1, 1, 1, 1),
                on_release=lambda x, p=producto: self.confirmar_eliminar(p)
            )
            fila.add_widget(btn_quitar)

            contenedor.add_widget(fila)
            total += float(precio) * qty

        self.ids.lbl_total.text = f"Total: ${total:.2f}"

    # ---------------------------
    # Previsualizar venta (tabla con scroll)
    # ---------------------------
    def previsualizar_venta(self):
        """Muestra un resumen visual de los productos antes de confirmar."""
        if not self.carrito:
            popup = Popup(
                title="Sin productos",
                content=Label(text="No hay productos en la venta actual.", color=(1, 1, 1, 1)),
                size_hint=(None, None),
                size=(350, 150)
            )
            popup.open()
            return

        resumen = Bx(orientation="vertical", spacing=dp(10), padding=dp(10))
        resumen.add_widget(Label(text="Resumen de Venta", font_size=dp(22), bold=True, color=(1, 1, 1, 1)))

        # Encabezado
        encabezado = Bx(size_hint_y=None, height=dp(25), spacing=dp(5))
        encabezado.add_widget(Label(text="Producto", bold=True, color=(1, 1, 1, 1)))
        encabezado.add_widget(Label(text="Cant.", bold=True, color=(1, 1, 1, 1), size_hint_x=None, width=dp(50)))
        encabezado.add_widget(Label(text="Precio", bold=True, color=(1, 1, 1, 1), size_hint_x=None, width=dp(80)))
        encabezado.add_widget(Label(text="Subtotal", bold=True, color=(1, 1, 1, 1), size_hint_x=None, width=dp(100)))
        resumen.add_widget(encabezado)

        # Scroll con productos
        scroll = ScrollView(size_hint=(1, 1))
        lista_productos = Bx(orientation="vertical", size_hint_y=None, spacing=dp(5))
        lista_productos.bind(minimum_height=lista_productos.setter("height"))

        total_general = 0
        for producto in self.carrito:
            pid, nombre, desc, precio, stock = producto
            cantidad = self.cantidades.get(pid, 1)
            subtotal = float(precio) * cantidad
            total_general += subtotal

            fila = Bx(size_hint_y=None, height=dp(25))
            fila.add_widget(Label(text=nombre, color=(1, 1, 1, 1)))
            fila.add_widget(Label(text=f"x{cantidad}", color=(1, 1, 1, 1), size_hint_x=None, width=dp(50)))
            fila.add_widget(Label(text=f"${float(precio):.2f}", color=(1, 1, 1, 1), size_hint_x=None, width=dp(80)))
            fila.add_widget(Label(text=f"${subtotal:.2f}", color=(1, 1, 1, 1), size_hint_x=None, width=dp(100)))
            lista_productos.add_widget(fila)

        scroll.add_widget(lista_productos)
        resumen.add_widget(scroll)

        # Total general
        resumen.add_widget(Label(
            text=f"TOTAL GENERAL: ${total_general:.2f}",
            font_size=dp(20), bold=True, color=(1, 1, 1, 1)
        ))

        # Botones
        botones = Bx(size_hint_y=None, height=dp(45), spacing=dp(10))
        btn_confirmar = Button(
            text="Confirmar Venta", background_color=(0.1, 0.6, 0.3, 1),
            color=(1, 1, 1, 1), on_release=lambda x: self.confirmar_venta(popup)
        )
        btn_cancelar = Button(
            text="Cancelar", background_color=(0.6, 0.1, 0.1, 1),
            color=(1, 1, 1, 1), on_release=lambda x: popup.dismiss()
        )
        botones.add_widget(btn_confirmar)
        botones.add_widget(btn_cancelar)
        resumen.add_widget(botones)

        popup = Popup(
            title="Previsualización de Venta",
            content=resumen,
            size_hint=(None, None),
            size=(600, 500),
            auto_dismiss=False
        )
        popup.open()

    # ---------------------------
    # Confirmar venta
    # ---------------------------
    def confirmar_venta(self, popup):
        popup.dismiss()
        self.carrito.clear()
        self.cantidades.clear()
        self.actualizar_tabla_carrito()

        confirm_popup = Popup(
            title="Venta confirmada",
            content=Label(text="La venta se ha confirmado exitosamente.", color=(1, 1, 1, 1)),
            size_hint=(None, None),
            size=(350, 150)
        )
        confirm_popup.open()
