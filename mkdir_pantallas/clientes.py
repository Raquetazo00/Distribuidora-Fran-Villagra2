from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.popup import Popup
from kivy.metrics import dp
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.lang import Builder

# Cargar KV correctamente
Builder.load_file("mkdir_pantallas/clientes.kv")

try:
    from mkdir_database.conexion import ejecutar_consulta
except:
    from conexion import ejecutar_consulta


class ClientesScreen(Screen):
    pantalla_factura = None

    def on_enter(self):
        """Se ejecuta cuando se abre este Screen"""
        self.cargar_clientes()

    # ------------------------------------------------
    # VOLVER A FACTURACIÓN
    # ------------------------------------------------
    def volver_menu(self):
        if self.manager:
            if self.pantalla_factura:
                self.manager.switch_to(self.pantalla_factura)
            else:
                self.manager.current = "menu_principal"

    # ------------------------------------------------
    # CARGAR CLIENTES
    # ------------------------------------------------
    def cargar_clientes(self, busqueda=""):
        cont = self.ids.tabla_clientes
        cont.clear_widgets()

        try:
            if busqueda.strip() != "":
                filas = ejecutar_consulta("""
                    SELECT ClienteID, Nombre, CUIT, CondicionFiscal
                    FROM Clientes
                    WHERE Nombre LIKE ? OR CUIT LIKE ?
                """, (f"%{busqueda}%", f"%{busqueda}%"))
            else:
                filas = ejecutar_consulta("""
                    SELECT ClienteID, Nombre, CUIT, CondicionFiscal
                    FROM Clientes
                """, ())
        except Exception as e:
            cont.add_widget(Label(text=f"Error: {e}", color=(1, 0, 0, 1)))
            return

        if not filas:
            cont.add_widget(Label(text="No hay clientes registrados.", color=(0, 0, 0, 1)))
            return

        # Agregar filas
        for cid, nombre, cuit, cond in filas:
            fila = BoxLayout(size_hint_y=None, height=dp(40), spacing=dp(10))

            fila.add_widget(Label(text=str(cid), color=(0, 0, 0, 1)))
            fila.add_widget(Label(text=nombre, color=(0, 0, 0, 1)))
            fila.add_widget(Label(text=cuit or "-", color=(0, 0, 0, 1)))
            fila.add_widget(Label(text=cond or "-", color=(0, 0, 0, 1)))

            btn_edit = Button(
                text="Editar",
                size_hint_x=None, width=dp(100),
                background_color=(0.2, 0.6, 0.9, 1),
                color=(1, 1, 1, 1),
                on_release=lambda x, _id=cid: self.editar_cliente(_id)
            )

            btn_del = Button(
                text="Eliminar",
                size_hint_x=None, width=dp(100),
                background_color=(0.9, 0.2, 0.2, 1),
                color=(1, 1, 1, 1),
                on_release=lambda x, _id=cid, _nom=nombre: self.confirmar_eliminar(_id, _nom)
            )

            fila.add_widget(btn_edit)
            fila.add_widget(btn_del)
            cont.add_widget(fila)

    # ------------------------------------------------
    # POPUP NUEVO CLIENTE
    # ------------------------------------------------
    def abrir_popup_nuevo(self):
        contenido = BoxLayout(orientation="vertical", padding=dp(15), spacing=dp(10))

        campos = {
            "nombre": TextInput(hint_text="Nombre"),
            "direccion": TextInput(hint_text="Dirección"),
            "telefono": TextInput(hint_text="Teléfono"),
            "email": TextInput(hint_text="Email"),
            "cuit": TextInput(hint_text="CUIT"),
            "condicion": TextInput(hint_text="Condición Fiscal"),
            "ruta": TextInput(hint_text="Ruta"),
        }

        for c in campos.values():
            contenido.add_widget(c)

        botones = BoxLayout(size_hint_y=None, height=dp(50), spacing=dp(10))

        btn_guardar = Button(
            text="Guardar",
            background_color=(0.1, 0.5, 0.2, 1),
            color=(1, 1, 1, 1),
            on_release=lambda x: self.validar_nuevo(campos, popup)
        )

        btn_cancelar = Button(
            text="Cancelar",
            background_color=(0.5, 0.1, 0.1, 1),
            color=(1, 1, 1, 1),
            on_release=lambda x: popup.dismiss()
        )

        botones.add_widget(btn_cancelar)
        botones.add_widget(btn_guardar)
        contenido.add_widget(botones)

        popup = Popup(
            title="Nuevo Cliente",
            content=contenido,
            size_hint=(None, None),
            size=(450, 550),
            auto_dismiss=False
        )
        popup.open()

    # Guardar nuevo cliente
    def validar_nuevo(self, campos, popup):
        for c in campos.values():
            if c.text.strip() == "":
                self._popup_error("Completa todos los campos.")
                return

        self._guardar_cliente(campos)
        popup.dismiss()
        self.cargar_clientes()

    def _guardar_cliente(self, campos):
        datos = tuple(c.text for c in campos.values())
        ejecutar_consulta("""
            INSERT INTO Clientes (Nombre, Direccion, Telefono, Email, CUIT, CondicionFiscal, Ruta)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, datos)

    # ------------------------------------------------
    # POPUPS SIMPLES
    # ------------------------------------------------
    def _popup_error(self, msg):
        Popup(
            title="Error",
            content=Label(text=msg, color=(1, 0, 0, 1)),
            size_hint=(None, None),
            size=(350, 200)
        ).open()
