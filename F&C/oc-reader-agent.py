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
haiku = "claude-3-sonnet-20240229" # Why? This model is more efficent to "view" the doc image

# Inicia el adaptador para el API de Anthropic
proveedor = AnthropicAdapter()

# Initialize the InstantNeo client and set the agent classifier role.
role_antropic = """
    Contexto:
    Eres un agente encargado de examinar detalladamente un archivo y extraer la siguiente información:

    Inicio de contrato: Indicar la fecha de inicio del servicio según el documento, debiendo estar en el formato DD-MM-AAAA.
    Fin de contrato: Describir la fecha de vencimiento del contrato, incluyendo cualquier extensión potencial en las observaciones. Deberá estar en el formato DD-MM-AAAA.
    Divisa: Seleccionar únicamente entre "SOLES" y "DÓLARES AMERICANOS".
    Forma de pago: Especifique cómo se cobrará, ya sea cada cierto número de días, de contado, en cuotas, etc. Incluya cualquier explicación relevante en las observaciones.
    Total a pagar: Busque dentro del documento la cantidad que el cliente debe pagar, asegurándose de que dicho total incluya todo tipo de impuestos (incluido el IVG) y descuentos aplicados.
    Nombre del cliente: Identificar quién es el cliente mencionado en el documento o la empresa a la que se emitirá la orden de compra. Nota: evite usar "LILAB SAC" u otras variantes.
    RUC del cliente: Registrar el RUC correspondiente al cliente. Nota: nunca utilice el RUC 20604947805.
    Dirección del cliente: Anotar la dirección del cliente. Nota: evitar usar "Av. Javier Prado Oeste Nro. 757" u otros equivalentes.
    Formato de respuesta esperado:
    Se requiere que la respuesta esté siempre en el siguiente formato:

    {
        "inicio_contrato": "DD-MM-AAAA" o "No especificado",
        "fin_contrato": "DD-MM-AAAA" o "No especificado",
        "divisa": "SOLES" o "DÓLARES AMERICANOS" o "No especificado",
        "forma_pago": ["texto"] o "No especificado",
        "total_pagar": [número] o "No especificado",
        "cliente_nombre": [texto] o "No especificado",
        "cliente_ruc": [texto] o "No especificado",
        "cliente_direccion": [texto] o "No especificado",
        "comentario_adicional": ""
    }
    Instrucciones importantes:

    Si algún dato falta, ingrese "No especificado".
    Utilice los valores iniciales cuando sean provistos, incorporando esa información en su respuesta.
    El resultado siempre debe mantenerse en formato JSON, utilizando solamente las llaves {" ": " "}. Evite agregar texto adicional.
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
            Junto a la respuesta anterior:
            {ultima_respuesta}

            Complete la información faltante con la siguiente imagen de un documento
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