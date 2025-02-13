import os
import json
import re
import PyPDF2


def extract_text_from_pdf(pdf_path):
    text = ""
    with open(pdf_path, "rb") as file:
        reader = PyPDF2.PdfReader(file)
        for page in reader.pages:
            text += page.extract_text() + "\n"
    return text

def find_sections(text):
    sections = {
        "purpose": ["Objective", "Career Objective", "Purpose"],
        "experience": ["Experience", "Work Experience", "Employment History"],
        "projects": ["Projects", "Project Experience", "Extracurriculars", "Personal Projects"],
        "skills": ["Skills", "Technical Skills", "Relevant Skills"]
    }
    
    extracted_data = {}
    
    section_patterns = {key: re.compile(rf"(?:{'|'.join(map(re.escape, headers))})", re.IGNORECASE) for key, headers in sections.items()}
    
    matches = sorted(
        [(match.start(), key) for key, pattern in section_patterns.items() for match in pattern.finditer(text)],
        key=lambda x: x[0]
    )
    
    if not matches:
        return extracted_data
    
    for i in range(len(matches)):
        start_idx = matches[i][0]
        section_name = matches[i][1]
        end_idx = matches[i + 1][0] if i + 1 < len(matches) else len(text)
        extracted_data[section_name] = text[start_idx:end_idx].strip()
    
    return extracted_data

def process_resumes(directory):
    resume_data = []
    
    for file_name in os.listdir(directory):
        if file_name.lower().endswith(".pdf"):
            pdf_path = os.path.join(directory, file_name)
            text = extract_text_from_pdf(pdf_path)
            extracted_sections = find_sections(text)
            
            resume_entry = {"file_name": file_name, **extracted_sections}
            resume_data.append(resume_entry)
    
    return resume_data

# TODO: Usage
directory_path = r"C:\Users\junkn\OneDrive\Desktop\Chrome Downloads\reusmer"
parsed_resumes = process_resumes(directory_path)

# Save as JSON
output_file = "parsed_resumes.json"
with open(output_file, "w", encoding="utf-8") as f:
    json.dump(parsed_resumes, f, indent=4)

print(f"Parsed resumes saved to {output_file}")
