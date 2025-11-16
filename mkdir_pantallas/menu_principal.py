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

    def volver_al_login(self):
        """Volver a la pantalla de login"""
        from mkdir_pantallas.login import LoginScreen
        self.clear_widgets()
        self.add_widget(LoginScreen())

    def ir_a_facturacion(self):
        """Navega a la pantalla de facturación"""
        from mkdir_pantallas.facturacion import FacturacionScreen
        self.clear_widgets()
        self.add_widget(FacturacionScreen())

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
                SELECT ProductoID, Nombre, Descripcion, Precio, Stock
                FROM Productos
                WHERE Nombre LIKE ? OR CodigoBarras LIKE ?
                ORDER BY Nombre
                LIMIT 50
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
            on_release=lambda x, p=producto: self._confirmar_si(p, popup)
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
