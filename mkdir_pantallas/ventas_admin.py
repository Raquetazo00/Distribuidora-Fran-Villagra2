from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.metrics import dp
from kivy.app import App

import sys, os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from mkdir_database.conexion import ejecutar_consulta
except:
    from conexion import ejecutar_consulta

from datetime import datetime


class VentasAdminScreen(BoxLayout):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.ventas_cache = []   # ← Guardamos todas las ventas
        self.cargar_ventas()

    # ===============================================================
    # CARGAR TODAS LAS VENTAS
    # ===============================================================
    def cargar_ventas(self):
        try:
            filas = ejecutar_consulta("""
                SELECT VentaID, Fecha, TipoPago, Total, ClienteID
                FROM Ventas
                ORDER BY VentaID DESC
            """, ())
        except Exception as e:
            print("Error al cargar ventas:", e)
            filas = []

        # Guardamos copia para el buscador
        self.ventas_cache = filas

        self.mostrar_ventas(filas)

    # ===============================================================
    # MOSTRAR TABLA REUTILIZABLE (para buscador)
    # ===============================================================
    def mostrar_ventas(self, filas):
        tabla = self.ids.tabla_ventas
        tabla.clear_widgets()

        # Encabezados actualizados
        encabezados = ["ID", "Fecha", "Estado", "Total", "Cliente", "Ver"]
        for titulo in encabezados:
            tabla.add_widget(Label(
                text=titulo, bold=True, font_size=18,
                color=(0, 0, 0, 1), size_hint_y=None, height=dp(35)
            ))

        # Filas
        for venta_id, fecha, metodo, total, cliente_id in filas:

            # ==== FORMATEAR FECHA ====
            try:
                fecha_obj = datetime.strptime(str(fecha), "%Y-%m-%d %H:%M:%S.%f")
                fecha_str = fecha_obj.strftime("%d/%m/%Y %H:%M")
            except:
                fecha_str = str(fecha)

            # ==== ESTADO / Método ====
            metodo = metodo if metodo and metodo != "Sin especificar" else "N/A"

            tabla.add_widget(Label(text=str(venta_id), color=(0, 0, 0, 1), font_size=16))
            tabla.add_widget(Label(text=fecha_str, color=(0, 0, 0, 1), font_size=16))
            tabla.add_widget(Label(text=metodo, color=(0, 0, 0, 1), font_size=16))
            tabla.add_widget(Label(text=f"${total:.2f}", color=(0, 0, 0, 1), font_size=16))
            tabla.add_widget(Label(text=str(cliente_id), color=(0, 0, 0, 1), font_size=16))

            from kivy.uix.button import Button
            tabla.add_widget(
                Button(
                    text="Ver",
                    size_hint_y=None,
                    height=dp(35),
                    background_color=(0.4, 0.4, 0.4, 1),
                    color=(1, 1, 1, 1),
                    on_release=lambda x, vid=venta_id: self.abrir_detalle(vid)
                )
            )

    # ===============================================================
    # BUSCADOR
    # ===============================================================
    def filtrar_busqueda(self, texto):
        texto = (texto or "").strip().lower()

        if texto == "":
            self.mostrar_ventas(self.ventas_cache)
            return

        filtradas = []
        for v in self.ventas_cache:
            venta_id, fecha, metodo, total, cliente = v

            cadena = f"{venta_id} {fecha} {metodo} {total} {cliente}".lower()

            if texto in cadena:
                filtradas.append(v)

        self.mostrar_ventas(filtradas)

    # ===============================================================
    # ABRIR DETALLE DE FACTURA
    # ===============================================================
    def abrir_detalle(self, venta_id):
        from mkdir_pantallas.detalle_venta import DetalleVentaScreen

        app = App.get_running_app()
        root = app.root
        root.clear_widgets()
        root.add_widget(DetalleVentaScreen(venta_id=venta_id))

    # ===============================================================
    # VOLVER
    # ===============================================================
    def volver(self):
        from mkdir_pantallas.panel_admin import PanelAdminScreen
        app = App.get_running_app()
        root = app.root
        root.clear_widgets()
        root.add_widget(PanelAdminScreen())
