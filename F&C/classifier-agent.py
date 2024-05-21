from instantneo.core import InstantNeo
import openai
import os

# This is the OpenAI API key used to authenticate requests.
api_key = os.getenv("OPENAI_API_KEY")
model = "gpt-3.5-turbo"

# Initialize the InstantNeo client.
role_neo = """
## Contexto
Eres un agente clasificador de correos electronicos, tu trabajo es etiquetar los correos
electronicos recibidos, en las siguientes categorias:

## Categorias
Categoria: "SPAN"
Descripción: Correos electrónicos no solicitados o no deseados que generalmente
contienen publicidad, ofertas fraudulentas o contenido irrelevante.

Categoria: "ORDEN DE COMPRA"
Descripción: Correos electrónicos que contienen detalles de órdenes de compra,
incluyendo confirmaciones, actualizaciones de envío, facturas y cualquier comunicación
relacionada con una transacción comercial.

## Ejemplos de respuestas deseadas
Entrada: {
    "Titulo": "Gana un iPhone Gratis",
    "Cuerpo": "¡Haz clic aquí para reclamar tu premio ahora!"
}
Salida: SPAN

Entrada: {
    "Titulo": "Confirmación de Pedido",
    "Cuerpo": "Tu compra ha sido enviada. Aquí están los detalles de tu pedido.",
}
Salida: ORDEN DE COMPRA

## Restricciones
1. Solo responder con las categorias tal como aparecen en la sección de categorias

"""

neo = InstantNeo(api_key,model, role_neo)

# Entrenameinto 1
entrenamiento1 = neo.run("""
 {
    "Titulo": "Tu Pedido ha Sido Procesado: Orden #24680",
    "Cuerpo": "Estimado cliente, \n\nNos complace informarle que su pedido con número de orden #24680 ha sido procesado. A continuación, encontrará un resumen de su compra: \n\n- 5x Libros de Ciencia Ficción \n- 1x Kindle Paperwhite \n\nEl total de su pedido es $150. El envío se realizará a través de DHL y se le proporcionará un número de seguimiento en breve. \n\nGracias por elegirnos para sus compras."
  }
""") # RTA: ORDEN DE COMPRA

entremaniento2 = neo.run("""
  {
    "Titulo": "Actualización de Envío y Factura: Orden #11223",
    "Cuerpo": "Estimado cliente, \n\nNos complace informarle que su pedido con número de orden #11223 ha sido enviado. Puede rastrear su paquete utilizando el número de seguimiento XYZ987654321 en el sitio web de la compañía de envíos. \n\nAdjunto encontrará la factura correspondiente a su compra, con los siguientes detalles: \n\nArtículo: Consola de Videojuegos PlayStation 5 \nCantidad: 1 \nPrecio Unitario: $499 \n\nArtículo: Controlador DualSense \nCantidad: 2 \nPrecio Unitario: $69 \n\nTotal: $637 \n\nSi tiene alguna pregunta o necesita asistencia adicional, no dude en ponerse en contacto con nuestro equipo de servicio al cliente. Gracias por su compra y esperamos que disfrute de sus productos."
  }
""") # RTA: ORDEN DE COMPRA

respuesta_neo = neo.run("""
  {
    "Titulo": "¡Gana un Viaje Todo Pagado a las Bahamas!",
    "Cuerpo": "Estimado usuario, \n\n¡Felicidades! Ha sido seleccionado para ganar un viaje todo pagado a las Bahamas. Solo necesita hacer clic en el siguiente enlace y completar una breve encuesta para reclamar su premio. \n\nNo pierda esta increíble oportunidad de disfrutar de unas vacaciones de ensueño. ¡Haga clic ahora y gane! \n\nSaludos, \n\nEl Equipo de Promociones"
  }
""") # RTA: SPAN
print(respuesta_neo)