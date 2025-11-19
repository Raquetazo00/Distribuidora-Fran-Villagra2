from kivymd.uix.screen import MDScreen
from kivy.metrics import dp
import hashlib

try:
    from mkdir_database.conexion import ejecutar_consulta
except:
    from conexion import ejecutar_consulta


class CrearUsuarioScreen(MDScreen):

    def abrir_selector_roles(self):
        """Abre la lista desplegable de roles."""
        menu_items = [
            {"text": "Administrador", "viewclass": "OneLineListItem",
             "on_release": lambda x="Administrador": self.seleccionar_rol(x)},
            {"text": "Empleado", "viewclass": "OneLineListItem",
             "on_release": lambda x="Empleado": self.seleccionar_rol(x)},
            {"text": "Preventista", "viewclass": "OneLineListItem",
             "on_release": lambda x="Preventista": self.seleccionar_rol(x)},
        ]

        from kivymd.uix.menu import MDDropdownMenu

        self.menu = MDDropdownMenu(
            caller=self.ids.rol_selector,
            items=menu_items,
            width_mult=3,
        )
        self.menu.open()

    def seleccionar_rol(self, rol):
        """Coloca el rol seleccionado en el campo visual."""
        self.ids.rol_selector.text = rol
        self.menu.dismiss()

    def validar_admin(self):
        usuario = self.ids.usuario_input.text.strip()
        password = self.ids.password_input.text.strip()
        rol_texto = self.ids.rol_selector.text.strip().lower()

        if not usuario or not password or rol_texto == "Seleccione un rol":
            self.mostrar_mensaje("Todos los campos son obligatorios", error=True)
            return

        # Mapeo rol → ID
        roles_map = {
            "administrador": 1,
            "admin": 1,
            "empleado": 2,
            "preventista": 3,
        }

        if rol_texto not in roles_map:
            self.mostrar_mensaje("Seleccione un rol válido", error=True)
            return

        rol_id = roles_map[rol_texto]

        password_hash = hashlib.sha256(password.encode()).hexdigest()

        try:
            ejecutar_consulta("""
                INSERT INTO Usuarios (NombreUsuario, ClaveHash, RolID)
                VALUES (?, ?, ?)
            """, (usuario, password_hash, rol_id))
        except Exception as e:
            self.mostrar_mensaje(f"Error al ejecutar consulta: {e}", error=True)
            return

        self.mostrar_mensaje("Usuario creado correctamente", error=False)
        self.ids.usuario_input.text = ""
        self.ids.password_input.text = ""
        self.ids.rol_selector.text = "Seleccione un rol"

    def mostrar_mensaje(self, msg, error=True):
        self.ids.mensaje_label.text = msg
        self.ids.mensaje_label.theme_text_color = "Custom"
        self.ids.mensaje_label.text_color = (1, 0, 0, 1) if error else (0, 0.7, 0, 1)

    def volver_al_panel(self):
        from mkdir_pantallas.panel_admin import PanelAdminScreen
        self.manager.switch_to(PanelAdminScreen())
