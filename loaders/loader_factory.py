from pathlib import Path

from loaders.CSVLoader import CSVLoader
from loaders.docx_loader import DOCXLoader
from loaders.image_loader import ImageLoader
from loaders.MarkdownLoader  import MarkdownLoader
from loaders.pdf_loader import PDFLoader
from loaders.textLoader import TXTLoader


class LoaderFactory:

    @staticmethod
    def create(file_path, ocr_engine=None):

        extension = Path(file_path).suffix.lower()

        if extension == ".pdf":
            return PDFLoader()

        elif extension in {
            ".png",
            ".jpg",
            ".jpeg",
            ".bmp",
            ".tiff",
            ".webp"
        }:
            return ImageLoader()

        elif extension == ".txt":
            return TXTLoader()

        elif extension == ".md":
            return MarkdownLoader()

        elif extension == ".csv":
            return CSVLoader()

        elif extension == ".docx":
            return DOCXLoader()

        raise ValueError(
            f"Unsupported file type: {extension}"
        )