from kivy.uix.screenmanager import Screen
from mkdir_database.conexion import obtener_productos, descontar_stock
from mkdir_servicios.arca_api import emitir_factura_simple


class FacturaScreen(Screen):
    def on_pre_enter(self):
        productos = obtener_productos() or []
        if not productos:
            print("No hay productos disponibles.")
            return
        for p in productos:
            print(f"{p['nombre']} - ${p['precio']} - stock: {p['stock']}")

    def emitir_factura(self, items):
        total = sum(i["cantidad"] * i["precio"] for i in items)
        neto = total / 1.21
        iva = total - neto
        factura = emitir_factura_simple(total, neto, iva)
        print("Factura emitida:", factura)
        for i in items:
            descontar_stock(i["id"], i["cantidad"])

# Alias para compatibilidad con main.py
class FacturasScreen(FacturaScreen):
    pass
