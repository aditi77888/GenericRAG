from loaders.base_loader import BaseLoader
from pathlib import Path
from models.document import Document

class ImageLoader(BaseLoader):
    def __init__(self, ocr_engine):
        self.ocr_engine = ocr_engine

    SUPPORTED_EXTENSIONS = {
        ".png",
        ".jpg",
        ".jpeg",
        ".bmp",
        ".tiff",
        ".webp"
    }

    def _validate_image(self, source):
        """
        Validates that the image exists and has a supported format.
        Args:
            source: Path to the image.
        Returns:
            Path object.
        Raises:
            FileNotFoundError
            ValueError
        """
        path = Path(source)
        if not path.exists():
            raise FileNotFoundError(f"Image not found: {path}")

        if path.suffix.lower() not in self.SUPPORTED_EXTENSIONS:
            raise ValueError(
                f"Unsupported image format: {path.suffix}"
            )

        return path

    def load(self, source):
        """
           Loads an image and returns it as a Document.
           Args:
               source: Path to the image.
           Returns:
               List containing a single Document.
           """
        image_path = self._validate_image(source)

        ocr_result = self._perform_ocr(image_path)

        document = self._create_document(
            ocr_result,
            image_path
        )

        return [document]

    def _perform_ocr(self, image_path):
        """
        Performs OCR on an image.
        Args:
            image_path: Path object.
        Returns:
            OCRResult
        """

        return self.ocr_engine.extract(str(image_path))

    def _create_document(self, ocr_result, image_path: Path) -> Document:
        """
        Creates a Document object from OCR output.
        Args:
            ocr_result: OCRResult returned by the OCR engine.
            image_path: Path to the image.
        Returns:
            Document object.
        """
        metadata = {
            "source": str(image_path),
            "file_name": image_path.name,
            "file_type": "image",
            "ocr_engine": ocr_result.metadata.get("engine"),
            "ocr_confidence": ocr_result.confidence
        }
        return Document(
            content=ocr_result.text,
            metadata=metadata
        )

