from kivy.uix.boxlayout import BoxLayout
from kivy.uix.popup import Popup
from kivy.metrics import dp
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.lang import Builder

# Cargar el KV
Builder.load_file("mkdir_pantallas/clientes.kv")

try:
    from mkdir_database.conexion import ejecutar_consulta
except:
    from conexion import ejecutar_consulta


class ClientesScreen(BoxLayout):

    # ------------------------------------------------
    # VOLVER AL MENÚ PRINCIPAL
    # ------------------------------------------------
    def volver_menu(self):
        from mkdir_pantallas.menu_principal import MenuPrincipalScreen
        self.clear_widgets()
        self.add_widget(MenuPrincipalScreen())

    # ------------------------------------------------
    # CARGAR CLIENTES (con o sin búsqueda)
    # ------------------------------------------------
    def cargar_clientes(self, busqueda=""):
        cont = self.ids.tabla_clientes
        cont.clear_widgets()

        try:
            if busqueda:
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
            cont.add_widget(Label(text=f"Error al cargar clientes: {e}", color=(1, 0, 0, 1)))
            return

        if not filas:
            cont.add_widget(Label(text="No hay clientes registrados.", color=(0, 0, 0, 1)))
            return

        for cid, nombre, cuit, cond_fiscal in filas:
            fila = BoxLayout(size_hint_y=None, height=dp(40), spacing=dp(10))
            fila.add_widget(Label(text=str(cid), color=(0, 0, 0, 1)))
            fila.add_widget(Label(text=nombre, color=(0, 0, 0, 1)))
            fila.add_widget(Label(text=cuit or "-", color=(0, 0, 0, 1)))
            fila.add_widget(Label(text=cond_fiscal or "-", color=(0, 0, 0, 1)))

            # Botón editar
            fila.add_widget(Button(
                text="Editar",
                size_hint_x=None,
                width=dp(100),
                background_color=(0.2, 0.6, 0.9, 1),
                color=(1, 1, 1, 1),
                on_release=lambda x, _cid=cid: self.editar_cliente(_cid)
            ))

            # Botón eliminar
            fila.add_widget(Button(
                text="Eliminar",
                size_hint_x=None,
                width=dp(100),
                background_color=(0.9, 0.2, 0.2, 1),
                color=(1, 1, 1, 1),
                on_release=lambda x, _cid=cid, _nombre=nombre: self.confirmar_eliminar(_cid, _nombre)
            ))

            cont.add_widget(fila)

    # ------------------------------------------------
    # NUEVO CLIENTE — popup
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
        botones.add_widget(Button(
            text="Guardar",
            on_release=lambda x: self.validar_nuevo(campos, popup)
        ))
        botones.add_widget(Button(text="Cancelar", on_release=lambda x: popup.dismiss()))
        contenido.add_widget(botones)

        popup = Popup(
            title="Nuevo Cliente",
            content=contenido,
            size_hint=(None, None),
            size=(450, 550),
            auto_dismiss=False
        )
        popup.open()

    # VALIDACIÓN para nuevo cliente
    def validar_nuevo(self, campos, popup):
        for key, c in campos.items():
            if c.text.strip() == "":
                self._popup_error("Todos los campos son obligatorios.")
                return

        self.guardar_cliente(campos, popup)

    def _popup_error(self, mensaje):
        Popup(
            title="Error",
            content=Label(text=mensaje, color=(1, 1, 1, 1)),
            size_hint=(None, None),
            size=(350, 150)
        ).open()

    # Guardar cliente en base
    def guardar_cliente(self, campos, popup):
        datos = (
            campos["nombre"].text,
            campos["direccion"].text,
            campos["telefono"].text,
            campos["email"].text,
            campos["cuit"].text,
            campos["condicion"].text,
            campos["ruta"].text,
        )

        try:
            ejecutar_consulta("""
                INSERT INTO Clientes (Nombre, Direccion, Telefono, Email, CUIT, CondicionFiscal, Ruta)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, datos)
        except Exception as e:
            self._popup_error(str(e))

        popup.dismiss()
        self.cargar_clientes()

    # ------------------------------------------------
    # EDITAR CLIENTE
    # ------------------------------------------------
    def editar_cliente(self, cliente_id):
        fila = ejecutar_consulta("""
            SELECT Nombre, Direccion, Telefono, Email, CUIT, CondicionFiscal, Ruta
            FROM Clientes WHERE ClienteID = ?
        """, (cliente_id,))

        if not fila:
            return

        nombre, direccion, telefono, email, cuit, cond_fiscal, ruta = fila[0]

        contenido = BoxLayout(orientation="vertical", padding=dp(15), spacing=dp(10))

        campos = {
            "nombre": TextInput(text=nombre),
            "direccion": TextInput(text=direccion or ""),
            "telefono": TextInput(text=telefono or ""),
            "email": TextInput(text=email or ""),
            "cuit": TextInput(text=cuit or ""),
            "condicion": TextInput(text=cond_fiscal or ""),
            "ruta": TextInput(text=ruta or ""),
        }

        for c in campos.values():
            contenido.add_widget(c)

        botones = BoxLayout(size_hint_y=None, height=dp(50), spacing=dp(10))

        btn_guardar = Button(
            text="Guardar Cambios",
            background_color=(0.2, 0.6, 0.2, 1),
            color=(1, 1, 1, 1),
            on_release=lambda x: self.validar_edicion(cliente_id, campos, popup)
        )

        btn_cancelar = Button(
            text="Cancelar",
            background_color=(0.6, 0.1, 0.1, 1),
            color=(1, 1, 1, 1),
            on_release=lambda x: popup.dismiss()
        )

        botones.add_widget(btn_guardar)
        botones.add_widget(btn_cancelar)
        contenido.add_widget(botones)

        popup = Popup(
            title=f"Editar Cliente #{cliente_id}",
            content=contenido,
            size_hint=(None, None),
            size=(450, 550),
            auto_dismiss=False
        )
        popup.open()

    # Validación antes de guardar cambios
    def validar_edicion(self, cliente_id, campos, popup):
        for c in campos.values():
            if c.text.strip() == "":
                self._popup_error("Completa todos los campos.")
                return

        self.guardar_cambios_cliente(cliente_id, campos, popup)

    # Guardar cambios
    def guardar_cambios_cliente(self, cliente_id, campos, popup):
        datos = (
            campos["nombre"].text,
            campos["direccion"].text,
            campos["telefono"].text,
            campos["email"].text,
            campos["cuit"].text,
            campos["condicion"].text,
            campos["ruta"].text,
            cliente_id
        )

        ejecutar_consulta("""
            UPDATE Clientes
            SET Nombre=?, Direccion=?, Telefono=?, Email=?, CUIT=?, CondicionFiscal=?, Ruta=?
            WHERE ClienteID=?
        """, datos)

        popup.dismiss()
        self.cargar_clientes()

    # ------------------------------------------------
    # ELIMINAR CLIENTE
    # ------------------------------------------------
    def confirmar_eliminar(self, cliente_id, nombre):
        box = BoxLayout(orientation="vertical", padding=dp(15), spacing=dp(10))
        box.add_widget(Label(text=f"¿Eliminar a '{nombre}'?", color=(1, 1, 1, 1)))

        botones = BoxLayout(size_hint_y=None, height=dp(45), spacing=dp(10))

        btn_si = Button(
            text="Sí",
            background_color=(0.9, 0.1, 0.1, 1),
            color=(1, 1, 1, 1),
            on_release=lambda x: self._eliminar_confirmado(cliente_id, popup)
        )
        btn_no = Button(
            text="No",
            background_color=(0.3, 0.3, 0.3, 1),
            color=(1, 1, 1, 1),
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

    def _eliminar_confirmado(self, cliente_id, popup):
        popup.dismiss()
        ejecutar_consulta(
            "DELETE FROM Clientes WHERE ClienteID = ?",
            (cliente_id,)
        )
        self.cargar_clientes()
