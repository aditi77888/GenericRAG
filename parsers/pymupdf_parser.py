import fitz
from PIL import Image
from models.document import Document
from parsers.base_parser import BaseParser


class PyMuPDFParser(BaseParser):

    def parse(self, source):

        pdf = fitz.open(source)

        documents = []

        for page_number, page in enumerate(pdf):

            text = self.extract_text(page)

            documents.append(

                self.create_document(

                    text=text,

                    source=source,

                    page_number=page_number + 1

                )

            )

        pdf.close()

        return documents

    def extract_text(self, page):

        return page.get_text("text").strip()

    def create_document(
            self,
            text,
            source,
            page_number
    ):

        return Document(

            content=text,

            metadata={

                "source": str(source),

                "page": page_number

            }

        )

    def render_page(
            self,
            page,
            dpi=300
    ):
        """
        Render a PDF page to a PIL Image.
        """

        pixmap = page.get_pixmap(dpi=dpi)

        return Image.frombytes(

            "RGB",

            [pixmap.width, pixmap.height],

            pixmap.samples

        )