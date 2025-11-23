import os
import re
from glob import glob
import fitz
import ftfy

# OCR imports
try:
    import pytesseract
    from PIL import Image
    import io

    OCR_AVAILABLE = True
except ImportError:
    OCR_AVAILABLE = False
    print("Install: pip install pytesseract pillow")

os.makedirs("irdai_pdfs/texts", exist_ok=True)


def remove_hindi(text):
    """Remove Devanagari script"""
    return re.sub(r"[\u0900-\u097F]+", " ", text)


def is_garbage_text(text):
    """Check if extracted text is garbage/unusable"""
    if not text or len(text) < 50:
        return True

    # Remove Hindi first
    english = remove_hindi(text).strip()

    # If very little English remains
    if len(english) < 50:
        return True

    # Check ratio of alphanumeric to total characters
    alnum = sum(c.isalnum() or c.isspace() for c in english)
    if len(english) > 0 and alnum / len(english) < 0.7:
        return True

    return False


def ocr_page(page, zoom=2.5):
    """OCR a page using Tesseract - English only"""
    if not OCR_AVAILABLE:
        return ""

    mat = fitz.Matrix(zoom, zoom)
    pix = page.get_pixmap(matrix=mat)
    img = Image.open(io.BytesIO(pix.tobytes("png")))

    # English only, document mode
    text = pytesseract.image_to_string(img, lang="eng", config="--psm 6 --oem 3")
    return text


def extract_text(path):
    text_parts = []
    method_used = []

    try:
        doc = fitz.open(path)

        for i, page in enumerate(doc):
            # First try direct extraction
            txt = page.get_text("text")
            txt_clean = remove_hindi(txt).strip()

            # If direct extraction is garbage, try OCR
            if is_garbage_text(txt_clean):
                if OCR_AVAILABLE:
                    txt = ocr_page(page)
                    txt_clean = remove_hindi(txt).strip()
                    method_used.append("ocr")
                else:
                    method_used.append("failed")
            else:
                method_used.append("direct")

            if txt_clean:
                text_parts.append(txt_clean)

        doc.close()

        # Print summary
        direct = method_used.count("direct")
        ocr = method_used.count("ocr")
        failed = method_used.count("failed")
        print(
            f"  Pages: {len(method_used)} | Direct: {direct} | OCR: {ocr} | Failed: {failed}"
        )

    except Exception as e:
        print(f"  Error: {e}")

    return "\n\n".join(text_parts)


def clean_text(text):
    # Fix encoding
    text = ftfy.fix_text(text)
    # Remove any remaining Hindi
    text = remove_hindi(text)
    # Clean up whitespace
    text = re.sub(r"\n{3,}", "\n\n", text)
    text = re.sub(r" {2,}", " ", text)
    # Remove empty lines
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    return "\n".join(lines)


def main():
    pdf_paths = glob("irdai_pdfs/*.pdf")
    print(f"Found {len(pdf_paths)} PDFs\n")

    failed_pdfs = []

    for i, path in enumerate(pdf_paths):
        filename = os.path.basename(path)
        out_path = os.path.join("irdai_pdfs/texts", filename.replace(".pdf", ".txt"))

        if os.path.exists(out_path):
            print(f"[{i + 1}/{len(pdf_paths)}] Skip: {filename}")
            continue

        print(f"[{i + 1}/{len(pdf_paths)}] {filename}")

        text = extract_text(path)

        if not text or len(text) < 100:
            print(f"  FAILED - insufficient text")
            failed_pdfs.append(filename)
            continue

        cleaned = clean_text(text)

        with open(out_path, "w", encoding="utf-8") as f:
            f.write(cleaned)

        print(f"  Saved: {len(cleaned)} chars")

    # Summary
    print(f"\n{'=' * 50}")
    print(f"Done! Failed: {len(failed_pdfs)}/{len(pdf_paths)}")
    if failed_pdfs:
        print("Failed files:")
        for f in failed_pdfs:
            print(f"  - {f}")


if __name__ == "__main__":
    main()
