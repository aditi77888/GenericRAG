from ocr.ocr_factory import OCRFactory
from loaders.image_loader import ImageLoader

ocr = OCRFactory.create("easyocr")

loader = ImageLoader(ocr)

documents = loader.load("sample.png")

print(documents[0].content)
print(documents[0].metadata)