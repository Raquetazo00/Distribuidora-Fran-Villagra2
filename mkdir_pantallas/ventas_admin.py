from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.metrics import dp
from kivy.app import App
from mkdir_pantallas.detalle_venta import DetalleVentaScreen
from datetime import datetime

import sys, os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from mkdir_database.conexion import ejecutar_consulta
except:
    from conexion import ejecutar_consulta


class VentasAdminScreen(Screen):

    def on_enter(self):
        self.ventas_cache = []
        self.cargar_ventas()

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

        self.ventas_cache = filas
        self.mostrar_ventas(filas)

    # ===============================================================
    def mostrar_ventas(self, filas):
        tabla = self.ids.tabla_ventas
        tabla.clear_widgets()

        encabezados = ["ID", "Fecha", "Pago", "Total", "Cliente", "Ver"]
        for titulo in encabezados:
            tabla.add_widget(Label(
                text=titulo,
                bold=True,
                font_size=18,
                color=(0, 0, 0, 1)
            ))

        from kivy.uix.button import Button

        for vid, fecha, metodo, total, cliente in filas:

            try:
                f = datetime.strptime(str(fecha), "%Y-%m-%d %H:%M:%S.%f")
                fecha_fmt = f.strftime("%d/%m/%Y %H:%M")
            except:
                fecha_fmt = str(fecha)

            tabla.add_widget(Label(text=str(vid), color=(0,0,0,1)))
            tabla.add_widget(Label(text=fecha_fmt, color=(0,0,0,1)))
            tabla.add_widget(Label(text=metodo or "N/A", color=(0,0,0,1)))
            tabla.add_widget(Label(text=f"${total:.2f}", color=(0,0,0,1)))
            tabla.add_widget(Label(text=str(cliente), color=(0,0,0,1)))

            tabla.add_widget(
                Button(
                    text="Ver",
                    background_color=(0.07, 0.20, 0.40, 1),
                    color=(1,1,1,1),
                    size_hint_y=None,
                    height=dp(40),
                    on_release=lambda x, _id=vid: self.abrir_detalle(_id)
                )
            )

    # ===============================================================
    def filtrar_busqueda(self, texto):
        texto = (texto or "").lower()

        if texto == "":
            self.mostrar_ventas(self.ventas_cache)
            return

        filtradas = []

        for v in self.ventas_cache:
            if texto in " ".join(map(str, v)).lower():
                filtradas.append(v)

        self.mostrar_ventas(filtradas)

    # ===============================================================
    from mkdir_pantallas.detalle_venta import DetalleVentaScreen

    def abrir_detalle(self, venta_id):

            # Si ya existe, no lo volvemos a agregar
            if not self.manager.has_screen("detalle"):
                detalle = DetalleVentaScreen(name="detalle", venta_id=venta_id)
                self.manager.add_widget(detalle)
            else:
                # si ya existe, actualizamos venta_id
                self.manager.get_screen("detalle").venta_id = venta_id

            self.manager.current = "detalle"


    # ===============================================================
    def volver(self):
        from mkdir_pantallas.panel_admin import PanelAdminScreen

        # Si la pantalla NO existe en el ScreenManager, la creamos
        if not self.manager.has_screen("panel_admin"):
            self.manager.add_widget(PanelAdminScreen(name="panel_admin"))

        # Ahora sí podemos volver sin error
        self.manager.current = "panel_admin"
