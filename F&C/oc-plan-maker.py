from instantneo.core import InstantNeo
from dotenv import load_dotenv
import openai
import os
import json


# Esta respuesta se consigue al correr: oc-reader-agent.py
# ! BORRAR
respuesta_anterior = {
    "inicio_contrato": "01-05-2024",
    "fin_contrato": "30-04-2026",
    "divisa": "SOLES",
    "forma_pago": "90 días",
    "total_pagar": "76,322.40",
    "cliente_nombre": "CORPORACIÓN ACEROS AREQUIPA S.A.",
    "cliente_ruc": "20370146994",
    "cliente_direccion": "Av. ARGENTINA 5682 Callao - CALLAO",
    "comentario_adiciónal": "La fecha de finalización podría extenderse por común acuerdo entre las partes."
}

# Cargar las variables de entorno desde el archivo .env
load_dotenv()
IA_API_KEY = os.getenv('OPENAI_API_KEY')

# Define the API key and model for the InstantNeo client.
api_key = IA_API_KEY
model = "gpt-3.5-turbo" # Why? Because it's faster reader and less expensive.

# Initialize the InstantNeo client and set the agent classifier role.
agent_classifier_role = """
  
  ##! Contexto
  Eres un agente creador de detalles de facturación.
  Tu tarea es generar un JSON con la información provista, donde contemple los ciclos
  de facturación. La respuesta debe contener la siguiente información:

  - Periodo: El periodo de facturación comprendido entre la fecha de inicio y fin de contrato.
  - Pagos: Un array de objetos que contienen la siguiente información:
    - Fecha: La fecha del pago
    - Categoria: La categoría del pago, puede ser "Inicio", "Entregable" o "Culminación"
    - Concepto: El concepto del pago
    - Total: El total del pago
  - Suma_pagos: La suma total de todos los pagos.
        

  ##! Ejemplos de respuestas deseadas
  ## Ejemplo 1
  Entrada: {
        "inicio_contrato": "02-08-2020",
        "fin_contrato": "02-12-2020",
        "divisa": "SOLES",
        "forma_pago": "Pago mensual",
        "total_pagar": 76322.40,
        "comentario_adicional": "",
    }
  Salida: {
    "periodo": "Periodo: Del 02/08/2020 al 02/10/2020"
    "pagos": [
        {
            "fecha": "02/08/2020",
            "categoria: "Inicio"
            "concepto": "Pago de inicio de contrato",
            "total": "S/ 25440.80"
        },
        {
            "fecha": "02/09/2020",
            "categoria: "Entregable"
            "concepto": "Entregable 1",
            "total": "S/ 25440.80"
        },
        {
            "fecha": "02/10/2020",
            "categoria: "Culminación"
            "concepto": "Entregable final",
            "total": "S/ 25440.80"
        }
    ],
    "suma_pagos": "S/ 76322.40"
  }


  ## Ejemplo 2
   Entrada: {
        "inicio_contrato": "01-09-2021",
        "fin_contrato": "No especificado",
        "divisa": "SOLES",
        "forma_pago": "No especificado",
        "total_pagar": "No especificado",
        "comentario_adicional": "",
    }
  Salida: {
    "periodo": "Periodo: Del 01-09-2021 al (Sin información)"
    "pagos": [],
    "suma_pagos": "(Sin información)"
  }
  ## ! A TENER EN CUENTA
  - El metodo de pago "contado", se abonara en un solo pago, es decir en "pagos"
    debera haber un solo elemento con categoria "Inicio" y concepto "Pago de inicio
    de contrato"
  - Todos los campos son opcionales, en caso de faltar alguno. Poner "(Sin información)"


  ## ! RESTRICCIONES
  - La primera fecha de pagos debe ser siempre el dia de inicio de contrato
  - La suma de todos los "totales" que aparecen en pagos debe ser SIEMPRE igual al total a pagar.
  - La columna "total" debe ser calculada como suma_pagos / cantidad_pagos
"""
neo = InstantNeo(api_key,model, agent_classifier_role, max_tokens=1200)

json_string = json.dumps(respuesta_anterior, indent=4)
respuesta_neo = neo.run(json_string) #? RTA: "OTROS"

print(respuesta_neo)
