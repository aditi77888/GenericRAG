from pathlib import Path

from loaders.base_loader import BaseLoader
from models.document import Document


class TXTLoader(BaseLoader):

    def load(self, source):

        path = self._validate_file(source)

        text = self._read_file(path)

        document = self._create_document(
            text,
            path
        )

        return [document]

    def _validate_file(self, source):

        path = Path(source)

        if not path.exists():
            raise FileNotFoundError(f"File not found: {path}")

        if path.suffix.lower() != ".txt":
            raise ValueError("Only .txt files are supported.")

        return path

    def _read_file(self, path):

        return path.read_text(
            encoding="utf-8"
        )

    def _create_document(
        self,
        text,
        path
    ) -> Document:

        metadata = {
            "source": str(path),
            "file_name": path.name,
            "file_type": "txt"
        }

        return Document(
            content=text,
            metadata=metadata
        )