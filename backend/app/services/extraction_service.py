import os
from typing import Dict

import pypdf
from docx import Document
from PIL import Image
import pytesseract

from app.core.logger import logger

# Text length below which a "successfully extracted" PDF/DOCX is treated as
# suspiciously empty and worth falling back to OCR (handles PDFs that are
# mostly a scanned image with a couple of stray text layer artifacts).
MIN_MEANINGFUL_CHARS = 20


class ExtractionService:
    """Service for extracting text and metadata from various file types"""

    SUPPORTED_EXTENSIONS = {
        '.pdf': 'pdf',
        '.docx': 'docx',
        '.doc': 'doc',
        '.txt': 'text',
        '.png': 'image',
        '.jpg': 'image',
        '.jpeg': 'image',
        '.gif': 'image'
    }

    def extract(self, file_path: str) -> Dict:
        """
        Extract text and metadata from a file

        Returns:
            {
                "text": str,
                "file_type": str,
                "pages": int (for PDFs),
                "word_count": int,
                "error": str (only present on failure)
            }
        """
        ext = os.path.splitext(file_path)[1].lower()
        file_type = self.SUPPORTED_EXTENSIONS.get(ext, 'unknown')

        try:
            if file_type == 'pdf':
                return self._extract_pdf(file_path)
            elif file_type == 'docx':
                return self._extract_docx(file_path)
            elif file_type == 'doc':
                # python-docx only understands the modern .docx (OpenXML) format.
                # Legacy binary .doc files need a different library entirely
                # (e.g. antiword, textract) -- rather than silently failing with
                # a generic "could not extract text" message, tell the user
                # exactly what to do.
                return {
                    "text": "",
                    "file_type": "doc",
                    "error": "Legacy .doc files aren't supported yet -- please re-save this as .docx (in Word: File > Save As > Word Document) and re-upload."
                }
            elif file_type == 'text':
                return self._extract_text(file_path)
            elif file_type == 'image':
                return self._extract_image(file_path)
            else:
                logger.warning(f"Unsupported file type: {ext}")
                return {"text": "", "file_type": file_type, "error": "Unsupported format"}
        except Exception as e:
            logger.error(f"❌ Extraction failed for {file_path}: {e}")
            return {"text": "", "file_type": file_type, "error": str(e)}

    def _extract_pdf(self, file_path: str) -> Dict:
        """Extract text from PDF, falling back to OCR for scanned/image-only pages."""
        text_parts = []
        page_count = 0

        try:
            # NOTE: pypdf.PdfReader is NOT a context manager -- do not wrap
            # this in `with ... as`, it will raise immediately.
            pdf = pypdf.PdfReader(file_path)
            page_count = len(pdf.pages)
            for page in pdf.pages:
                text = page.extract_text()
                if text:
                    text_parts.append(text)
        except Exception as e:
            logger.warning(f"pypdf text layer extraction failed for {file_path}: {e}")

        full_text = "\n".join(text_parts).strip()

        # If the PDF has little to no extractable text layer, it's likely a
        # scanned document -- rasterize pages and OCR them instead.
        if len(full_text) < MIN_MEANINGFUL_CHARS:
            ocr_text = self._ocr_pdf(file_path)
            if len(ocr_text.strip()) > len(full_text):
                full_text = ocr_text.strip()

        return {
            "text": full_text,
            "file_type": "pdf",
            "pages": page_count,
            "word_count": len(full_text.split())
        }

    def _ocr_pdf(self, file_path: str) -> str:
        """
        OCR fallback for scanned PDFs. Uses PyMuPDF (fitz) to rasterize pages
        in-process -- deliberately chosen over pdf2image/poppler, which needs
        a separate system-level binary that's a common deployment headache
        (especially on Windows). PyMuPDF ships as a self-contained wheel.
        """
        text_parts = []
        try:
            import fitz  # PyMuPDF

            doc = fitz.open(file_path)
            for page in doc:
                pix = page.get_pixmap(dpi=200)
                image = Image.frombytes("RGB", (pix.width, pix.height), pix.samples)
                text = pytesseract.image_to_string(image)
                if text:
                    text_parts.append(text)
            doc.close()
        except ImportError:
            logger.warning("PyMuPDF not installed -- cannot OCR scanned PDFs. Install with: pip install PyMuPDF")
        except Exception as e:
            logger.error(f"PDF OCR fallback failed for {file_path}: {e}")

        return "\n".join(text_parts)

    def _extract_docx(self, file_path: str) -> Dict:
        """Extract text (paragraphs + tables) from a modern .docx file."""
        try:
            doc = Document(file_path)
            paragraphs = [p.text for p in doc.paragraphs if p.text.strip()]
            full_text = "\n".join(paragraphs)

            tables_text = []
            for table in doc.tables:
                for row in table.rows:
                    row_text = [cell.text for cell in row.cells]
                    tables_text.append(" | ".join(row_text))

            if tables_text:
                full_text += "\n" + "\n".join(tables_text)

            return {
                "text": full_text,
                "file_type": "docx",
                "pages": max(1, len(full_text) // 2000),
                "word_count": len(full_text.split())
            }
        except Exception as e:
            logger.error(f"DOCX extraction error: {e}")
            return {"text": "", "file_type": "docx", "error": str(e)}

    def _extract_text(self, file_path: str) -> Dict:
        """Extract text from plain text files"""
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()

            return {
                "text": content,
                "file_type": "text",
                "pages": max(1, len(content) // 2000),
                "word_count": len(content.split())
            }
        except Exception as e:
            logger.error(f"Text extraction error: {e}")
            return {"text": "", "file_type": "text", "error": str(e)}

    def _extract_image(self, file_path: str) -> Dict:
        """Extract text from images using OCR"""
        try:
            image = Image.open(file_path)
            text = pytesseract.image_to_string(image)

            return {
                "text": text,
                "file_type": "image",
                "image_size": image.size,
                "word_count": len(text.split())
            }
        except Exception as e:
            logger.error(f"Image OCR error: {e}")
            return {"text": "", "file_type": "image", "error": str(e)}


# Singleton instance
extraction_service = ExtractionService()