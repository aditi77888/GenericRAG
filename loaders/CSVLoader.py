import pandas as pd
from pathlib import Path

from loaders.base_loader import BaseLoader
from models.document import Document


class CSVLoader(BaseLoader):

    def load(self, source):

        path = self._validate_file(source)

        dataframe = self._read_csv(path)

        documents = []

        for index, row in dataframe.iterrows():

            document = self._create_document(
                row=row,
                row_number=index + 1,
                file_path=path
            )

            documents.append(document)

        return documents

    def _validate_file(self, source):

        path = Path(source)

        if not path.exists():
            raise FileNotFoundError(f"File not found: {path}")

        if path.suffix.lower() != ".csv":
            raise ValueError("Only .csv files are supported.")

        return path

    def _read_csv(self, path):

        return pd.read_csv(path)

    def _create_document(
        self,
        row,
        row_number,
        file_path
    ) -> Document:

        content = "\n".join(
            f"{column}: {value}"
            for column, value in row.items()
        )

        metadata = {
            "source": str(file_path),
            "file_name": file_path.name,
            "file_type": "csv",
            "row": row_number
        }

        return Document(
            content=content,
            metadata=metadata
        )