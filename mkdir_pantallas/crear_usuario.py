from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.popup import Popup
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
import hashlib
import os, sys

# Import DB
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
try:
    from mkdir_database.conexion import ejecutar_consulta
except:
    ejecutar_consulta = None


class CrearUsuarioScreen(Screen):
    """Pantalla para crear nuevos usuarios (solo admin)"""

    # ===========================
    # VALIDACIÓN DE ADMIN
    # ===========================
    def validar_admin(self):
        """Solicita contraseña del admin antes de crear usuario"""
        contenido = BoxLayout(orientation='vertical', spacing=10, padding=10)
        contenido.add_widget(Label(text="Ingrese contraseña de administrador:", font_size=16))

        password_input = TextInput(password=True, multiline=False)
        contenido.add_widget(password_input)

        btn_layout = BoxLayout(spacing=10, size_hint_y=None, height=40)
        btn_confirmar = Button(text="Confirmar",
                               on_release=lambda x: self.verificar_admin(password_input.text))
        btn_cancelar = Button(text="Cancelar",
                              on_release=lambda x: self.popup.dismiss())
        btn_layout.add_widget(btn_confirmar)
        btn_layout.add_widget(btn_cancelar)

        contenido.add_widget(btn_layout)

        self.popup = Popup(title="Validación de Administrador",
                           content=contenido,
                           size_hint=(0.6, 0.4))
        self.popup.open()

    def verificar_admin(self, contrasena_admin):
        """Verifica contraseña del admin"""
        if ejecutar_consulta is None:
            self.ids.mensaje_label.text = "⚠ No hay conexión a la base"
            self.popup.dismiss()
            return

        password_hash = hashlib.sha256(contrasena_admin.encode()).hexdigest()

        consulta = """
            SELECT UsuarioID FROM Usuarios 
            INNER JOIN Roles ON Usuarios.RolID = Roles.RolID
            WHERE NombreUsuario = 'admin'
              AND ClaveHash = ?
              AND Roles.Nombre = 'Administrador'
        """

        resultado = ejecutar_consulta(consulta, (password_hash,))
        self.popup.dismiss()

        if resultado:
            self.crear_usuario()
        else:
            self.ids.mensaje_label.text = "Contraseña de administrador incorrecta ❌"

    # ===========================
    # CREAR USUARIO
    # ===========================
    def crear_usuario(self):
        usuario = self.ids.usuario_input.text.strip()
        password = self.ids.password_input.text.strip()
        rol = self.ids.rol_input.text.strip()

        if not usuario or not password or not rol:
            self.ids.mensaje_label.text = "Complete todos los campos"
            return

        # Crear hash
        password_hash = hashlib.sha256(password.encode()).hexdigest()

        # Buscar rol
        consulta_rol = "SELECT RolID FROM Roles WHERE Nombre = ?"
        rol_res = ejecutar_consulta(consulta_rol, (rol,))

        if not rol_res:
            self.ids.mensaje_label.text = f"El rol '{rol}' no existe"
            return

        rol_id = rol_res[0][0]

        # Insertar usuario
        consulta_insert = """
            INSERT INTO Usuarios (NombreUsuario, ClaveHash, RolID, Estado)
            VALUES (?, ?, ?, 1)
        """

        filas = ejecutar_consulta(consulta_insert, (usuario, password_hash, rol_id))

        if filas:
            self.ids.mensaje_label.color = (0, 1, 0, 1)
            self.ids.mensaje_label.text = "✅ Usuario creado correctamente"

            self.ids.usuario_input.text = ""
            self.ids.password_input.text = ""
            self.ids.rol_input.text = ""
        else:
            self.ids.mensaje_label.color = (1, 0, 0, 1)
            self.ids.mensaje_label.text = "❌ Error al crear usuario"

    # ===========================
    # VOLVER (NAVEGACIÓN CORRECTA)
    # ===========================
    def volver_al_login(self):
        self.manager.current = "login"

    def volver_al_menu(self):
        self.manager.current = "menu_principal"
