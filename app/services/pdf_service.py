import fitz  # pymupdf
import tempfile
import os

def extract_pdf(file_bytes: bytes) -> dict:
    with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp:
        tmp.write(file_bytes)
        tmp_path = tmp.name

    doc = None
    try:
        doc = fitz.open(tmp_path)
        pages = []
        scanned_pages = []

        for i, page in enumerate(doc):
            text = page.get_text().strip()
            if len(text) > 50:
                pages.append({"page": i + 1, "content": text})
            else:
                scanned_pages.append(i + 1)

        full_text = "\n\n".join(p["content"] for p in pages)
        total_chars = len(full_text)

        if total_chars < 100:
            return {
                "success": False,
                "text": None,
                "method": "native",
                "warning": "PDF appears to be scanned. No text could be extracted.",
                "scanned_pages": scanned_pages,
                "page_count": len(doc)
            }

        return {
            "success": True,
            "text": full_text,
            "method": "native",
            "warning": f"Pages {scanned_pages} may be scanned and were skipped." if scanned_pages else None,
            "page_count": len(doc),
            "char_count": total_chars
        }

    finally:
        if doc:
            doc.close()        
        os.unlink(tmp_path)    