from pathlib import Path

from parsers.hybrid_parser import HybridParser
from parsers.mistral_parser import MistralParser


class ParserFactory:

    @staticmethod
    def create(file_path):

        extension = Path(file_path).suffix.lower()

        if extension == ".pdf":
            return HybridParser()

        elif extension in {
            ".png",
            ".jpg",
            ".jpeg",
            ".bmp",
            ".tiff",
            ".webp"
        }:
            return MistralParser()

        return None