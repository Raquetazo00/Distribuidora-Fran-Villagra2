from kivy.app import App
from kivy.core.window import Window
from kivy.lang import Builder
from kivy.uix.screenmanager import ScreenManager

import os, sys

from mkdir_pantallas.login import LoginScreen
from mkdir_pantallas.menu_principal import MenuPrincipalScreen
from mkdir_pantallas.panel_admin import PanelAdminScreen
from mkdir_pantallas.crear_usuario import CrearUsuarioScreen
from mkdir_pantallas.agregar_producto import AgregarProductoScreen
from mkdir_pantallas.facturacion import FacturaScreen

BASE_PATH = os.path.dirname(os.path.abspath(__file__))
RUTA_PANTALLAS = os.path.join(BASE_PATH, "mkdir_pantallas")

class WindowManager(ScreenManager):
    pass

class DistribuidoraApp(App):

    def build(self):
        sm = WindowManager()

        kv_files = [
            "styles.kv",
            "login_sc.kv",
            "menu_principal.kv",
            "panel_admin.kv",
            "crear_usuario.kv",
            "agregar_producto.kv",
            "facturacion.kv"
        ]

        for kv in kv_files:
            path = os.path.join(RUTA_PANTALLAS, kv)
            if os.path.exists(path):
                Builder.load_file(path)

        sm.add_widget(LoginScreen(name="login"))
        sm.add_widget(MenuPrincipalScreen(name="menu_principal"))
        sm.add_widget(PanelAdminScreen(name="admin"))
        sm.add_widget(CrearUsuarioScreen(name="crear_usuario"))
        sm.add_widget(AgregarProductoScreen(name="agregar_producto"))
        sm.add_widget(FacturaScreen(name="factura"))

        sm.current = "login"
        return sm

if __name__ == "__main__":
    DistribuidoraApp().run()
