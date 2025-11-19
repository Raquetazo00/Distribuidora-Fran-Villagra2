from kivy.uix.screenmanager import Screen
from kivy.properties import StringProperty, NumericProperty
from kivy.metrics import dp

import sys, os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from mkdir_database.conexion import ejecutar_consulta
except:
    from conexion import ejecutar_consulta


class DetalleVentaScreen(Screen):

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

        self.venta_id = venta_id
        self.factura_id = str(venta_id)

        # Cargar venta
        fila = ejecutar_consulta("""
            SELECT Fecha, TipoPago, Total, ClienteID 
            FROM Ventas 
            WHERE VentaID = ?
        """, (venta_id,))

        if not fila:
            print("Venta no encontrada")
            return

        fecha, metodo, total, cliente_id = fila[0]

        from datetime import datetime

        try:
            f = datetime.strptime(str(fecha), "%Y-%m-%d %H:%M:%S.%f")
            self.fecha = f.strftime("%d/%m/%Y")
        except:
            self.fecha = str(fecha).split(" ")[0]

        self.metodo = metodo or "N/A"
        self.total = float(total)


        # Cargar cliente
        fila_cliente = ejecutar_consulta("""
            SELECT Nombre, Telefono, Email, CUIT
            FROM Clientes
            WHERE ClienteID = ?
        """, (cliente_id,))

        if fila_cliente:
            self.cli_nombre, self.cli_tel, self.cli_email, self.cli_cuit = fila_cliente[0]

        # Cargar productos
        tabla = self.ids.tabla_items

        productos = ejecutar_consulta("""
            SELECT P.Nombre, VD.Cantidad, VD.PrecioUnitario,
                   (VD.Cantidad * VD.PrecioUnitario) AS Subtotal
            FROM VentaDetalle VD
            JOIN Productos P ON P.ProductoID = VD.ProductoID
            WHERE VD.VentaID = ?
        """, (venta_id,))

        from kivy.uix.label import Label

        for nombre, cant, precio, subtotal in productos:

            tabla.add_widget(Label(text=str(nombre), font_size=16, color=(0,0,0,1)))
            tabla.add_widget(Label(text=str(cant), font_size=16, color=(0,0,0,1)))
            tabla.add_widget(Label(text=f"${precio:.2f}", font_size=16, color=(0,0,0,1)))
            tabla.add_widget(Label(text=f"${subtotal:.2f}", font_size=16, color=(0,0,0,1)))

    # BOTÓN PDF
    def generar_pdf(self):
        print("PDF pronto")

    # BOTÓN VOLVER
    def volver(self):
        self.manager.current = "ventas_admin"
