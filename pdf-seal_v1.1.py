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

pdf_file = st.file_uploader("Selecciona un archivo PDF", type=["pdf"])

def convertir_paginas_a_imagenes(pdf_bytes):
    doc = fitz.open(stream=pdf_bytes, filetype="pdf")
    imagenes = []

    for page in doc:
        pix = page.get_pixmap(dpi=150)
        img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
        imagenes.append(img)

    return imagenes

def crear_pdf_con_sello(imagenes, texto_sello="PDF SEALED ✓"):
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
        c.drawString(340, 40, texto_sello)

        # Fecha debajo del sello
        c.setFont("Helvetica", 10)
        c.setFillColorRGB(0, 0, 0)
        c.drawString(340, 30, fecha)

        c.showPage()

    c.save()
    buffer.seek(0)
    return buffer

if pdf_file:
    pdf_bytes = pdf_file.read()
    images = convertir_paginas_a_imagenes(pdf_bytes)
    pdf_output_buffer = crear_pdf_con_sello(images)

    st.download_button(
        label="Descargar PDF sellado",
        data=pdf_output_buffer,
        file_name="pdf_selled.pdf",
        mime="application/pdf"
    )
