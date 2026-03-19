#!/usr/bin/env python3
import pdfplumber
import os
import re

def clean_text(text):
    text = re.sub(r'\n{3,}', '\n\n', text)
    text = re.sub(r'[ \t]{2,}', ' ', text)
    return text.strip()

def extract_pdf_to_markdown(pdf_path, output_dir):
    filename = os.path.basename(pdf_path)
    base_name = os.path.splitext(filename)[0]
    output_path = os.path.join(output_dir, f"{base_name}.md")
    
    print(f"Processing: {filename}")
    
    all_text = []
    
    with pdfplumber.open(pdf_path) as pdf:
        for i, page in enumerate(pdf.pages):
            text = page.extract_text()
            if text:
                cleaned = clean_text(text)
                all_text.append(f"## Page {i + 1}\n\n{cleaned}")
            
            tables = page.extract_tables()
            if tables:
                for j, table in enumerate(tables):
                    if table and len(table) > 0:
                        table_md = []
                        if table[0]:
                            header = "| " + " | ".join(str(cell) if cell else "" for cell in table[0]) + " |"
                            separator = "| " + " | ".join(["---"] * len(table[0])) + " |"
                            table_md.append(header)
                            table_md.append(separator)
                            for row in table[1:]:
                                if row:
                                    row_str = "| " + " | ".join(str(cell) if cell else "" for cell in row) + " |"
                                    table_md.append(row_str)
                            if table_md:
                                all_text.append(f"\n### Table {j + 1}\n\n" + "\n".join(table_md))
    
    markdown_content = f"# {base_name}\n\n" + "\n\n".join(all_text)
    
    os.makedirs(output_dir, exist_ok=True)
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(markdown_content)
    
    print(f"Saved: {output_path}")
    return output_path

def main():
    pdf_files = [
        "/Users/nguyen.tran/Documents/GitHub/navavej/doc inputs/ENG_POC_ Smart Health Checkup Recommendation Dashboard_FINAL.pdf",
        "/Users/nguyen.tran/Documents/GitHub/navavej/doc inputs/ENG_TOR - Smart Health Checkup Recommendation Dashboard v7_Final.pdf"
    ]
    
    output_dir = "/Users/nguyen.tran/Documents/GitHub/navavej/doc inputs"
    
    for pdf_path in pdf_files:
        if os.path.exists(pdf_path):
            extract_pdf_to_markdown(pdf_path, output_dir)
        else:
            print(f"File not found: {pdf_path}")

if __name__ == "__main__":
    main()