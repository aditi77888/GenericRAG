from loaders.base_loader import BaseLoader


class PDFLoader(BaseLoader):
    def __init__(selfself,ocr_engine=None):
        self.ocr_engine = ocr_engine

    def load(self,source):
        pass

    def _open_pdf(self, source):
        pass

    def _extract_text_from_page(self, page):
        pass

    def _needs_ocr(self, text):
        pass

    def _perform_ocr(self, page):
        pass

    def _create_document(self, text, file_name, page_number):
        pass