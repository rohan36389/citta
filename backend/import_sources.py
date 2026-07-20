import os
import docx2txt
from pathlib import Path

BACKEND_DIR = Path(__file__).resolve().parent
SOURCE_DIR = BACKEND_DIR / "knowledge" / "source"
SOURCE_DIR.mkdir(parents=True, exist_ok=True)

def clean_extracted_text(text: str) -> str:
    # Clean typical Microsoft Word smart characters
    text = text.replace("\u201c", '"').replace("\u201d", '"')
    text = text.replace("\u2018", "'").replace("\u2019", "'")
    text = text.replace("\u2013", "-").replace("\u2014", "-")
    text = text.replace("\ufffd", "'") # Replace unresolved characters with clean quote
    return text

def run_import():
    print("=== Start One-Time Knowledge Base Source Import ===")
    
    kb_docx = SOURCE_DIR / "CittaAI_Knowledge_Base.docx"
    web_docx = SOURCE_DIR / "cittaai_complete-3.docx"
    
    if not kb_docx.exists():
        print(f"Error: {kb_docx} not found.")
        return
    if not web_docx.exists():
        print(f"Error: {web_docx} not found.")
        return
        
    # 1. Extract Website scraped content
    print(f"Extracting {web_docx.name}...")
    web_text = docx2txt.process(str(web_docx))
    web_text = clean_extracted_text(web_text)
    website_md_path = SOURCE_DIR / "website.md"
    with open(website_md_path, "w", encoding="utf-8") as f:
        f.write("# Scraped Website Content\n\n" + web_text)
    print(f"Saved {website_md_path.name}")

    # 2. Extract CittaAI Knowledge Base content
    print(f"Extracting {kb_docx.name}...")
    kb_text = docx2txt.process(str(kb_docx))
    kb_text = clean_extracted_text(kb_text)
    
    # Save the complete clean extracted text
    master_md_path = SOURCE_DIR / "cittaai_master_knowledge.md"
    with open(master_md_path, "w", encoding="utf-8") as f:
        f.write("# CittaAI Master Knowledge Base\n\n" + kb_text)
    print(f"Saved {master_md_path.name}")
    
    # Split into thematic md sources
    lines = kb_text.split("\n")
    current_section = None
    
    sections = {
        "Executive Summary": [],
        "Awards & Recognition": [],
        "About": [],
        "Contact": [],
        "Products": [],
        "Solutions": [],
        "Services": [],
        "Contact Information": []
    }
    
    for line in lines:
        line_strip = line.strip()
        if line_strip in sections:
            current_section = line_strip
            continue
        if current_section:
            sections[current_section].append(line)
            
    # Write cittaai_products_services.md
    prod_serv_path = SOURCE_DIR / "cittaai_products_services.md"
    with open(prod_serv_path, "w", encoding="utf-8") as f:
        f.write("# CittaAI Products, Solutions, and Services\n\n")
        f.write("## Products\n" + "\n".join(sections["Products"]) + "\n\n")
        f.write("## Solutions\n" + "\n".join(sections["Solutions"]) + "\n\n")
        f.write("## Services\n" + "\n".join(sections["Services"]) + "\n\n")
    print(f"Saved {prod_serv_path.name}")
    
    # Write recognition.md
    rec_path = SOURCE_DIR / "recognition.md"
    with open(rec_path, "w", encoding="utf-8") as f:
        f.write("# CittaAI Recognition & Achievements\n\n")
        f.write("\n".join(sections["Awards & Recognition"]))
    print(f"Saved {rec_path.name}")
    
    # Write contact_details.md
    contact_path = SOURCE_DIR / "contact_details.md"
    with open(contact_path, "w", encoding="utf-8") as f:
        f.write("# CittaAI Contact and Location Coordinates\n\n")
        f.write("\n".join(sections["Contact"]) + "\n\n")
        f.write("\n".join(sections["Contact Information"]))
    print(f"Saved {contact_path.name}")
    
    # Write partner_list.md (Hardcoded verified list as single source of truth for the demo)
    partners_path = SOURCE_DIR / "partner_list.md"
    with open(partners_path, "w", encoding="utf-8") as f:
        f.write("# CittaAI Manually Curated Partners List\n\n")
        f.write("CittaAI has 15+ Enterprise Partners with a 100% retention rate.\n")
        f.write("Publicly verified partner companies include:\n")
        partner_companies = [
            "Aurum Street", "Devarasa", "Green Leaves", "Nails by Mahas", "Olive Mithai", 
            "Premedis", "SRK Jawa", "SVS", "Shilpa Botanica", "Shaaranga", "Vegasri", "Axygen", "Fixity"
        ]
        for p in partner_companies:
            f.write(f"- {p}\n")
    print(f"Saved {partners_path.name}")
    
    print("=== Knowledge Source Import Complete ===")

if __name__ == "__main__":
    run_import()
