import os
import fitz  # PyMuPDF

# === Input ===
PDF_PATH = "pdf.pdf"
OUTPUT_PATH = "laws_texts/personal_status_law.txt"

def extract_text_from_pdf(pdf_path):
    doc = fitz.open(pdf_path)
    full_text = ""

    for page_num, page in enumerate(doc):
        text = page.get_text()
        full_text += f"\n\n# الصفحة {page_num + 1} #\n{text.strip()}"

    return full_text

def main():
    if not os.path.exists(PDF_PATH):
        print(f"❌ PDF file not found: {PDF_PATH}")
        return

    print(f"📄 Extracting text from {PDF_PATH}...")
    text = extract_text_from_pdf(PDF_PATH)

    if len(text) < 500:
        print("⚠️ Warning: Extracted text is too short.")
    else:
        os.makedirs("laws_texts", exist_ok=True)
        with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
            f.write(text)
        print(f"✅ Saved extracted text to {OUTPUT_PATH}")

if __name__ == "__main__":
    main()