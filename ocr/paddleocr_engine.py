from paddleocr import PaddleOCR

from models.ocr_result import OCRResult
from ocr.base_ocr import BaseOCR

class PaddleOCREngine(BaseOCR):
    def __init__(self):
        self.ocr = PaddleOCR(
            use_angle_cls=False,
            lang="en"
        )
    def extract(self, image) -> OCRResult:
        result = self.ocr.predict(image)

        print(result)

        return OCRResult(text="")



