from kivy.app import App
from kivy.core.window import Window
from kivy.lang import Builder
from kivy.uix.screenmanager import ScreenManager
import os, sys

# ================================
# CONFIGURACIÓN DE VENTANA
# ================================
Window.size = (1000, 650)
Window.minimum_width, Window.minimum_height = 800, 500
Window.clearcolor = (0.95, 0.95, 0.97, 1)

# ================================
# RUTAS
# ================================
BASE_PATH = os.path.dirname(os.path.abspath(__file__))
RUTA_PANTALLAS = os.path.join(BASE_PATH, 'mkdir_pantallas')

if RUTA_PANTALLAS not in sys.path:
    sys.path.insert(0, RUTA_PANTALLAS)

# ================================
# IMPORTAR PANTALLAS
# ================================
from login import LoginScreen
from mkdir_pantallas.facturas_sc import FacturaScreen


# ================================
# GESTOR DE PANTALLAS
# ================================
class WindowManager(ScreenManager):
    pass


# ================================
# APLICACIÓN PRINCIPAL
# ================================
class DistribuidoraApp(App):
    def build(self):
        sm = WindowManager()

        # Cargar archivos .kv
        kv_files = [
            'login_sc.kv',
            'crear_usuario.kv',
            'menu_principal.kv',
            'panel_admin.kv',
            'facturas_sc.kv'
        ]
        for kv_file in kv_files:
            kv_path = os.path.join(RUTA_PANTALLAS, kv_file)
            print("Buscando:", kv_path)
            if os.path.exists(kv_path):
                Builder.load_file(kv_path)
                print(f"✅ Archivo .kv cargado: {kv_path}")
            else:
                print(f"⚠️ No se encontró el archivo .kv: {kv_path}")

        # Agregar pantallas
        sm.add_widget(LoginScreen(name="login"))
        sm.add_widget(FacturaScreen(name="factura"))

        # 🟢 Establecer pantalla inicial (login)
        sm.current = "login"

        return sm


if __name__ == "__main__":
    DistribuidoraApp().run()
