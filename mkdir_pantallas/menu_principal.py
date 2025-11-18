from kivy.uix.screenmanager import Screen
from kivy.clock import Clock
from kivy.properties import StringProperty
from datetime import datetime
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.metrics import dp
from kivy.uix.popup import Popup
from kivy.uix.boxlayout import BoxLayout

try:
    from mkdir_database.conexion import ejecutar_consulta
except:
    ejecutar_consulta = None


class MenuPrincipalScreen(Screen):

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

    # -------------------------------------------------------------------
    # RELOJ
    # -------------------------------------------------------------------
    def _actualizar_hora(self, dt):
        self.hora_actual = datetime.now().strftime("%H:%M:%S")

    # -------------------------------------------------------------------
    # NAVEGACIÓN
    # -------------------------------------------------------------------
    def volver_al_login(self):
        self.manager.current = "login"

    def volver_al_menu(self):
        self.manager.current = "menu_principal"

    # -------------------------------------------------------------------
    # SALIR DEL SISTEMA
    # -------------------------------------------------------------------
    def confirmar_salida(self):
        box = BoxLayout(orientation="vertical", padding=dp(15), spacing=dp(10))
        box.add_widget(Label(text="¿Deseas salir?", color=(0, 0, 0, 1)))

        botones = BoxLayout(size_hint_y=None, height=dp(40), spacing=dp(10))
        btn_si = Button(text="Sí", background_color=(0.8, 0.1, 0.1, 1),
                        color=(1, 1, 1, 1), on_release=lambda x: exit())
        btn_no = Button(text="No", background_color=(0.3, 0.3, 0.3, 1),
                        color=(1, 1, 1, 1), on_release=lambda x: popup.dismiss())
        botones.add_widget(btn_si)
        botones.add_widget(btn_no)

        box.add_widget(botones)

        popup = Popup(
            title="Salir",
            content=box,
            size_hint=(None, None),
            size=(400, 200),
            auto_dismiss=False
        )
        popup.open()

    # -------------------------------------------------------------------
    # BÚSQUEDA PROGRAMADA
    # -------------------------------------------------------------------
    def programar_busqueda(self, texto):
        if self._evento_busqueda:
            self._evento_busqueda.cancel()

        self._evento_busqueda = Clock.schedule_once(
            lambda dt: self.buscar_producto(texto), 0.6
        )

    # -------------------------------------------------------------------
    # BUSCAR PRODUCTOS
    # -------------------------------------------------------------------
    def buscar_producto(self, texto):
        texto = (texto or "").strip()
        contenedor = self.ids.tabla_productos
        contenedor.clear_widgets()

        if not texto:
            contenedor.add_widget(Label(text="Escribe algo...", color=(0, 0, 0, 1)))
            return

        if ejecutar_consulta is None:
            contenedor.add_widget(Label(text="Sin conexión", color=(0, 0, 0, 1)))
            return

        try:
            consulta = """
                SELECT ProductoID, Nombre, Descripcion, Precio, Stock
                FROM Productos
                WHERE Nombre LIKE ? OR CodigoBarras LIKE ?
                ORDER BY Nombre
                LIMIT 50
            """

            param = f"%{texto}%"
            filas = ejecutar_consulta(consulta, (param, param))

        except Exception as e:
            contenedor.add_widget(Label(text=f"Error: {e}", color=(0, 0, 0, 1)))
            return

        if not filas:
            contenedor.add_widget(Label(text="No hay resultados", color=(0, 0, 0, 1)))
            return

        for fila in filas:
            pid, nombre, desc, precio, stock = fila
            self.stock_productos[pid] = int(stock)

            fila_layout = BoxLayout(size_hint_y=None, height=dp(35), spacing=dp(10))
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
                on_release=lambda x, p=fila: self.agregar_a_venta(p)
            )

            fila_layout.add_widget(btn_agregar)
            contenedor.add_widget(fila_layout)

    # -------------------------------------------------------------------
    # AGREGAR PRODUCTO AL CARRITO
    # -------------------------------------------------------------------
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

    # -------------------------------------------------------------------
    # QUITAR UN PRODUCTO
    # -------------------------------------------------------------------
    def quitar_de_venta(self, producto):
        pid = producto[0]

        if producto in self.carrito:
            self.carrito.remove(producto)

        if pid in self.cantidades:
            del self.cantidades[pid]

        self.actualizar_tabla_carrito()

    # -------------------------------------------------------------------
    # ACTUALIZAR TABLA CARRITO
    # -------------------------------------------------------------------
    def actualizar_tabla_carrito(self):
        contenedor = self.ids.tabla_carrito
        contenedor.clear_widgets()
        total = 0.0

        for producto in self.carrito:
            pid = producto[0]
            cantidad = self.cantidades.get(pid, 1)
            precio = float(producto[3])
            subtotal = precio * cantidad
            total += subtotal

            fila = BoxLayout(size_hint_y=None, height=dp(35), spacing=dp(10))
            fila.add_widget(Label(text=producto[1], color=(0, 0, 0, 1)))
            fila.add_widget(Label(text=f"Cantidad: {cantidad}", color=(0, 0, 0, 1)))
            fila.add_widget(Label(text=f"Subtotal: ${subtotal:.2f}", color=(0, 0, 0, 1)))

            btn = Button(
                text="Eliminar",
                size_hint_x=None,
                width=dp(100),
                background_color=(0.8, 0.1, 0.1, 1),
                color=(1, 1, 1, 1),
                on_release=lambda x, p=producto: self.quitar_de_venta(p)
            )

            fila.add_widget(btn)
            contenedor.add_widget(fila)

        self.ids.lbl_total.text = f"Total: ${total:.2f}"

    # -------------------------------------------------------------------
    # IR A FACTURACIÓN (CORREGIDO Y FUNCIONAL)
    # -------------------------------------------------------------------
    def ir_a_facturacion(self):

        factura = self.manager.get_screen("factura")

        # ---- PASAR CARRITO ----
        carrito_formateado = []
        for p in self.carrito:
            pid, nombre, desc, precio, stock = p
            cantidad = self.cantidades.get(pid, 1)

            carrito_formateado.append({
                "id": pid,
                "nombre": nombre,
                "precio": float(precio),
                "cantidad": cantidad,
                "subtotal": float(precio) * cantidad
            })

        factura.set_carrito_inicial(carrito_formateado)

        # ---- CARGAR PRODUCTOS DISPONIBLES ----
        filas = ejecutar_consulta("SELECT ProductoID, Nombre, Precio FROM Productos")
        lista = [{"id": f[0], "nombre": f[1], "precio": float(f[2])} for f in filas]

        factura.productos_disponibles = lista

        if hasattr(factura, "on_pre_enter"):
            factura.on_pre_enter()

        self.manager.current = "factura"
