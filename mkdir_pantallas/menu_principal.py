from kivy.uix.boxlayout import BoxLayout

class MenuPrincipalScreen(BoxLayout):
    """Pantalla principal para empleados y otros roles"""

    def volver_al_login(self):
        """Volver a la pantalla de login"""
        from mkdir_pantallas.login import LoginScreen
        self.clear_widgets()
        self.add_widget(LoginScreen())
