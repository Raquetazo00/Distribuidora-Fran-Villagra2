from kivy.uix.boxlayout import BoxLayout
from kivy.app import App

try:
    from mkdir_database.conexion import ejecutar_consulta
except:
    from conexion import ejecutar_consulta


class CrearUsuarioScreen(BoxLayout):

    def validar_admin(self):
        usuario = self.ids.usuario_input.text.strip()
        password = self.ids.password_input.text.strip()
        rol = self.ids.rol_input.text.strip()

        if not usuario or not password or not rol:
            self.ids.mensaje_label.text = "Todos los campos son obligatorios"
            self.ids.mensaje_label.color = (1, 0, 0, 1)
            return

        try:
            ejecutar_consulta("""
                INSERT INTO Usuarios (Usuario, Contrasena, Rol)
                VALUES (?, ?, ?)
            """, (usuario, password, rol))
        except Exception as e:
            self.ids.mensaje_label.text = f"Error: {e}"
            self.ids.mensaje_label.color = (1, 0, 0, 1)
            return

        self.ids.mensaje_label.text = "Usuario creado correctamente"
        self.ids.mensaje_label.color = (0, 0.6, 0, 1)

    def volver_al_login(self):
        # CAMBIO → ahora vuelve al Panel Admin
        from mkdir_pantallas.panel_admin import PanelAdminScreen

        app = App.get_running_app()
        app.root.clear_widgets()
        app.root.add_widget(PanelAdminScreen())
