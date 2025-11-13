from kivy.uix.boxlayout import BoxLayout

class PanelAdminScreen(BoxLayout):
    """Pantalla de administración para el rol Administrador"""

    def ir_a_crear_usuario(self):
        """Ir a la pantalla para crear usuarios"""
        from mkdir_pantallas.crear_usuario import CrearUsuarioScreen
        self.clear_widgets()
        self.add_widget(CrearUsuarioScreen())

    def volver_al_login(self):
        """Volver a la pantalla de login"""
        from mkdir_pantallas.login import LoginScreen
<<<<<<< Updated upstream
        self.clear_widgets()
        self.add_widget(LoginScreen())
=======
        app = App.get_running_app()
        root = app.root
        root.clear_widgets()
        root.add_widget(LoginScreen())

    def volver_al_menu(self):
        """Volver al Menú Principal"""
        from mkdir_pantallas.menu_principal import MenuPrincipalScreen
        app = App.get_running_app()
        root = app.root
        root.clear_widgets()
        root.add_widget(MenuPrincipalScreen())
>>>>>>> Stashed changes
