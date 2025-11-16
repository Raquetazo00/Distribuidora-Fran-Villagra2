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
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Valor por defecto expuesto para los KV antes de build()
        self.text_color = (0.1, 0.1, 0.1, 1)

    def build(self):
<<<<<<< Updated upstream
        sm = WindowManager()

        # Cargar archivos .kv
        kv_files = [
=======
        base_path = ruta_pantallas
        # Color de tipografía global (RGBA). Cambia estos valores si quieres otro color.
        # Ejemplo: (0,0,0,1) negro, (1,1,1,1) blanco, (0.1,0.1,0.1,1) gris oscuro
        self.text_color = (0.1, 0.1, 0.1, 1)

        # Cargar estilos globales primero
        styles_kv = os.path.join(base_path, 'styles.kv')
        if os.path.exists(styles_kv):
            Builder.load_file(styles_kv)
            print(f"Archivo de estilos cargado: {styles_kv}")
        else:
            print(f"Aviso: no se encontró styles.kv en: {styles_kv}")
        # Cargar todos los .kv
        for kv_file in [
>>>>>>> Stashed changes
            'login_sc.kv',
            'crear_usuario.kv',
            'menu_principal.kv',
            'panel_admin.kv',
<<<<<<< Updated upstream
            'facturas_sc.kv'
        ]
        for kv_file in kv_files:
            kv_path = os.path.join(RUTA_PANTALLAS, kv_file)
            print("Buscando:", kv_path)
=======
            'facturacion.kv'
        ]:
            kv_path = os.path.join(base_path, kv_file)
>>>>>>> Stashed changes
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
