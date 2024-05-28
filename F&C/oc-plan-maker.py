from instantneo.core import InstantNeo
from dotenv import load_dotenv
import openai
import os
import json


# Esta respuesta se consigue al correr: oc-reader-agent.py
# ! BORRAR
respuesta_anterior = {
    "inicio_contrato": "02.05.2024",
    "fin_contrato": "10.01.2026",
    "divisa": "DOLARES AMERICANO",
    "forma_pago": "4 Cuotas",
    "total_pagar": 101290.10,
    "comentario_adicional": "El Contrato tendrá una vigencia desde el 01 de mayo de 2024 al 30 de abril del 2026. No obstante, a lo señalado en el numeral anterior, ambas PARTES por común acuerdo podrán prorrogar o ampliar el plazo estipulado en la presente cláusula, con una anticipación no menor a quince (15) días calendario de la fecha de vencimiento del presente Contrato, señalando el nuevo plazo para la ampliación de arrendamiento correspondiente.",
    "campos_completos": True
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

    - Periodo: El periodo se comprende entre la fecha de incio a fecha de fin.
        [NOTA: La fechas deben ser retornadas del formato DD/MM/YYYY]
    
    - Pagos: La fechas de los pagos deben ser calculados teniendo en cuenta a la 
        "forma de pago" proporcionada. Es decir, si dice mensual, es una por cada mes.
        [Agregar siempre la divisa adelante, ejemplo si es "SOLES" usar S/, si es "Dólares" usar USD/]

    - Categoria: Las unicas categorias permitidas son: "Inicio", "Entregable", "Culminación".
        Elegir la que mejor se adapte en cada caso.
    
    - Concepto: El conceptos permitidos son: "Pago de inicio de contrato", "Entregable X", "Entregable final"
        [NOTA: "X" hace referencia al número del entregables, modificar el parametro por un numero]
        

  ##! Ejemplos de respuestas deseadas
  ## Ejemplo 1
  Entrada: {
        "inicio_contrato": "02-08-2020",
        "fin_contrato": "02-12-2020",
        "divisa": "SOLES",
        "forma_pago": "Pago mensual",
        "total_pagar": 76322.40,
        "comentario_adicional": "",
        "campos_completos": true
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
        "divisa": "DOLARES AMERICANO",
        "forma_pago": "Pago contado",
        "total_pagar": 10127.12,
        "comentario_adicional": "",
        "campos_completos": true
    }
  Salida: {
    "periodo": "Periodo: Del 02/08/2020 al (Sin especificar)"
    "pagos": [
        {
            "fecha": "01/09/2021",
            "categoria: "Inicio"
            "concepto": "Pago de inicio de contrato",
            "total": "USD/ 10127.12"
        },
    ],
    "suma_pagos": "USD/ 10127.12"
  }



  ## ! A TENER EN CUENTA
  - El metodo de pago "contado", se abonara en un solo pago, es decir en "pagos"
    debera haber un solo elemento con categoria "Inicio" y concepto "Pago de inicio
    de contrato"


  ## ! RESTRICCIONES
  - La primera fecha de pagos debe ser siempre el dia de inicio de contrato
  - La fecha de culminación y entrega final, debe ser siempre la fecha de fin de contrato, aunque no cumpla con la forma de pago
  - La suma de todos los "totales" que aparecen en pagos debe ser SIEMPRE igual al total a pagar.
"""
neo = InstantNeo(api_key,model, agent_classifier_role, max_tokens=1200)

json_string = json.dumps(respuesta_anterior, indent=4)
respuesta_neo = neo.run(json_string) #? RTA: "OTROS"

print(respuesta_neo)
