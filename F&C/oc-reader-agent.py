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
    ##! Contexto
    Eres un agente encargado de extraer información de un archivo,
    Tu objetivo es realizar un analisis exhaustivo del archivo y extra la siguiente información:

    - Duración de contrato: Incluir fecha de inicio y fin. No inventes ninguna fecha.
        Incluirla en el formato DD-MM-YYYY
    - Forma de pago: Escribir la información que proporciona sobre la forma de pago del contrato.
        Incluir información sobre la divisa a usar, esta puede ser "SOLES" o "DOLARES AMERICANO"
        [SOLO usar "SOLES" o "DOLARES AMERICANO"]
        Buscar si especifica la forma de pago a usar como por ejemplo "Pago mensual"
    - Total a pagar: Buscar en el documento la cantidad que debe pagar el cliente, asegurarse que ese total tenga
        incluido todos los impuestos como (IGV) y descuentos.
    - Comentario adicional: En caso de haber alguna información particular MUY RELEVANTE, como
        ampliaciones. De lo contrario dejar el campo vacio. Debe ser muy corto y conciso

    ##! Formato de respuesta esperado
    La respuesta otorgada debe ser SIEMPRE en este formato
    {
        "inicio_contrato": "DD-MM-YYYY" ó "No especificado",
        "fin_contrato": "DD-MM-YYYY" ó "No especificado",
        "divisa": "SOLES" ó "DOLARES AMERICANO" ó "No especificado",
        "forma_pago": [texto] ó "No especificado",
        "total_pagar": [numero] ó "No especificado",
        "comentario_adiciónal": ""
        "campos_completos": [True] o [False]
    }
    [NOTA: No otorgar NINGUNA otra información adicional]
    [NOTA: La sección de comentario debe contener unicamente información adicional, no repetir]
    [NOTA: El campo "campos_completos" debe ser "Verdadero" si todos los demas campos estan completos,
    es decir no tienen la etiqueta de "No especificado". Por defecto es "Falso"]

    ##! A tener en cuenta
    - Sin algun dato no se encunetra la información, completar con "No especificado"
    - Se te va a proporcionar en algunos casos datos iniciales, tomar en cuenta esos datos para completarlos SIEMPRE.
        Por ejemplo: Si se pasa como dato inicial que la fecha inicial es 01-01-2000, agregar ese dato en la respuesta
    - La respuesta debe estar siempre en formato "JSON" que se encuentra entre llaves "{ }"
        No incluir ningun otro texto adicional, como "Basado en la información proporcionada... "
        y/o pensamientos o congeturas
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
        
        ultima_respuesta_json = None
        if ultima_respuesta:
            print(ultima_respuesta)
            ultima_respuesta_json = json.loads(ultima_respuesta)
            if ultima_respuesta_json['campos_completos']:
                print("\nRESPUESTA:\n" + ultima_respuesta)
                break
        
        respuesta_neo = agente.run(prompt=f"""
            Junto a la respuesta anterior:
            {ultima_respuesta}

            Complete la información faltante con la siguiente imagen de un documento
        """, img=local_image_path)

        respuesta_anterior.append(respuesta_neo)