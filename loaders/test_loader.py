from loaders.pdf_loader import PDFLoader

loader = PDFLoader()

"""pdf = loader._open_pdf('Learning Python by Mark Lutz.pdf')

print(type(pdf))

page = pdf[10]
text = loader._extract_text_from_page(page)

print(len(text))
print(repr(text[:500]))

print(page.get_text("text"))"""

"""doc = loader._create_document(text="hello aditi ..",
                              file_name="temp.pdf",
                              page_number=1)
print(doc)"""

from loaders.pdf_loader import PDFLoader

loader = PDFLoader()

documents = loader.load("Learning Python by Mark Lutz.pdf")

print(f"Documents: {len(documents)}")

print(documents[1].metadata)

print(documents[1].content[:500])