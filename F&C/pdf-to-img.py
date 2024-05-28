from flask import Flask, send_from_directory
import fitz  # PyMuPDF
import os
import sys

app = Flask(__name__)
UPLOAD_FOLDER = 'uploads'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

def convert_pdf_to_images(pdf_path, zoom_x=4, zoom_y=4):
    pdf_document = fitz.open(pdf_path)
    image_paths = []

    # Ruta de la carpeta
    ruta_carpeta = "uploads/"

    # Contar archivos
    cantidad_archivos = len([nombre for nombre in os.listdir(ruta_carpeta) if os.path.isfile(os.path.join(ruta_carpeta, nombre))])

    for page_num in range(len(pdf_document)):
        page = pdf_document.load_page(page_num)
        matrix = fitz.Matrix(zoom_x, zoom_y)
        pix = page.get_pixmap(matrix=matrix)
        img_path = os.path.join(UPLOAD_FOLDER, f"page_{cantidad_archivos + page_num + 1}.png")
        pix.save(img_path)
        image_paths.append(img_path)
    return image_paths

@app.route('/upload/<filename>')
def uploaded_file(filename):
    return send_from_directory(UPLOAD_FOLDER, filename)

def main(pdf_path):
    image_paths = convert_pdf_to_images(pdf_path)
    urls = [f"http://127.0.0.1:5000/upload/{os.path.basename(path)}" for path in image_paths]
    return urls

if __name__ == '__main__':
    from threading import Thread
    import webbrowser

    if len(sys.argv) < 2:
        print("Usage: python pdf_to_images.py <path_to_pdf>")
        sys.exit(1)

    pdf_path = sys.argv[1]

    # Convierte el PDF a imágenes y obtén las URLs
    urls = main(pdf_path)
    print("Image URLs:", urls)

    # Inicia el servidor Flask en un hilo separado
    def run_app():
        app.run(debug=False, port=5000)

    server_thread = Thread(target=run_app)
    server_thread.start()

    # Abre el navegador web con la primera imagen para verificar
    if urls:
        webbrowser.open(urls[0])
