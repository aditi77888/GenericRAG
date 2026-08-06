from ocr.ocr_factory import OCRFactory

ocr = OCRFactory.create("easyocr")

result = ocr.extract("sample.png")

print(result.text)
print
print(result.confidence)
print(result.metadata["engine"])