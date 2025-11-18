from kivy.app import App
from kivy.core.window import Window 
from kivy.lang import Builder
import os
import sys

# Configurar ventana (responsive base)
Window.size = (1000, 650)
Window.minimum_width, Window.minimum_height = 800, 500
Window.clearcolor = (0.95, 0.95, 0.97, 1)

# Agregar ruta de pantallas
ruta_pantallas = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'mkdir_pantallas')
if ruta_pantallas not in sys.path:
    sys.path.insert(0, ruta_pantallas)

from login import LoginScreen

class DistribuidoraApp(App):
    def build(self):
        base_path = ruta_pantallas
        # Cargar todos los .kv
        for kv_file in [
            'login_sc.kv',
            'crear_usuario.kv',
            'menu_principal.kv',
            'panel_admin.kv',
            'facturacion.kv'
        ]:
            kv_path = os.path.join(base_path, kv_file)
            if os.path.exists(kv_path):
                Builder.load_file(kv_path)
                print(f"Archivo .kv cargado: {kv_path}")
            else:
                print(f"Error: No se encontró el archivo .kv en: {kv_path}")
        return LoginScreen()

if __name__ == "__main__":
    DistribuidoraApp().run()
