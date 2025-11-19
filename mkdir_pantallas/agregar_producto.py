from kivymd.uix.screen import MDScreen
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.button import MDRaisedButton
from kivymd.uix.label import MDLabel
from kivy.metrics import dp
from kivy.clock import Clock
from kivy.app import App

from mkdir_database.conexion import ejecutar_consulta


class AgregarProductoScreen(MDScreen):

    tabla = None
    producto_editando_id = None

    def on_enter(self, *args):
        """Cargar productos al entrar a la pantalla"""
        Clock.schedule_once(lambda dt: self.mostrar_productos(), 0.2)

    # ========================================================
    # AGREGAR O ACTUALIZAR PRODUCTO
    # ========================================================
    def agregar_o_actualizar_producto(self):
        nombre = self.ids.nombre_input.text.strip()
        descripcion = self.ids.descripcion_input.text.strip()
        precio = self.ids.precio_input.text.strip()
        stock = self.ids.stock_input.text.strip()
        fecha = self.ids.fecha_input.text.strip()
        codigo = self.ids.codigo_input.text.strip()

        if not nombre or not precio or not stock:
            print("⚠ Debes completar nombre, precio y stock.")
            return

        try:
            if self.producto_editando_id is None:
                consulta = """
                    INSERT INTO Productos (Nombre, Descripcion, Precio, Stock, FechaVencimiento, CodigoBarras)
                    VALUES (?, ?, ?, ?, ?, ?)
                """
                ejecutar_consulta(
                    consulta,
                    (nombre, descripcion, float(precio), int(stock), fecha or None, codigo)
                )
                print("🟢 Producto agregado.")
            else:
                consulta = """
                    UPDATE Productos
                    SET Nombre=?, Descripcion=?, Precio=?, Stock=?, FechaVencimiento=?, CodigoBarras=?
                    WHERE ProductoID=?
                """
                ejecutar_consulta(
                    consulta,
                    (nombre, descripcion, float(precio), int(stock),
                     fecha or None, codigo, self.producto_editando_id)
                )
                print("🟢 Producto actualizado.")
                self.producto_editando_id = None
                self.ids.boton_agregar.text = "Agregar Producto"

            self.limpiar_campos()
            self.mostrar_productos()

        except Exception as e:
            print("❌ Error:", e)

    # ========================================================
    # BUSCADOR
    # ========================================================
    def buscar_productos(self):
        texto = self.ids.buscar_input.text.strip()
        if texto == "":
            self.mostrar_productos()
            return

        consulta = """
            SELECT ProductoID, Nombre, Descripcion, Precio, Stock
            FROM Productos
            WHERE Nombre LIKE ? OR CodigoBarras LIKE ?
        """
        like = f"%{texto}%"
        resultados = ejecutar_consulta(consulta, (like, like))
        self.mostrar_productos(resultados)

    # ========================================================
    # TABLA MANUAL MEJORADA VISUALMENTE
    # ========================================================
    def mostrar_productos(self, resultados=None):

        contenedor = self.ids.tabla_productos
        contenedor.clear_widgets()

        # Cargar todos los productos
        if resultados is None:
            resultados = ejecutar_consulta(
                "SELECT ProductoID, Nombre, Descripcion, Precio, Stock FROM Productos"
            )

        # ---------- ENCABEZADO ----------
        header = MDBoxLayout(
            orientation="horizontal",
            spacing=dp(10),
            size_hint_y=None,
            height=dp(40),
            padding=dp(5),
            md_bg_color=(0.90, 0.90, 0.92, 1),
            radius=[10]
        )

        for title in ["ID", "Nombre", "Descripción", "Precio", "Stock", "Editar", "Eliminar"]:
            header.add_widget(MDLabel(text=title, bold=True, halign="center"))

        contenedor.add_widget(header)

        # ---------- FILAS ----------
        for i, producto in enumerate(resultados):
            pid, nombre, descripcion, precio, stock = producto

            bg_color = (0.97, 0.97, 0.97, 1) if i % 2 == 0 else (1, 1, 1, 1)

            fila = MDBoxLayout(
                orientation="horizontal",
                spacing=dp(10),
                size_hint_y=None,
                height=dp(40),
                padding=dp(5),
                md_bg_color=bg_color,
                radius=[10]
            )

            fila.add_widget(MDLabel(text=str(pid), halign="center"))
            fila.add_widget(MDLabel(text=nombre, halign="center"))
            fila.add_widget(MDLabel(text=descripcion or "", halign="center"))
            fila.add_widget(MDLabel(text=f"{precio:,.2f}", halign="center"))
            fila.add_widget(MDLabel(text=str(stock), halign="center"))

            # Botón editar
            btn_editar = MDRaisedButton(
                text="Editar",
                md_bg_color=(0, 0.6, 0.2, 1),
                size_hint=(None, None),
                width=dp(80),
                height=dp(32),
                on_release=lambda x, id=pid: self.editar_producto(id)
            )

            # Botón eliminar
            btn_eliminar = MDRaisedButton(
                text="Eliminar",
                md_bg_color=(0.8, 0, 0, 1),
                size_hint=(None, None),
                width=dp(80),
                height=dp(32),
                on_release=lambda x, id=pid: self.eliminar_producto(id)
            )

            fila.add_widget(btn_editar)
            fila.add_widget(btn_eliminar)

            contenedor.add_widget(fila)

    # ========================================================
    # EDITAR PRODUCTO
    # ========================================================
    def editar_producto(self, pid):
        datos = ejecutar_consulta("SELECT * FROM Productos WHERE ProductoID=?", (pid,))
        if not datos:
            return

        p = datos[0]
        self.ids.nombre_input.text = p[1] or ""
        self.ids.descripcion_input.text = p[2] or ""
        self.ids.precio_input.text = str(p[3] or "")
        self.ids.stock_input.text = str(p[4] or "")
        self.ids.fecha_input.text = str(p[5] or "")
        self.ids.codigo_input.text = p[6] or ""

        self.producto_editando_id = pid
        self.ids.boton_agregar.text = "Guardar Cambios"

    # ========================================================
    # ELIMINAR PRODUCTO
    # ========================================================
    def eliminar_producto(self, pid):
        ejecutar_consulta("DELETE FROM Productos WHERE ProductoID=?", (pid,))
        print("🗑 Producto eliminado:", pid)
        self.mostrar_productos()

    # ========================================================
    # LIMPIAR CAMPOS
    # ========================================================
    def limpiar_campos(self):
        for campo in [
            "nombre_input", "descripcion_input", "precio_input",
            "stock_input", "fecha_input", "codigo_input"
        ]:
            self.ids[campo].text = ""

    # ========================================================
    # VOLVER
    # ========================================================
    def volver_al_panel(self):
        from mkdir_pantallas.panel_admin import PanelAdminScreen
        self.manager.switch_to(PanelAdminScreen())
