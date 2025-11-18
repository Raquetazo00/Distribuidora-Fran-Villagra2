from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.metrics import dp

try:
    from mkdir_database.conexion import ejecutar_consulta
except Exception:
    ejecutar_consulta = None


class AgregarProductoScreen(Screen):
    producto_editando_id = None

    def on_pre_enter(self, *args):
        """Cuando se entra a la pantalla, cargar productos."""
        self.mostrar_productos()

    # ------------------------------
    # AGREGAR o ACTUALIZAR
    # ------------------------------
    def agregar_o_actualizar_producto(self):
        nombre = self.ids.nombre_input.text.strip()
        descripcion = self.ids.descripcion_input.text.strip()
        precio = self.ids.precio_input.text.strip()
        stock = self.ids.stock_input.text.strip()
        codigo_barras = self.ids.codigo_input.text.strip()

        if not ejecutar_consulta:
            print("⚠️ ejecutar_consulta no configurado")
            return

        if not nombre or not precio or not stock:
            print("⚠️ Debes completar al menos nombre, precio y stock.")
            return

        try:
            precio_val = float(precio)
            stock_val = int(stock)
        except ValueError:
            print("⚠️ Precio o stock inválidos.")
            return

        try:
            if self.producto_editando_id is None:
                consulta = """
                    INSERT INTO Productos (Nombre, Descripcion, Precio, Stock, CodigoBarras, Activo)
                    VALUES (?, ?, ?, ?, ?, 1)
                """
                parametros = (nombre, descripcion, precio_val, stock_val, codigo_barras)
                ejecutar_consulta(consulta, parametros)
                print("✅ Producto agregado correctamente.")
            else:
                consulta = """
                    UPDATE Productos
                    SET Nombre=?, Descripcion=?, Precio=?, Stock=?, CodigoBarras=?
                    WHERE ProductoID=?
                """
                parametros = (
                    nombre, descripcion, precio_val, stock_val,
                    codigo_barras, self.producto_editando_id
                )
                ejecutar_consulta(consulta, parametros)
                print(f"🟢 Producto {self.producto_editando_id} actualizado.")
                self.producto_editando_id = None
                self.ids.boton_agregar.text = "Agregar Producto"

            self.limpiar_campos()
            self.mostrar_productos()
        except Exception as e:
            print(f"❌ Error al guardar producto: {e}")

    # ------------------------------
    # LIMPIAR CAMPOS
    # ------------------------------
    def limpiar_campos(self):
        self.ids.nombre_input.text = ""
        self.ids.descripcion_input.text = ""
        self.ids.precio_input.text = ""
        self.ids.stock_input.text = ""
        self.ids.codigo_input.text = ""

    # ------------------------------
    # VOLVER AL PANEL ADMIN
    # ------------------------------
    def volver_al_panel(self):
        self.manager.current = "admin"  # Asegurate que el Screen se llame "admin"

    # ------------------------------
    # CARGAR PRODUCTOS
    # ------------------------------
    def mostrar_productos(self):
        contenedor = self.ids.tabla_productos
        contenedor.clear_widgets()

        if not ejecutar_consulta:
            contenedor.add_widget(Label(text="Sin conexión a BD", color=(0, 0, 0, 1)))
            return

        try:
            consulta = """
                SELECT ProductoID, Nombre, Descripcion, Precio, Stock, CodigoBarras
                FROM Productos
                WHERE Activo = 1
                ORDER BY Nombre
            """
            filas = ejecutar_consulta(consulta)
        except Exception as e:
            contenedor.add_widget(Label(text=f"Error al cargar: {e}", color=(0, 0, 0, 1)))
            return

        if not filas:
            contenedor.add_widget(Label(text="No hay productos cargados.", color=(0, 0, 0, 1)))
            return

        for fila in filas:
            pid, nombre, desc, precio, stock, cod_barras = fila

            fila_layout = BoxLayout(size_hint_y=None, height=dp(35), spacing=dp(10))
            fila_layout.add_widget(Label(text=str(pid), color=(0, 0, 0, 1)))
            fila_layout.add_widget(Label(text=nombre, color=(0, 0, 0, 1)))
            fila_layout.add_widget(Label(text=f"${float(precio):.2f}", color=(0, 0, 0, 1)))
            fila_layout.add_widget(Label(text=f"Stock: {stock}", color=(0, 0, 0, 1)))
            fila_layout.add_widget(Label(text=f"CB: {cod_barras or '-'}", color=(0, 0, 0, 1)))

            # Botón editar (solo visual, puedes implementar lógica luego)
            btn_editar = Button(
                text="Editar",
                size_hint_x=None,
                width=dp(80),
                on_release=lambda x, p=fila: self.cargar_en_formulario(p)
            )
            fila_layout.add_widget(btn_editar)

            contenedor.add_widget(fila_layout)

    # ------------------------------
    # BUSCAR PRODUCTOS
    # ------------------------------
    def buscar_productos(self):
        texto = self.ids.buscar_input.text.strip()
        if not texto:
            self.mostrar_productos()
            return

        contenedor = self.ids.tabla_productos
        contenedor.clear_widgets()

        if not ejecutar_consulta:
            contenedor.add_widget(Label(text="Sin conexión a BD", color=(0, 0, 0, 1)))
            return

        try:
            consulta = """
                SELECT ProductoID, Nombre, Descripcion, Precio, Stock, CodigoBarras
                FROM Productos
                WHERE (Nombre LIKE ? OR CodigoBarras LIKE ?)
                  AND Activo = 1
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
            pid, nombre, desc, precio, stock, cod_barras = fila

            fila_layout = BoxLayout(size_hint_y=None, height=dp(35), spacing=dp(10))
            fila_layout.add_widget(Label(text=str(pid), color=(0, 0, 0, 1)))
            fila_layout.add_widget(Label(text=nombre, color=(0, 0, 0, 1)))
            fila_layout.add_widget(Label(text=f"${float(precio):.2f}", color=(0, 0, 0, 1)))
            fila_layout.add_widget(Label(text=f"Stock: {stock}", color=(0, 0, 0, 1)))
            fila_layout.add_widget(Label(text=f"CB: {cod_barras or '-'}", color=(0, 0, 0, 1)))

            btn_editar = Button(
                text="Editar",
                size_hint_x=None,
                width=dp(80),
                on_release=lambda x, p=fila: self.cargar_en_formulario(p)
            )
            fila_layout.add_widget(btn_editar)

            contenedor.add_widget(fila_layout)

    # ------------------------------
    # Cargar producto en formulario para editar
    # ------------------------------
    def cargar_en_formulario(self, fila):
        pid, nombre, desc, precio, stock, cod_barras = fila
        self.producto_editando_id = pid
        self.ids.nombre_input.text = nombre or ""
        self.ids.descripcion_input.text = desc or ""
        self.ids.precio_input.text = str(precio)
        self.ids.stock_input.text = str(stock)
        self.ids.codigo_input.text = cod_barras or ""
        self.ids.boton_agregar.text = "Actualizar Producto"
