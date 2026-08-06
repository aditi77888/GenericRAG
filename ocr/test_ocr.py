from PIL import Image
import numpy as np
from ocr.paddleocr_engine import PaddleOCREngine

ocr = PaddleOCREngine()
result = ocr.extract("sample.png")
print(result)