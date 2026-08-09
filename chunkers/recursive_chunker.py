from models.chunk import Chunk
from chunkers.base_chunker import BaseChunker


class RecursiveChunker(BaseChunker):

    def __init__(
            self,
            chunk_size=500,
            chunk_overlap=50,
            length_function=len,
            separators=None
    ):

        if chunk_overlap >= chunk_size:
            raise ValueError(
                "chunk_overlap must be smaller than chunk_size."
            )

        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.length_function = length_function

        self.separators = separators or [
            "\n\n",
            "\n",
            ". ",
            " ",
            ""
        ]

    def chunk(self, documents):

        final_chunks = []
        chunk_id = 0

        for document in documents:

            pieces = self._split_text(
                document.content
            )

            for piece in pieces:

                metadata = document.metadata.copy()

                metadata["chunk_id"] = chunk_id

                final_chunks.append(
                    Chunk(
                        content=piece,
                        metadata=metadata
                    )
                )

                chunk_id += 1

        return final_chunks

    def _split_text(
            self,
            text,
            separators=None
    ):

        if separators is None:
            separators = self.separators

        text = text.strip()

        if not text:
            return []

        # Already small enough
        if self.length_function(text) <= self.chunk_size:
            return [text]

        # No separators left
        if not separators:
            return self._split_by_size(text)

        separator = separators[0]

        # Character-level splitting
        if separator == "":
            return self._split_by_size(text)

        splits = text.split(separator)

        results = []

        for split in splits:

            split = split.strip()

            if not split:
                continue

            if self.length_function(split) <= self.chunk_size:

                results.append(split)

            else:

                results.extend(
                    self._split_text(
                        split,
                        separators[1:]
                    )
                )

        return self._merge_splits(
            results,
            separator
        )

    def _merge_splits(
            self,
            splits,
            separator
    ):

        chunks = []
        current = ""

        for split in splits:

            if not split:
                continue

            if not current:

                current = split
                continue

            candidate = (
                current
                + separator
                + split
            )

            if self.length_function(candidate) <= self.chunk_size:

                current = candidate

            else:

                chunks.append(current.strip())

                # Keep character-based overlap
                if self.chunk_overlap > 0:

                    overlap = self._get_overlap(current)

                    # Move to the beginning of the first
                    # complete word in the overlap.


                else:

                    overlap = ""

                if overlap:

                    candidate = (
                        overlap
                        + separator
                        + split
                    )

                    if (
                        self.length_function(candidate)
                        <= self.chunk_size
                    ):
                        current = candidate

                    else:
                        current = split

                else:

                    current = split

        if current:

            chunks.append(current.strip())

        return chunks

    def _split_by_size(self, text):

        chunks = []

        start = 0

        while start < len(text):

            end = start + self.chunk_size

            chunk = text[start:end].strip()

            if chunk:

                chunks.append(chunk)

            start = end

        return chunks

    def _get_overlap(self, text):

        if self.chunk_overlap <= 0:
            return ""

        words = text.split()

        overlap_words = []
        current_length = 0

        for word in reversed(words):

            word_length = len(word)

            if current_length + word_length + 1 > self.chunk_overlap:
                break

            overlap_words.insert(0, word)

            current_length += word_length + 1

        return " ".join(overlap_words)