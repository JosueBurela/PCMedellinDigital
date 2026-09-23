import pypdf
import os

pdf_path = os.path.join("Documentacion", "ORIGEN", "Servicios de mayo.pdf")
reader = pypdf.PdfReader(pdf_path)
print(f"Total páginas en Servicios de mayo.pdf: {len(reader.pages)}")

# Extract text from first 5 pages and look for transfer patterns
transfer_count = 0
keywords = ["traslado", "hospital", "imss", "regional", "alta especialidad", "cruz roja", "urgencias"]

sample_services = []

for idx, page in enumerate(reader.pages):
    text = page.extract_text() or ""
    text_lower = text.lower()
    has_kw = any(k in text_lower for k in keywords)
    if has_kw:
        transfer_count += 1
        if len(sample_services) < 10:
            sample_services.append((idx + 1, text[:300].replace('\n', ' ')))

print(f"Páginas con mención a traslados/hospitales: {transfer_count}")
print("\nMuestra de páginas encontradas:")
for p, s in sample_services:
    print(f"Pág {p}: {s[:120]}...")
