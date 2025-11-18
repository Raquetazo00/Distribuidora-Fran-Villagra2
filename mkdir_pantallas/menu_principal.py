from kivy.uix.boxlayout import BoxLayout
from kivy.clock import Clock
from kivy.properties import StringProperty
from datetime import datetime
from kivy.uix.label import Label
from kivy.uix.boxlayout import BoxLayout as Bx
from kivy.uix.button import Button
from kivy.metrics import dp
from kivy.uix.popup import Popup
from kivy.uix.scrollview import ScrollView

try:
    from mkdir_database.conexion import ejecutar_consulta
except:
    from conexion import ejecutar_consulta


class MenuPrincipalScreen(BoxLayout):
    hora_actual = StringProperty("00:00:00")
    _evento_busqueda = None

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        Clock.schedule_interval(self._actualizar_hora, 1)

        self.carrito = []
        self.cantidades = {}
        self.stock_productos = {}

    # ---------------------------
    # Reloj
    # ---------------------------
    def _actualizar_hora(self, dt):
        self.hora_actual = datetime.now().strftime("%H:%M:%S")

    # ---------------------------
    # Ir a clientes
    # ---------------------------
    def ir_clientes(self):
        from mkdir_pantallas.clientes import ClientesScreen
        self.clear_widgets()
        pantalla = ClientesScreen()
        pantalla.cargar_clientes()
        self.add_widget(pantalla)

    # ---------------------------
    # Buscar producto
    # ---------------------------
    def programar_busqueda(self, texto):
        if self._evento_busqueda:
            self._evento_busqueda.cancel()
        self._evento_busqueda = Clock.schedule_once(
            lambda dt: self.buscar_producto(texto), 0.5
        )

    def buscar_producto(self, texto):
        texto = (texto or "").strip()
        tabla = self.ids.tabla_productos
        tabla.clear_widgets()

        if not texto:
            tabla.add_widget(Label(text="Escribe algo para buscar...", color=(0, 0, 0, 1)))
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
            tabla.add_widget(Label(text=f"Error: {e}", color=(1, 0, 0, 1)))
            return

        if not filas:
            tabla.add_widget(Label(text="No se encontraron productos.", color=(0, 0, 0, 1)))
            return

        for pid, nombre, desc, precio, stock in filas:
            self.stock_productos[pid] = int(stock)

            fila = Bx(size_hint_y=None, height=dp(35), spacing=dp(10))
            fila.add_widget(Label(text=str(pid), color=(0, 0, 0, 1)))
            fila.add_widget(Label(text=nombre, color=(0, 0, 0, 1)))
            fila.add_widget(Label(text=f"${float(precio):.2f}", color=(0, 0, 0, 1)))
            fila.add_widget(Label(text=f"Stock: {stock}", color=(0, 0, 0, 1)))

            btn = Button(
                text="Agregar",
                size_hint_x=None,
                width=dp(100),
                background_color=(0, 0.6, 0.2, 1),
                color=(1, 1, 1, 1),
                on_release=lambda x, p=(pid, nombre, desc, precio, stock): self.agregar_a_venta(p)
            )
            fila.add_widget(btn)
            tabla.add_widget(fila)

    # ---------------------------
    # Agregar al carrito
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
    # Incrementar / Decrementar
    # ---------------------------
    def inc_cantidad(self, pid):
        stock = self.stock_productos.get(pid, 0)
        actual = self.cantidades.get(pid, 1)
        if actual < stock:
            self.cantidades[pid] = actual + 1
        self.actualizar_tabla_carrito()

    def dec_cantidad(self, pid):
        actual = self.cantidades.get(pid, 1)
        if actual > 1:
            self.cantidades[pid] = actual - 1
        self.actualizar_tabla_carrito()

    # ---------------------------
    # Quitar producto
    # ---------------------------
    def eliminar_producto(self, producto):
        pid = producto[0]
        if producto in self.carrito:
            self.carrito.remove(producto)
        if pid in self.cantidades:
            del self.cantidades[pid]
        self.actualizar_tabla_carrito()

    # ---------------------------
    # Actualizar tabla carrito
    # ---------------------------
    def actualizar_tabla_carrito(self):
        tabla = self.ids.tabla_carrito
        tabla.clear_widgets()
        total = 0

        if not self.carrito:
            tabla.add_widget(Label(text="No hay productos agregados", color=(0, 0, 0, 1)))
            self.ids.lbl_total.text = "Total: $0.00"
            return

        for pid, nombre, desc, precio, stock in self.carrito:
            qty = self.cantidades[pid]
            subtotal = float(precio) * qty
            total += subtotal

            fila = Bx(size_hint_y=None, height=dp(35), spacing=dp(10))
            fila.add_widget(Label(text=nombre, color=(0, 0, 0, 1)))

            cantidad_box = Bx(size_hint_x=None, width=dp(140), spacing=dp(5))
            cantidad_box.add_widget(
                Button(text="-", width=dp(40), size_hint_x=None,
                       background_color=(0.9, 0.2, 0.2, 1), color=(1, 1, 1, 1),
                       on_release=lambda x, _pid=pid: self.dec_cantidad(_pid))
            )

            cantidad_box.add_widget(
                Label(text=f"{qty}/{stock}", width=dp(60), size_hint_x=None, color=(0, 0, 0, 1))
            )

            cantidad_box.add_widget(
                Button(text="+", width=dp(40), size_hint_x=None,
                       background_color=(0.1, 0.7, 0.5, 1), color=(1, 1, 1, 1),
                       on_release=lambda x, _pid=pid: self.inc_cantidad(_pid))
            )

            fila.add_widget(cantidad_box)
            fila.add_widget(Label(text=f"${subtotal:.2f}", color=(0, 0, 0, 1)))

            fila.add_widget(
                Button(text="Eliminar", width=dp(100), size_hint_x=None,
                       background_color=(0.7, 0.1, 0.1, 1), color=(1, 1, 1, 1),
                       on_release=lambda x, p=(pid, nombre, desc, precio, stock): self.eliminar_producto(p))
            )

            tabla.add_widget(fila)

        self.ids.lbl_total.text = f"Total: ${total:.2f}"

    # ---------------------------
    # Previsualizar -> Ir a Facturación
    # ---------------------------
    def previsualizar_venta(self):
        if not self.carrito:
            Popup(
                title="Sin productos",
                content=Label(text="Agrega productos primero.", color=(1, 1, 1, 1)),
                size_hint=(None, None), size=(300, 150)
            ).open()
            return

        resumen = Bx(orientation="vertical", spacing=dp(10), padding=dp(10))
        resumen.add_widget(Label(text="Resumen de Venta", font_size=dp(22), bold=True, color=(1, 1, 1, 1)))

        scroll = ScrollView()
        lista = Bx(orientation="vertical", size_hint_y=None)
        lista.bind(minimum_height=lista.setter("height"))

        total = 0
        for pid, nombre, desc, precio, stock in self.carrito:
            qty = self.cantidades[pid]
            subtotal = float(precio) * qty
            total += subtotal

            fila = Bx(size_hint_y=None, height=dp(25))
            fila.add_widget(Label(text=nombre, color=(1, 1, 1, 1)))
            fila.add_widget(Label(text=f"x{qty}", color=(1, 1, 1, 1)))
            fila.add_widget(Label(text=f"${subtotal:.2f}", color=(1, 1, 1, 1)))
            lista.add_widget(fila)

        scroll.add_widget(lista)
        resumen.add_widget(scroll)

        resumen.add_widget(
            Label(text=f"TOTAL: ${total:.2f}", font_size=dp(20), bold=True, color=(1, 1, 1, 1))
        )

        botones = Bx(size_hint_y=None, height=dp(40), spacing=dp(10))

        btn_ok = Button(
            text="Confirmar", background_color=(0, 0.7, 0.3, 1), color=(1, 1, 1, 1),
            on_release=lambda x: self.ir_a_facturacion(popup)
        )
        btn_cancel = Button(
            text="Cancelar", background_color=(0.8, 0.1, 0.1, 1),
            color=(1, 1, 1, 1), on_release=lambda x: popup.dismiss()
        )

        botones.add_widget(btn_ok)
        botones.add_widget(btn_cancel)
        resumen.add_widget(botones)

        popup = Popup(
            title="Previsualización",
            content=resumen,
            size_hint=(None, None), size=(600, 500)
        )
        popup.open()

    # ---------------------------
    # IR A FACTURACIÓN (CORREGIDO)
    # ---------------------------
    def ir_a_facturacion(self, popup):
        from mkdir_pantallas.facturacion import FacturaScreen

        # formatear carrito
        carrito_formateado = []
        for pid, nombre, desc, precio, stock in self.carrito:
            qty = self.cantidades[pid]
            carrito_formateado.append({
                "id": pid,
                "nombre": nombre,
                "precio": float(precio),
                "cantidad": qty,
                "subtotal": float(precio) * qty
            })

        # crear pantalla de factura
        factura = FacturaScreen()
        factura.set_carrito_inicial(carrito_formateado)

        # cargar productos disponibles
        try:
            filas = ejecutar_consulta("SELECT ProductoID, Nombre, Precio FROM Productos", ())
            factura.productos_disponibles = [
                {"id": f[0], "nombre": f[1], "precio": float(f[2])}
                for f in filas
            ]
        except Exception as e:
            print("Error cargando productos para facturación:", e)

        popup.dismiss()

        # REEMPLAZA la pantalla actual con la de facturación SIN usar ScreenManager
        self.clear_widgets()
        self.add_widget(factura)


    # ---------------------------
    # Salir
    # ---------------------------
    def confirmar_salida(self):
        box = Bx(orientation="vertical", spacing=dp(10), padding=dp(15))
        box.add_widget(Label(text="¿Deseas salir al login?", color=(1, 1, 1, 1)))

        botones = Bx(size_hint_y=None, height=dp(40), spacing=dp(10))

        btn_si = Button(
            text="Sí", background_color=(0.9, 0.2, 0.2, 1),
            color=(1, 1, 1, 1),
            on_release=lambda x: self._salir_confirmado(popup)
        )
        btn_no = Button(
            text="No", background_color=(0.3, 0.3, 0.3, 1),
            color=(1, 1, 1, 1),
            on_release=lambda x: popup.dismiss()
        )

        botones.add_widget(btn_si)
        botones.add_widget(btn_no)
        box.add_widget(botones)

        popup = Popup(title="Salir", content=box, size_hint=(None, None), size=(350, 180))
        popup.open()

    def _salir_confirmado(self, popup):
        popup.dismiss()
        from mkdir_pantallas.login import LoginScreen
        self.clear_widgets()
        self.add_widget(LoginScreen())
