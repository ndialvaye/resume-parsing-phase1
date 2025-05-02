
import streamlit as st
import pandas as pd
import fitz  # PyMuPDF
import pytesseract
from pdf2image import convert_from_bytes
import re
from difflib import get_close_matches
from io import BytesIO

skills_list = ["Python", "Java", "SQL", "Excel", "Git", "Linux", "HTML", "CSS", "Docker", "Flask", "Django", "Pandas"]

def extract_text(file):
    text = ""
    try:
        doc = fitz.open(stream=file.read(), filetype="pdf")
        for page in doc:
            text += page.get_text()
        if not text.strip():
            raise Exception("Empty text, fallback to OCR")
    except:
        file.seek(0)
        images = convert_from_bytes(file.read())
        for img in images:
            gray = img.convert("L")
            text += pytesseract.image_to_string(gray)
    return text

def extract_data(text):
    data = {
        "Nom": "", "Email": "", "Téléphone": "", "Adresse": "",
        "Langues": "", "Compétences": "", "Expérience": "", "Formation": "", "Permis": ""
    }
    emails = re.findall(r'[\w\.-]+@[\w\.-]+\.\w+', text)
    if emails: data["Email"] = emails[0]
    phones = re.findall(r'(\+?\d[\d\s\-\(\)]{7,})', text)
    if phones: data["Téléphone"] = re.sub(r"[^\d+]", "", phones[0])
    name_line = text.strip().split("\n")[0]
    if len(name_line.split()) <= 5: data["Nom"] = name_line.title()
    license_match = re.search(r"permis\s+([A-Za-z])", text, re.IGNORECASE)
    if license_match: data["Permis"] = f"Permis {license_match.group(1).upper()}"
    langs = []
    for lang in ["Français", "Anglais", "Arabe", "Espagnol"]:
        if lang.lower() in text.lower(): langs.append(lang)
    data["Langues"] = ", ".join(langs)
    skill_words = re.findall(r'\b\w[\w\-\+#/.]*\b', text)
    matched_skills = set()
    for word in skill_words:
        match = get_close_matches(word, skills_list, n=1, cutoff=0.85)
        if match: matched_skills.add(match[0])
    data["Compétences"] = ", ".join(sorted(matched_skills))
    return data

st.title("📄 Analyse automatique de CV – Phase 1 : Extraction")
uploaded_files = st.file_uploader("Téléversez vos CVs PDF", type=["pdf"], accept_multiple_files=True)

if uploaded_files:
    all_results = []
    for file in uploaded_files:
        with st.spinner(f"Traitement de {file.name}..."):
            text = extract_text(file)
            data = extract_data(text)
            all_results.append(data)
    df = pd.DataFrame(all_results)
    st.success("✅ Extraction terminée")
    st.dataframe(df)

    buffer = BytesIO()
    with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
        df.to_excel(writer, index=False)
    st.download_button("📥 Télécharger les résultats (Excel)", data=buffer.getvalue(), file_name="resultats_phase1.xlsx")
else:
    st.info("Chargez un ou plusieurs fichiers PDF pour commencer.")
