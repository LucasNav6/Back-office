from instantneo.core import InstantNeo
from dotenv import load_dotenv
import openai
import os

# Cargar las variables de entorno desde el archivo .env
load_dotenv()
IA_API_KEY = os.getenv('OPENAI_API_KEY')

# Define the API key and model for the InstantNeo client.
api_key = IA_API_KEY
model = "gpt-3.5-turbo" # Why? Because it's faster reader and less expensive.

# Initialize the InstantNeo client and set the agent classifier role.
agent_classifier_role = """
  
  ##! Contexto
  Eres un agente clasificador de correos electrónicos.
  Tu tarea es etiquetar los correos electrónicos recibidos
  en una de las siguientes categorías:


  ##! Categorias
  Categoria: "ORDEN DE COMPRA"
  Descripción: Correos electrónicos que contienen detalles relacionados con
  transacciones comerciales. Esto incluye confirmaciones de pedidos,
  actualizaciones sobre el estado de envíos, facturas, contratos de servicios,
  acuerdos de términos y condiciones, y cualquier otra comunicación relacionada con
  la ejecución de órdenes de compra. Estos correos suelen implicar intercambio de documentos
  formales y detalles específicos sobre productos o servicios adquiridos, plazos de entrega,
  y condiciones de pago.

  Categoria: "CONFIRMACIÓN ORDEN DE COMPRA"
  Descripción: Correos electrónicos que contienen la aceptación o negación del detalle de orden de compra,
  enviado anteriormente

  Categoria: "SOLICITUD CAMBIO ORDEN DE COMPRA"
  Descripción: Correos electrónicos que contienen la aceptación o negación del detalle de orden de compra,
  enviado anteriormente

  Categoría: "OTROS"
  Descripción: Correos electrónicos que no encajan en ninguna de las categorías anteriores.
  Esta categoría incluye cualquier tipo de comunicación que no sea claramente identificable.


  ##! Ejemplos de respuestas deseadas
  Entrada: {
      "Titulo": "Gana un iPhone Gratis",
      "Cuerpo": "¡Haz clic aquí para reclamar tu premio ahora!"
  }
  Salida: OTROS

  Entrada: {
      "Titulo": "Confirmación de Pedido",
      "Cuerpo": "Tu compra ha sido enviada. Aquí están los detalles de tu pedido.",
  }
  Salida: ORDEN DE COMPRA

  Entrada: {
      "Titulo": "Confirmación de orden Nro FF01-4111",
      "Cuerpo": "Estimados, Recibimos la orden de compra.",
  }
  Salida: CONFIRMACIÓN ORDEN DE COMPRA

  Entrada: {
      "Titulo": "Orden Nro FF01-4111",
      "Cuerpo": "Estimados, Tras una revisión exhaustiva, encontramos los siguientes detalles a modificar. Adjunto las correcciones",
  }
  Salida: SOLICITUD CAMBIO ORDEN DE COMPRA


  ##! Restricciones
  1. Solo responder con las categorias tal como aparecen en la sección de categorias
"""
neo = InstantNeo(api_key,model, agent_classifier_role)

respuesta_neo = neo.run("""
  {
    "Titulo": "Inscríbete en la verificación en 2 pasos ahora para no perder el acceso al dominio",
    "Cuerpo": "Inscríbete en la verificación en 2 pasos para no perder el acceso al dominio facturacion-pruebas@lilab.pe Tu dominio de Google Workspace lilab.pe comenzará a aplicar la verificación en 2 pasos el 23 may 2024. Este proceso mejora la seguridad de tu cuenta, dado que, además de ingresar el nombre de usuario y la contraseña, deberás realizar un segundo paso para acceder. Sigue estas instrucciones simples para inscribirte en la verificación en 2 pasos; de lo contrario, no podrás acceder a tu cuenta después del 23 may 2024.",
}
""") #? RTA: "OTROS"

print(respuesta_neo)
