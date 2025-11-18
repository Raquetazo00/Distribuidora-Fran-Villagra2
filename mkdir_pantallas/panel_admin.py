from kivy.app import App
from kivy.uix.boxlayout import BoxLayout

class PanelAdminScreen(BoxLayout):
    """Pantalla de administración para el rol Administrador"""

    def ir_a_crear_usuario(self):
        """Ir a la pantalla para crear usuarios"""
        from mkdir_pantallas.crear_usuario import CrearUsuarioScreen
        app = App.get_running_app()
        root = app.root
        root.clear_widgets()
        root.add_widget(CrearUsuarioScreen())

    def ir_a_agregar_producto(self):
        """Ir a la pantalla de gestión de productos"""
        from mkdir_pantallas.agregar_producto import AgregarProductoScreen
        app = App.get_running_app()
        root = app.root
        root.clear_widgets()
        root.add_widget(AgregarProductoScreen())

    def volver_al_login(self):
        """Volver a la pantalla de login"""
        from mkdir_pantallas.login import LoginScreen
        app = App.get_running_app()
        root = app.root
        root.clear_widgets()
        root.add_widget(LoginScreen())

    # ======================================================
    # NUEVA FUNCIÓN → VER VENTAS / FACTURAS
    # ======================================================
    def ir_a_ver_ventas(self):
        """Ir a la pantalla donde se listan las ventas/facturas"""
        from mkdir_pantallas.ventas_admin import VentasAdminScreen
        app = App.get_running_app()
        root = app.root
        root.clear_widgets()
        root.add_widget(VentasAdminScreen())
