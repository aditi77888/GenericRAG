from pathlib import Path

from loaders.base_loader import BaseLoader


class PDFLoader(BaseLoader):

    SUPPORTED_EXTENSIONS = {".pdf"}

    def load(self, source):

        path = self._validate_pdf(source)

        return path

    def _validate_pdf(self, source):

        path = Path(source)

        if not path.exists():
            raise FileNotFoundError(
                f"PDF not found: {path}"
            )

        if path.suffix.lower() != ".pdf":
            raise ValueError(
                "Only PDF files are supported."
            )

        return path