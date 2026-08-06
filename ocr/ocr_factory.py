from ocr.easy_ocr_engine import EasyOCREngine
from ocr.paddleocr_engine import PaddleOCREngine

class OCRFactory:
    @staticmethod
    def create(engine: str):
        engine = engine.lower()

        if engine == 'easyocr':
            return EasyOCREngine()

        raise ValueError(f"Unsupported ocr engine: {engine}")