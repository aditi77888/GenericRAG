from models.document import Document

from ocr.ocr_factory import OCRFactory
from parsers.base_parser import BaseParser


class MistralParser(BaseParser):
    """
    Parser for scanned documents.

    Uses the configured OCR engine to extract text
    from PDFs or images and converts the OCR output
    into the framework's Document objects.
    """

    def __init__(self):

        self.ocr = OCRFactory.create("mistral")

    def parse(
            self,
            source
    ):
        """
        Parse a scanned document.

        Parameters
        ----------
        source : str | Path
            Path to an image or scanned PDF.

        Returns
        -------
        list[Document]
        """

        ocr_result = self.ocr.extract(source)

        return [

            Document(

                content=ocr_result.text,

                metadata=ocr_result.metadata

            )

        ]