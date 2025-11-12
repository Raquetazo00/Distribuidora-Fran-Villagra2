from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.metrics import dp
from kivy.clock import Clock
from kivy.lang import Builder
import os
from mkdir_database.conexion import ejecutar_consulta

# Cargar el KV
ruta_kv = os.path.join(os.path.dirname(__file__), "agregar_producto.kv")
if os.path.exists(ruta_kv):
    Builder.load_file(ruta_kv)
    print("✅ agregar_producto.kv cargado correctamente.")
else:
    print("⚠️ No se encontró agregar_producto.kv en:", ruta_kv)


class AgregarProductoScreen(BoxLayout):
    producto_editando_id = None

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        Clock.schedule_once(self._esperar_tabla, 0.3)

    def _esperar_tabla(self, dt):
        if "tabla_productos" in self.ids:
            self.mostrar_productos()
        else:
            Clock.schedule_once(self._esperar_tabla, 0.2)

    # ------------------------------
    # AGREGAR o ACTUALIZAR
    # ------------------------------
    def agregar_o_actualizar_producto(self):
        nombre = self.ids.nombre_input.text.strip()
        descripcion = self.ids.descripcion_input.text.strip()
        precio = self.ids.precio_input.text.strip()
        stock = self.ids.stock_input.text.strip()
        fecha_venc = self.ids.fecha_input.text.strip()
        codigo_barras = self.ids.codigo_input.text.strip()

        if not nombre or not precio or not stock:
            print("⚠️ Debes completar al menos el nombre, precio y stock.")
            return

        try:
            if self.producto_editando_id is None:
                consulta = """
                    INSERT INTO Productos (Nombre, Descripcion, Precio, Stock, FechaVencimiento, CodigoBarras)
                    VALUES (?, ?, ?, ?, ?, ?)
                """
                parametros = (nombre, descripcion, float(precio), int(stock), fecha_venc or None, codigo_barras)
                ejecutar_consulta(consulta, parametros)
                print("✅ Producto agregado correctamente.")
            else:
                consulta = """
                    UPDATE Productos
                    SET Nombre=?, Descripcion=?, Precio=?, Stock=?, FechaVencimiento=?, CodigoBarras=?
                    WHERE ProductoID=?
                """
                parametros = (
                    nombre, descripcion, float(precio), int(stock), fecha_venc or None,
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
    # BUSCAR PRODUCTOS
    # ------------------------------
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
        parametro = f"%{texto}%"
        resultados = ejecutar_consulta(consulta, (parametro, parametro))
        self.mostrar_productos(resultados)

    # ------------------------------
    # MOSTRAR PRODUCTOS
    # ------------------------------
    def mostrar_productos(self, resultados=None):
        if "tabla_productos" not in self.ids:
            print("⚠️ No se encontró el id 'tabla_productos'")
            return

        contenedor = self.ids.tabla_productos
        contenedor.clear_widgets()

        if resultados is None:
            resultados = ejecutar_consulta(
                "SELECT ProductoID, Nombre, Descripcion, Precio, Stock FROM Productos"
            )

        if not resultados:
            contenedor.add_widget(Label(text="No hay productos registrados", color=(0, 0, 0, 1)))
            return

        header = GridLayout(cols=7, size_hint_y=None, height=dp(35))
        for titulo in ["ID", "Nombre", "Descripción", "Precio", "Stock", "Editar", "Eliminar"]:
            header.add_widget(Label(text=titulo, bold=True, color=(0, 0, 0, 1)))
        contenedor.add_widget(header)

        for fila in resultados:
            producto_id, nombre, desc, precio, stock = fila
            fila_layout = GridLayout(cols=7, size_hint_y=None, height=dp(35))
            for valor in [producto_id, nombre, desc, precio, stock]:
                fila_layout.add_widget(Label(text=str(valor), color=(0, 0, 0, 1)))

            btn_edit = Button(
                text="Editar",
                size_hint_x=None,
                width=dp(80),
                background_color=(0.0, 0.6, 0.0, 1),
                color=(1, 1, 1, 1),
                on_release=lambda btn, pid=producto_id: self.editar_producto(pid)
            )
            fila_layout.add_widget(btn_edit)

            btn_del = Button(
                text="Eliminar",
                size_hint_x=None,
                width=dp(80),
                background_color=(0.8, 0.1, 0.1, 1),
                color=(1, 1, 1, 1),
                on_release=lambda btn, pid=producto_id: self.eliminar_producto(pid)
            )
            fila_layout.add_widget(btn_del)

            contenedor.add_widget(fila_layout)

    # ------------------------------
    # EDITAR
    # ------------------------------
    def editar_producto(self, producto_id):
        consulta = "SELECT * FROM Productos WHERE ProductoID = ?"
        datos = ejecutar_consulta(consulta, (producto_id,))
        if not datos:
            print("⚠️ No se encontró el producto.")
            return

        producto = datos[0]
        self.ids.nombre_input.text = producto[1] or ""
        self.ids.descripcion_input.text = producto[2] or ""
        self.ids.precio_input.text = str(producto[3] or "")
        self.ids.stock_input.text = str(producto[4] or "")
        self.ids.fecha_input.text = str(producto[5] or "")
        self.ids.codigo_input.text = producto[6] or ""
        self.producto_editando_id = producto_id
        self.ids.boton_agregar.text = "Guardar Cambios"
        print(f"✏️ Editando producto {producto_id}")

    # ------------------------------
    # ELIMINAR
    # ------------------------------
    def eliminar_producto(self, producto_id):
        try:
            consulta = "DELETE FROM Productos WHERE ProductoID = ?"
            ejecutar_consulta(consulta, (producto_id,))
            print(f"🗑️ Producto {producto_id} eliminado correctamente.")
            self.mostrar_productos()
        except Exception as e:
            print(f"❌ Error al eliminar producto: {e}")

    # ------------------------------
    # LIMPIAR
    # ------------------------------
    def limpiar_campos(self):
        for campo in [
            "nombre_input", "descripcion_input", "precio_input",
            "stock_input", "fecha_input", "codigo_input"
        ]:
            self.ids[campo].text = ""

    # ------------------------------
    # VOLVER
    # ------------------------------
    def volver_al_panel(self):
        from mkdir_pantallas.panel_admin import PanelAdminScreen
        app = App.get_running_app()
        root = app.root
        root.clear_widgets()
        root.add_widget(PanelAdminScreen())
