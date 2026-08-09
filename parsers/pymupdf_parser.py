import fitz

from models.document import Document
from parsers.base_parser import BaseParser


class PyMuPDFParser(BaseParser):

    def parse(self, source):

        pdf = fitz.open(source)

        documents = []

        for page_number, page in enumerate(pdf):

            text = page.get_text()

            documents.append(

                Document(

                    content=text,

                    metadata={

                        "source": source,

                        "page": page_number + 1

                    }

                )

            )

        pdf.close()

        return documents