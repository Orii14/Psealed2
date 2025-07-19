import os
from datetime import datetime
from PIL import Image
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch
from reportlab.lib.pagesizes import A4
from reportlab.lib.utils import ImageReader
import fitz  # PyMuPDF
from io import BytesIO
import streamlit as st

st.title("📄 Firmar y Sellar PDF")

pdf_path = st.file_uploader("Selecciona un archivo PDF", type=["pdf"])

def convertir_paginas_a_imagenes(pdf_path):
    doc = fitz.open(pdf_path)
    imagenes = []

    for page in doc:
        pix = page.get_pixmap(dpi=150)
        img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
        imagenes.append(img)

    return imagenes

def crear_pdf_con_sello(imagenes, salida_pdf, texto_sello="PDF SEALED ✓"):
    buffer = BytesIO()
    c = canvas.Canvas(buffer, pagesize=A4)

    fecha = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    for img in imagenes:
        # Redimensionar imagen al tamaño de la página (A4)
        img_io = BytesIO()
        img.save(img_io, format='PNG')
        img_io.seek(0)
        image_reader = ImageReader(img_io)

        page_width, page_height = A4
        img_width, img_height = img.size
        aspect = img_height / img_width

        scaled_width = page_width
        scaled_height = page_width * aspect

        if scaled_height > page_height:
            scaled_height = page_height
            scaled_width = page_height / aspect

        x = (page_width - scaled_width) / 2
        y = (page_height - scaled_height) / 2

        c.drawImage(image_reader, x, y, width=scaled_width, height=scaled_height)

        # Añadir sello real (texto vectorial)
        c.setFont("Helvetica-Bold", 22)
        c.setFillColorRGB(1, 0, 0)  # rojo
        c.drawString(340, 40, texto_sello) #modificar

        # Fecha debajo del sello
        c.setFont("Helvetica", 10)
        c.setFillColorRGB(0, 0, 0)
        c.drawString(340, 30, fecha)

        c.showPage()

    c.save()
    with open(salida_pdf, "wb") as f:
        f.write(buffer.getvalue())

def procesar_pdf(pdf_path, salida_pdf):
    imagenes = convertir_paginas_a_imagenes(pdf_path)
    crear_pdf_con_sello(imagenes, salida_pdf)

def seleccionar_pdf():
    archivo = filedialog.askopenfilename(filetypes=[("PDF files", "*.pdf")])
    if archivo:
        nombre = os.path.basename(archivo)
        salida = os.path.join(os.path.dirname(archivo), f"sellado_textual_{nombre}")
        try:
            procesar_pdf(archivo, salida)
            messagebox.showinfo("Éxito", f"PDF sellado creado:\n{salida}")
        except Exception as e:
            messagebox.showerror("Error", f"Fallo al procesar:\n{e}")