import fitz  # PyMuPDF
import pytesseract
from pdf2image import convert_from_path
from PIL import Image
import os

def extract_text_from_pdf(filepath):
    text = ""
    try:
        # Tenter d'ouvrir avec PyMuPDF
        with fitz.open(filepath) as doc:
            for page in doc:
                text += page.get_text()
        if text.strip() == "":
            raise Exception("Page vide détectée")
    except:
        # OCR fallback
        images = convert_from_path(filepath)
        for img in images:
            gray = img.convert("L")
            text += pytesseract.image_to_string(gray)
    return text
