from kivymd.app import MDApp
from kivy.core.window import Window
from kivy.lang import Builder
from kivy.uix.screenmanager import ScreenManager, NoTransition
import os
import sys

# Tamaño base
Window.size = (1000, 650)

# Agregar rutas
ruta_pantallas = os.path.join(os.path.dirname(os.path.abspath(__file__)), "mkdir_pantallas")
sys.path.append(ruta_pantallas)

# Importar login
from login import LoginScreen


class GestorPantallas(ScreenManager):
    pass


class DistribuidoraApp(MDApp):

    def build(self):

        self.theme_cls.primary_palette = "Blue"
        self.theme_cls.theme_style = "Light"

        # Crear screen manager
        sm = GestorPantallas(transition=NoTransition())

        # Cargar todos los .kv
        kv_files = [
            "login_sc.kv",
            "panel_admin.kv",
            "menu_principal.kv",
            "crear_usuario.kv",
            "agregar_producto.kv",
            "facturacion.kv",
            "ventas_admin.kv",
            "detalle_venta.kv",
            "clientes.kv",
        ]

        for kv_file in kv_files:
            ruta = os.path.join(ruta_pantallas, kv_file)
            if os.path.exists(ruta):
                Builder.load_file(ruta)
                print("Cargado:", ruta)
            else:
                print("No encontrado:", ruta)

        # Agregar pantalla inicial
        sm.add_widget(LoginScreen(name="login"))

        return sm


if __name__ == "__main__":
    DistribuidoraApp().run()
