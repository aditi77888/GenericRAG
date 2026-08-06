from abc import ABC, abstractmethod
from models.ocr_result import OCRResult

class BaseOCR(ABC):
    """
        Base class for all OCR engines.
    """
    @abstractmethod
    def extract(self, image) -> str:
        """
                Extract text from an image.
                Args:
                    image:
                        PIL Image / NumPy array.
                Returns:
                    OCRResult
                """
        pass