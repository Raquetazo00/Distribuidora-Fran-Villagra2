from kivymd.uix.screen import MDScreen
from kivy.metrics import dp
import hashlib
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from mkdir_database.conexion import ejecutar_consulta


class LoginScreen(MDScreen):

    def validar_login(self):
        usuario = self.ids.usuario_input.text.strip()
        password = self.ids.password_input.text.strip()

        if not usuario or not password:
            self.mostrar_mensaje("Complete todos los campos", error=True)
            return

        password_hash = hashlib.sha256(password.encode()).hexdigest()

        consulta = """
            SELECT u.UsuarioID, u.NombreUsuario, u.RolID, r.Nombre as RolNombre, u.EmpleadoID
            FROM Usuarios u
            INNER JOIN Roles r ON u.RolID = r.RolID
            WHERE u.NombreUsuario = ? AND u.ClaveHash = ? AND u.Estado = 1
        """

        resultado = ejecutar_consulta(consulta, (usuario, password_hash))

        if resultado:
            usuario_data = {
                'UsuarioID': resultado[0][0],
                'NombreUsuario': resultado[0][1],
                'RolID': resultado[0][2],
                'RolNombre': resultado[0][3],
                'EmpleadoID': resultado[0][4]
            }

            rol = usuario_data["RolNombre"].lower()

            if rol == "administrador":
                destino = "panel_admin"
                from mkdir_pantallas.panel_admin import PanelAdminScreen
                if destino not in self.manager.screen_names:
                    self.manager.add_widget(PanelAdminScreen(name="panel_admin"))
            else:
                destino = "menu_principal"
                from mkdir_pantallas.menu_principal import MenuPrincipalScreen
                if destino not in self.manager.screen_names:
                    self.manager.add_widget(MenuPrincipalScreen(name="menu_principal"))

            self.manager.current = destino
            self.mostrar_mensaje(f"Bienvenido {usuario_data['NombreUsuario']}", error=False)
        else:
            self.mostrar_mensaje("Usuario o contraseña incorrectos", error=True)


    def mostrar_mensaje(self, mensaje, error=True):
        color = (1, 0, 0, 1) if error else (0, 1, 0, 1)
        self.ids.mensaje_label.text = mensaje
        self.ids.mensaje_label.theme_text_color = "Custom"
        self.ids.mensaje_label.text_color = color
