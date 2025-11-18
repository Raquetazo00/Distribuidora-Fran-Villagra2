# arca_api.py - versión simulada para desarrollo sin PyAfipWs

from datetime import datetime
import random

def emitir_factura_simple(cliente, productos, usuario_id):
    """
    Simula la emisión de una factura AFIP.
    Devuelve un diccionario con los datos como si se hubiera emitido correctamente.
    
    Args:
        cliente: dict con 'nombre', 'ci', 'telefono', 'email'
        productos: lista de dicts {'producto_id', 'nombre', 'cantidad', 'precio'}
        usuario_id: ID del usuario que genera la factura
    """
    # Simular número de factura
    numero_factura = f"F{random.randint(1000,9999)}-{random.randint(10000000,99999999)}"
    cae = f"{random.randint(10000000000000,99999999999999)}"
    vto_cae = (datetime.now().replace(microsecond=0)).isoformat()

    total = sum(p['cantidad'] * p['precio'] for p in productos)

    factura_simulada = {
        "numero_factura": numero_factura,
        "fecha_factura": datetime.now().isoformat(),
        "cliente_nombre": cliente.get('nombre'),
        "cliente_ci": cliente.get('ci'),
        "cliente_telefono": cliente.get('telefono'),
        "cliente_email": cliente.get('email'),
        "total": total,
        "usuario_id": usuario_id,
        "cae": cae,
        "vto_cae": vto_cae,
        "estado": "completada"
    }

    print("⚡ Factura simulada generada:", factura_simulada)
    return factura_simulada
