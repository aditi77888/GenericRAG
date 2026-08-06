from loaders.base_loader import BaseLoader
from models.document import Document
from pathlib import Path
import fitz


class PDFLoader(BaseLoader):
    def __init__(self,ocr_engine=None):
        self.ocr_engine = ocr_engine

    def load(self,source):
        """
            Loads a PDF and returns a list of Document objects.
            Args:
                source: Path to the PDF.
            Returns:
                List of Document objects (one per non-empty page).
            """
        pdf = self._open_pdf(source)

        documents=[]
        file_name = Path(source).name
        for page_index in range(len(pdf)):
            page = pdf[page_index]
            text = self._extract_text_from_page(page)

            if self._needs_ocr(text):
                text = self._perform_ocr(page)
            if not text.strip():
                continue

            document = self._create_document(
                text=text,
                file_name=file_name,
                page_number=page_index+1
            )
            documents.append(document)
        pdf.close()

        return documents


    def _open_pdf(self, source):
        """
           Opens a PDF file using PyMuPDF.
           Args:
               source: Path to the PDF file.
           Returns:
               fitz.Document object.
           Raises:
               FileNotFoundError:
                   If the PDF file does not exist.
               RuntimeError:
                   If the PDF cannot be opened.
           """
        path = Path(source)

        if not path.exists():
            raise FileNotFoundError("PDF not found: {path}")

        try:
            return fitz.open(path)
        except Exception as e:
            raise RuntimeError(f"Failed to open PDF: {e}")

    def _extract_text_from_page(self, page):
        """
            Extract plain text from a single PDF page.
            Args:
                page: A PyMuPDF page object.
            Returns:
                Extracted text as a string.
            """
        text = page.get_text("text")
        return text.strip()

    def _needs_ocr(self, text):
        """
            Determines whether OCR should be used.
            """
        return not text.strip()

    def _perform_ocr(self, page):
        """
            Placeholder for OCR.
            """
        if self.ocr_engine is None:
            return ""
        raise NotImplementedError("OCR support not implemented yet.")

    def _create_document(self, text: str, file_name: str, page_number: int) -> Document:
        """
            Creates a Document object for a single PDF page.
            Args:
                text: Extracted page text.
                file_name: Name of the PDF.
                page_number: Current page number (1-based).
            Returns:
                Document object.
            """
        metadata = {
            "file_name": file_name,
            "file_type": "pdf",
            "page": page_number
        }
        return Document(
            content=text,
            metadata=metadata
        )