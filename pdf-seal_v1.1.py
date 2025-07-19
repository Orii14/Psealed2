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

uploaded_file = st.file_uploader("Selecciona un archivo PDF", type=["pdf"])

if uploaded_file is not None:
    # Guardar PDF subido en memoria
    pdf_bytes = uploaded_file.read()

    # Abrir PDF con PyMuPDF desde memoria
    pdf = fitz.open(stream=pdf_bytes, filetype="pdf")

    # Ruta del sello (puedes cambiar esto o permitir que el usuario lo suba también)
    sello_path = "sello.png"

    if not os.path.isfile(sello_path):
        st.error("⚠️ No se encontró el archivo 'sello.png'")
    else:
        # Cargar sello como imagen
        sello_image = Image.open(sello_path)
        sello_bytes = BytesIO()
        sello_image.save(sello_bytes, format="PNG")
        sello_bytes.seek(0)
        sello_reader = ImageReader(sello_bytes)

        # Crear nuevo PDF con ReportLab
        output = BytesIO()
        c = canvas.Canvas(output, pagesize=A4)

        # Agregar sello y fecha en cada página
        for page_num in range(len(pdf)):
            c.drawImage(sello_reader, A4[0] - 2 * inch, inch, width=1 * inch, height=1 * inch)

            fecha = datetime.now().strftime("%d/%m/%Y %H:%M")
            c.setFont("Helvetica", 10)
            c.drawString(0.75 * inch, inch, f"Firmado el {fecha}")

            c.showPage()

        c.save()

        # Mostrar y ofrecer descarga
        st.success("✅ PDF procesado con sello y fecha")
        st.download_button(
            label="📥 Descargar PDF sellado",
            data=output.getvalue(),
            file_name="pdf_sellado.pdf",
            mime="application/pdf"
        )
