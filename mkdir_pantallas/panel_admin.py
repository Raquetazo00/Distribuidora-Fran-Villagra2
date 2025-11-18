from kivy.uix.screenmanager import Screen

class PanelAdminScreen(Screen):
    """
    Pantalla del Panel Administrador
    Controlada completamente por ScreenManager
    """

    # ============================
    # NAVEGACIÓN ENTRE PANTALLAS
    # ============================

    def ir_a_crear_usuario(self):
        """Ir a la pantalla de creación de usuarios"""
        self.manager.current = "crear_usuario"

    def ir_a_agregar_producto(self):
        """Ir a la pantalla de agregar/editar productos"""
        self.manager.current = "agregar_producto"

    def volver_al_login(self):
        """Volver a Login"""
        self.manager.current = "login"

    def volver_al_menu(self):
        """Volver al menú principal"""
        self.manager.current = "menu_principal"
