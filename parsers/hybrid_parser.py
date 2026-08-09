import fitz

from parsers.base_parser import BaseParser
from parsers.pymupdf_parser import PyMuPDFParser
from parsers.mistral_parser import MistralParser


class HybridParser(BaseParser):

    def __init__(
            self,
            min_text_threshold=200
    ):

        self.min_text_threshold = min_text_threshold

        self.pymupdf = PyMuPDFParser()

        self.mistral = MistralParser()

    def parse(
            self,
            source
    ):

        pdf = fitz.open(source)

        documents = []

        for page_number, page in enumerate(pdf):

            text = self.pymupdf.extract_text(page)

            if len(text.strip()) >= self.min_text_threshold:

                document = self.pymupdf.create_document(

                    text=text,

                    source=source,

                    page_number=page_number + 1

                )

            else:

                image = self.pymupdf.render_page(page)

                ocr_result = self.mistral.ocr.extract_image(image)

                document = self.pymupdf.create_document(

                    text=ocr_result.text,

                    source=source,

                    page_number=page_number + 1

                )

                document.metadata.update(

                    ocr_result.metadata

                )

            documents.append(document)

        pdf.close()

        return documents