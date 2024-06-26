from instantneo.core import InstantNeo
from instantneo.adapters.anthropic_adapter import AnthropicAdapter
from dotenv import load_dotenv
import openai
import requests
from PIL import Image
from io import BytesIO
import os
from flask import Flask, send_from_directory
import fitz
import json


# Cargar las variables de entorno desde el archivo .env
load_dotenv()
IA_CLAUDE_API_KEY = os.getenv('CLAUDE_API_KEY')

# Define the API key and model for the InstantNeo client.
claude_api_key= IA_CLAUDE_API_KEY
haiku = "claude-3-haiku-20240307" # Why? This model is more efficent to "view" the doc image

# Inicia el adaptador para el API de Anthropic
proveedor = AnthropicAdapter()

# Initialize the InstantNeo client and set the agent classifier role.
role_antropic = """
    ##! CONTEXTO
    Eres un agente de IA, encargado de leer ordenes de compra, tu trabajo es realizar un resumen
    del mismo. Incluir toda la inforamción relevante.
    El resumen debe ser claro y conciso, y se debe complementar a la respuesta anterior.

    La información que nunca debes quitar en caso de aparecer es:
    - Fechas
    - Montos a pagar (indicar si es con IGV o sin IGV)
    - Items a facturar
    - Nombre y ruc de las empresas
"""


# Para crear la instancia necesitas llamar al adaptador en los parámetros
agente = InstantNeo(claude_api_key, haiku, role_antropic, provider=proveedor, max_tokens=1200, temperature=0.2)

# Define la función para descargar la imagen
def download_image(url):
    response = requests.get(url)
    if response.status_code == 200:
        return Image.open(BytesIO(response.content))
    else:
        raise FileNotFoundError(f"Unable to download image from {url}")

# Define la función para guardar la imagen localmente
def save_image_to_file(image, file_path):
    image.save(file_path, format="PNG")

# Define la variable para almacenar la respuesta anterior
respuesta_anterior = []

#! Ejecuta el agente
if __name__ == "__main__":
    
    # Ruta de la carpeta
    ruta_carpeta = "uploads/"

    # Contar archivos
    cantidad_archivos = len([nombre for nombre in os.listdir(ruta_carpeta) if os.path.isfile(os.path.join(ruta_carpeta, nombre))])

    print(f"La cantidad de archivos en la carpeta es: {cantidad_archivos}")

    limit_pages = cantidad_archivos # Número de páginas a procesar
    
    # Recorre las páginas del documento
    for page_num in range(1, limit_pages+1):
        print(f"Procesando página {page_num}...")
        image_url = f"http://127.0.0.1:5000/upload/page_{page_num}.png"
        local_image_path = "temp_image.png"

        # Descarga la imagen
        img = download_image(image_url)

        # Guarda la imagen localmente
        save_image_to_file(img, local_image_path)

        # Ejecuta el agente con la imagen descargada localmente
        ultima_respuesta = respuesta_anterior[-1] if respuesta_anterior else None
        print(ultima_respuesta)
        
        # ultima_respuesta_json = None
        # if ultima_respuesta:
        #     ultima_respuesta_json = json.loads(ultima_respuesta)
        #     if ultima_respuesta_json['campos_completos']:
        #         print("\nRESPUESTA:\n" + ultima_respuesta)
        #         break
        
        respuesta_neo = agente.run(prompt=f"""
            La respuesta anterior es:
            {ultima_respuesta}

            El documento es:
        """, img=local_image_path)

        respuesta_anterior.append(respuesta_neo)

    print("Respuesta: \n", respuesta_anterior[-1])

    #     - Duración de contrato: Incluir fecha de inicio y fin. No inventes ninguna fecha.
    #     Incluirla en el formato DD-MM-YYYY
    # - Forma de pago: Escribir la información que proporciona sobre la forma de pago del contrato.
    #     Incluir información sobre la divisa a usar, esta puede ser "SOLES" o "DOLARES AMERICANO"
    #     Buscar si especifica la forma de pago a usar como por ejemplo "Pago mensual"
    # - Total a pagar: Buscar en el documento la cantidad que debe pagar el cliente, asegurarse que ese total tenga
    #     incluido todos los impuestos como (IGV) y descuentos.
    # - Comentario adicional: En caso de haber alguna información particular MUY RELEVANTE, como
    #     ampliaciones. De lo contrario dejar el campo vacio. Debe ser muy corto y conciso