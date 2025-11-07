from afip import Afip
from kivy import key
from datetime import date

from afip import Afip

afip = Afip({
    "CUIT": 20409378472,
    "access_token": "PJR0t4Tl9IuhETgDNxXqdBDm4yPD2rQE69mrZn8aysBfHAEm8Rtsgxnq2annGcbA",
    "production": False  # cambia a True cuando pases a producción
})

def emitir_factura_simple(data):
    print("factura emitida con exito")
    return {"status":"ok"}

def emitir_factura():
    # 👉 Datos del comprobante
    data = {
        "CantReg": 1,
        "PtoVta": 1,
        "CbteTipo": 6,  # 6 = Factura B (podés usar 1 para A)
        "Concepto": 1,  # 1 = Productos, 2 = Servicios, 3 = Ambos
        "DocTipo": 80,  # 80 = CUIT, 96 = DNI, 99 = sin identificar
        "DocNro": 20123456789,  # CUIT del cliente
        "CbteFch": afip.format_date(datetime.date.today()),

        # ⚠️ Campo obligatorio desde RG 5616
        "IvaCondicionReceptor": 4,  # 4 = Consumidor Final (por ejemplo)

        "ImpTotal": 1000.00,
        "ImpNeto": 826.45,
        "ImpIVA": 173.55,
        "MonId": "PES",
        "MonCotiz": 1,
        "Iva": [
            {
                "Id": 5,        # 21%
                "BaseImp": 826.45,
                "Importe": 173.55
            }
        ],
    }

    # 👉 Crear la factura
    factura = afip.ElectronicBilling.create_next_voucher(data)

    print("Factura creada correctamente:", factura)