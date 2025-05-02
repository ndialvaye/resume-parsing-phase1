import os
import pandas as pd
from extract_text import extract_text_from_pdf
import re
from difflib import get_close_matches

uploads_dir = "uploads"
output_file = "resultats_cv.xlsx"

skills_list = ["Python", "Java", "SQL", "Excel", "Git", "Linux", "HTML", "CSS", "Docker", "Flask", "Django", "Pandas"]

def extract_fields(text):
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

results = []
for filename in os.listdir(uploads_dir):
    if filename.endswith(".pdf"):
        print(f"Traitement de : {filename}")
        text = extract_text_from_pdf(os.path.join(uploads_dir, filename))
        data = extract_fields(text)
        results.append(data)

df = pd.DataFrame(results)
df.to_excel(output_file, index=False)
print(f"✅ Données extraites vers {output_file}")
