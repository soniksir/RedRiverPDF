import io
import os
from PyPDF2 import PdfReader, PdfWriter

def clone_pdf_pages(input_path):
    """
    PDF dosyasındaki her sayfayı belleğe kopyalayarak seek hatalarını önler.
    Geriye (sayfa listesi, toplam sayfa sayısı) döner.
    """
    with open(input_path, "rb") as infile:
        reader = PdfReader(infile)
        total_pages = len(reader.pages)
        page_clones = []
        for i in range(total_pages):
            writer = PdfWriter()
            writer.add_page(reader.pages[i])
            buffer = io.BytesIO()
            writer.write(buffer)
            buffer.seek(0)
            clone_reader = PdfReader(buffer)
            page_clones.append(clone_reader.pages[0])
    return page_clones, total_pages