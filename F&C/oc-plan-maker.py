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
    "forma_pago": "90 días o afiliación a factoring",
    "comentario_adicional": "La selección del candidato estará sujeta a la evaluación técnica que realizará el área usuaria al total de candidatos presentados por los proveedores homologados durante el presente proceso.",
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

    - Categoria: Las unicas categorias permitidas son: "Inicio", "Entregable", "Culminación".
        Elegir la que mejor se adapte en cada caso.
    
    - Concepto: El conceptos permitidos son: "Pago de inicio de contrato", "Entregable X", "Entregable final"
        [NOTA: "X" hace referencia al número del entregables, modificar el parametro por un numero]
        

  ##! Ejemplos de respuestas deseadas
  Entrada: {
        "inicio_contrato": "02-08-2020",
        "fin_contrato": "02-12-2020",
        "divisa": "SOLES",
        "forma_pago": "Pago mensual",
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
        },
        {
            "fecha": "02/09/2020",
            "categoria: "Entregable"
            "concepto": "Entregable 1",
        },
        {
            "fecha": "02/10/2020",
            "categoria: "Culminación"
            "concepto": "Entregable final",
        }
    ]
  }


  ## ! RESTRICCIONES
  - La primera fecha de pagos debe ser siempre el dia de inicio de contrato
  - La fecha de culminación y entrega final, debe ser siempre la fecha de fin de contrato, aunque no cumpla con la forma de pago
"""
neo = InstantNeo(api_key,model, agent_classifier_role, max_tokens=1200)

json_string = json.dumps(respuesta_anterior, indent=4)
respuesta_neo = neo.run(json_string) #? RTA: "OTROS"

print(respuesta_neo)
