from ocr.mistral_ocr import MistralOCR


class OCRFactory:

    @staticmethod
    def create(engine="mistral"):

        engine = engine.lower()

        if engine == "mistral":
            return MistralOCR()

        raise ValueError(
            f"Unknown OCR engine: {engine}"
        )