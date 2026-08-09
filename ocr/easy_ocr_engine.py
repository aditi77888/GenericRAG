
import easyocr
from models.ocr_result import OCRResult
from ocr.base_ocr import BaseOCR

class EasyOCREngine(BaseOCR):
    def __init__(self):
        self.reader = easyocr.Reader(["en"], gpu=False)

    def extract(self, image: str) -> OCRResult:
        detections = self.reader.readtext(image)

        texts = []
        confidences = []

        for _, text, confidence in detections:
            texts.append(text)
            confidences.append(float(confidence))

        final_text = "\n".join(texts)

        avg_confidence = (
            sum(confidences) / len(confidences)
             if confidences else 0.0
        )
        return OCRResult(
            text=final_text,
            confidence=avg_confidence,
            metadata={
                "engine": "easyocr",
                "raw_output": detections
            }
        )