from kivymd.uix.screen import MDScreen

class PanelAdminScreen(MDScreen):

    def ir_a_crear_usuario(self):
        from mkdir_pantallas.crear_usuario import CrearUsuarioScreen
        self.manager.switch_to(CrearUsuarioScreen(name="crear_usuario"))

    def ir_a_agregar_producto(self):
        from mkdir_pantallas.agregar_producto import AgregarProductoScreen
        self.manager.switch_to(AgregarProductoScreen(name="agregar_producto"))

    def volver_al_login(self):
        from mkdir_pantallas.login import LoginScreen
        self.manager.switch_to(LoginScreen(name="login"))

    def ir_a_ver_ventas(self):
        from mkdir_pantallas.ventas_admin import VentasAdminScreen
        self.manager.switch_to(VentasAdminScreen(name="ventas_admin"))
