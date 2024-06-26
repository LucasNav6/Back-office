from instantneo.core import InstantNeo
from dotenv import load_dotenv
import openai
import os
from datetime import datetime
import requests
import json


respuesta_anterior = {
    "fecha": "01-10-2024",
    "categoria": "Inicio",
    "concepto": "Pago de inicio de contrato",
    "total": 25440.80,  # Changed to numeric type for calculations
    "cliente_nombre": "CORPORACIÓN ACEROS AREQUIPA S.A.",
    "cliente_ruc": "20370146994",
    "cliente_direccion": "Av. ARGENTINA 5682 Callao - CALLAO",
    "moneda": "SOLES"
}

def generador_factura(respuesta_anterior):
    # Obtengo la información
    fecha = respuesta_anterior["fecha"]
    categoria = respuesta_anterior["categoria"]
    concepto = respuesta_anterior["concepto"]
    total = respuesta_anterior["total"]
    cliente_nombre = respuesta_anterior["cliente_nombre"]
    cliente_ruc = respuesta_anterior["cliente_ruc"]
    cliente_direccion = respuesta_anterior["cliente_direccion"]
    moneda = respuesta_anterior["moneda"]

    # Obtener el día de hoy
    fecha_hoy = datetime.now().strftime("%d-%m-%Y")

    moneda_cod = 1 if moneda == "SOLES" else 2

    igv = 18

    # Generar el JSON
    total_gravada = total / (1 + igv / 100)
    total_igv = total - total_gravada

    json_nubefact = {
        "operacion": "generar_comprobante",
        "tipo_de_comprobante": 1,
        "serie": "FFF1",
        "numero": "3", # Iterativo
        "sunat_transaction": 1,
        "cliente_tipo_de_documento": 6,
        "cliente_numero_de_documento": cliente_ruc,
        "cliente_denominacion": cliente_nombre,
        "cliente_direccion": cliente_direccion,
        "cliente_email": "",
        "cliente_email_1": "",
        "cliente_email_2": "",
        "fecha_de_emision": f"{fecha_hoy}",
        "fecha_de_vencimiento": f"{fecha}",
        "moneda": moneda_cod,
        "tipo_de_cambio": "",
        "porcentaje_de_igv": f"{igv}.00",
        "descuento_global": "",
        "total_descuento": "",
        "total_anticipo": "",
        "total_gravada": f"{total_gravada:.2f}",
        "total_inafecta": "",
        "total_exonerada": "",
        "total_igv": f"{total_igv:.2f}",
        "total_gratuita": "",
        "total_otros_cargos": "",
        "total": f"{total:.2f}",
        "percepcion_tipo": "",
        "percepcion_base_imponible": "",
        "total_percepcion": "",
        "total_incluido_percepcion": "",
        "detraccion": "false",
        "observaciones": "",
        "documento_que_se_modifica_tipo": "",
        "documento_que_se_modifica_serie": "",
        "documento_que_se_modifica_numero": "",
        "tipo_de_nota_de_credito": "",
        "tipo_de_nota_de_debito": "",
        "enviar_automaticamente_a_la_sunat": "true",
        "enviar_automaticamente_al_cliente": "false",
        "codigo_unico": "",
        "condiciones_de_pago": "",
        "medio_de_pago": "",
        "placa_vehiculo": "",
        "orden_compra_servicio": "",
        "tabla_personalizada_codigo": "",
        "formato_de_pdf": "",
        "items": [
            {
                "unidad_de_medida": "ZZ",
                "codigo": "001",
                "descripcion": concepto,
                "cantidad": "1",
                "valor_unitario": f"{total_gravada:.2f}",
                "precio_unitario": f"{total:.2f}",
                "descuento": "",
                "subtotal": f"{total_gravada:.2f}",
                "tipo_de_igv": "1",
                "igv": f"{total_igv:.2f}",
                "total": f"{total:.2f}",
                "anticipo_regularizacion": "false",
                "anticipo_documento_serie": "",
                "anticipo_documento_numero": "",
                "codigo_producto_sunat": "10000000"
            },
        ]
    }
    return json_nubefact

res_gen_nubefact = generador_factura(respuesta_anterior)
print(res_gen_nubefact)

# URL del endpoint
url = "https://api.nubefact.com/api/v1/8afb6079-b90c-4efd-b54b-ee9b1dac50b4"

# Headers (opcional)
headers = {
    "Content-Type": "application/json",
    "Authorization": "f4bcd7d1c0634cb9b5c5e112856762ebe1dd11b3273a47c9a3e6ff404cd16ac7" # TODO: .ENV
}

# Realizar la solicitud POST
response = requests.post(url, data=json.dumps(res_gen_nubefact), headers=headers)

# Verificar la respuesta
if response.status_code == 200:
    print("Solicitud exitosa")
    print("Respuesta del servidor:", response.json())
else:
    print("Error en la solicitud:", response.status_code)
    print("Mensaje:", response.text)