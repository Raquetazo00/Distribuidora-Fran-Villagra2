from kivy.uix.screenmanager import Screen
from kivy.properties import ObjectProperty
import hashlib
from mkdir_database.conexion import ejecutar_consulta


class LoginScreen(Screen):
    """Pantalla de inicio de sesión"""

    def validar_login(self, usuario, password):
        if not usuario or not password:
            self.mostrar_mensaje("Por favor, complete todos los campos", error=True)
            return False

        # Hash de la contraseña
        password_hash = hashlib.sha256(password.encode()).hexdigest()

        # Consulta SQL compatible con SQLite
        consulta = """
            SELECT u.UsuarioID, u.NombreUsuario, u.RolID, r.Nombre as RolNombre, u.EmpleadoID
            FROM Usuarios u
            JOIN Roles r ON u.RolID = r.RolID
            WHERE u.NombreUsuario = ? AND u.ClaveHash = ? AND u.Estado = 1
        """

        resultado = ejecutar_consulta(consulta, (usuario, password_hash))

        if resultado and len(resultado) > 0:
            usuario_data = {
                'UsuarioID': resultado[0][0],
                'NombreUsuario': resultado[0][1],
                'RolID': resultado[0][2],
                'RolNombre': resultado[0][3],
                'EmpleadoID': resultado[0][4]
            }

            print(f"✅ Usuario autenticado: {usuario_data}")
            self.mostrar_mensaje(f"Bienvenido {usuario_data['NombreUsuario']}", error=False)

            # Cambiar de pantalla según el rol
            rol = usuario_data['RolNombre'].lower()

            if rol == "administrador":
                self.manager.current = "admin"         # PANEL ADMIN
            elif rol == "empleado":
                self.manager.current = "menu_principal"
            elif rol == "vendedor":
                self.manager.current = "menu_principal"
            else:
                self.manager.current = "menu_principal"

            return True

        else:
            self.mostrar_mensaje("Usuario o contraseña incorrectos", error=True)
            return False

    def mostrar_mensaje(self, mensaje, error=True):
        """Muestra mensajes en etiqueta del KV"""
        if hasattr(self, 'ids') and 'mensaje_label' in self.ids:
            mensaje_label = self.ids.mensaje_label
            mensaje_label.text = mensaje
            mensaje_label.color = (1, 0, 0, 1) if error else (0, 1, 0, 1)
            print(f"Mensaje mostrado: {mensaje}")
