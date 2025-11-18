from kivy.uix.boxlayout import BoxLayout
from kivy.properties import StringProperty, NumericProperty
from kivy.metrics import dp

import sys, os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from mkdir_database.conexion import ejecutar_consulta
except:
    from conexion import ejecutar_consulta


class DetalleVentaScreen(BoxLayout):

    # ============================
    # PROPIEDADES NECESARIAS PARA EL KV
    # ============================
    factura_id = StringProperty("")
    fecha = StringProperty("")
    metodo = StringProperty("")
    total = NumericProperty(0)

    cli_nombre = StringProperty("")
    cli_tel = StringProperty("")
    cli_email = StringProperty("")
    cli_cuit = StringProperty("")

    def __init__(self, venta_id="", **kwargs):
        super().__init__(**kwargs)

        self.factura_id = str(venta_id)

        # ============================
        # CARGAR DATOS DE VENTA
        # ============================
        fila = ejecutar_consulta("""
            SELECT Fecha, TipoPago, Total, ClienteID 
            FROM Ventas 
            WHERE VentaID = ?
        """, (venta_id,))

        if fila:
            fecha, metodo, total, cliente_id = fila[0]

            self.fecha = str(fecha)
            self.metodo = metodo or "N/A"
            self.total = float(total)
        else:
            print("Venta no encontrada")
            return

        # ============================
        # CARGAR DATOS DEL CLIENTE
        # ============================
        fila_cliente = ejecutar_consulta("""
            SELECT Nombre, Telefono, Email, CUIT
            FROM Clientes
            WHERE ClienteID = ?
        """, (cliente_id,))

        if fila_cliente:
            self.cli_nombre, self.cli_tel, self.cli_email, self.cli_cuit = fila_cliente[0]

        # ============================
        # CARGAR DETALLE DE PRODUCTOS
        # ============================
        tabla = self.ids.tabla_items
        filas_detalle = ejecutar_consulta("""
            SELECT P.Nombre, VD.Cantidad, VD.PrecioUnitario, (VD.Cantidad * VD.PrecioUnitario)
            FROM VentaDetalle VD
            JOIN Productos P ON P.ProductoID = VD.ProductoID
            WHERE VD.VentaID = ?
        """, (venta_id,))

        for nombre, cant, precio, subtotal in filas_detalle:
            from kivy.uix.label import Label
            tabla.add_widget(Label(text=str(nombre), font_size=16, color=(0,0,0,1)))
            tabla.add_widget(Label(text=str(cant), font_size=16, color=(0,0,0,1)))
            tabla.add_widget(Label(text=f"${precio:.2f}", font_size=16, color=(0,0,0,1)))
            tabla.add_widget(Label(text=f"${subtotal:.2f}", font_size=16, color=(0,0,0,1)))

    def generar_pdf(self):
        print("Generar PDF (luego lo implementamos)")

    def volver(self):
        from kivy.app import App
        from mkdir_pantallas.ventas_admin import VentasAdminScreen
        root = App.get_running_app().root
        root.clear_widgets()
        root.add_widget(VentasAdminScreen())
