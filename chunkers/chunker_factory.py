from chunkers.recursive_chunker import RecursiveChunker
from chunkers.markdown_chunker import MarkdownChunker


class ChunkerFactory:

    @staticmethod
    def create(
            chunker_name,
            **kwargs
    ):

        chunker_name = chunker_name.lower()

        if chunker_name == "recursive":
            return RecursiveChunker(**kwargs)

        elif chunker_name == "markdown":
            return MarkdownChunker(**kwargs)

        raise ValueError(
            f"Unknown chunker: {chunker_name}"
        )