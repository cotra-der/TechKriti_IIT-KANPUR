import fitz
import re

def extract_and_clean(pdf_path):
    doc = fitz.open(pdf_path)
    text = ""
    for page in doc:
        text += page.get_text() + " "
    
    text = text.replace('\n', ' ')
    text = re.sub(r'[^\x20-\x7E]', ' ', text)
    text = re.sub(r'\s+', ' ', text)
    
    name_pattern = r'(?i)\b(?:Name|Full Name)[:\-\s]+[A-Z][a-zA-Z\s\.\-]+'
    text = re.sub(name_pattern, '', text)
    
    phone_pattern = r'(?:(?:\+?\d{1,4}[\s.-]?)?(?:\d{5}[\s.-]?\d{5}|\(?\d{3}\)?[\s.-]?\d{3}[\s.-]?\d{4}|\d{10}))'
    text = re.sub(phone_pattern, '', text)
    
    email_pattern = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
    text = re.sub(email_pattern, '', text)
    
    url_pattern = r'(?:https?://|www\.)[^\s|]+(?:\.com|\.in|\.ai|\.co|\.org|\.net|\.io|\.tech|\.dev|\.xyz)?(?:/[^\s|]*)?'
    text = re.sub(url_pattern, '', text)
    
    gender_pattern = r'\b(he|she|his|her|him|male|female|mr\.?|ms\.?|mrs\.?)\b'
    text = re.sub(gender_pattern, '', text, flags=re.IGNORECASE)
    
    loc_pattern = r'\b[A-Z][a-zA-Z\s]+,\s*(?:[A-Z]{2}|[A-Z][a-zA-Z\s]+(?!\.))\b'
    text = re.sub(loc_pattern, '', text)
    
    title_keywords = ['Product Manager', 'Engineer', 'Developer', 'Analyst', 'Lead', 'Director', 'Technician']
    for kw in title_keywords:
        pos = text.lower().find(kw.lower())
        if pos != -1:
            text = text[pos:]
            break
    
    text = re.sub(r'\s*[\|—]\s*', ' ', text)
    text = " ".join(text.split())
    text = text.strip()
    
    return text

if __name__ == "__main__":
    result = extract_and_clean("./resume/2.pdf")
    print(result)