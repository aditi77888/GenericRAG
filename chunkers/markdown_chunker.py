from models.chunk import Chunk
from chunkers.base_chunker import BaseChunker


class MarkdownChunker(BaseChunker):

    def __init__(
            self,
            chunk_size=500,
            chunk_overlap=50
    ):

        if chunk_overlap >= chunk_size:
            raise ValueError(
                "chunk_overlap must be smaller than chunk_size."
            )

        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap

    def chunk(self, documents):

        final_chunks = []
        chunk_id = 0

        for document in documents:

            sections = self._split_sections(
                document.content
            )

            for section in sections:

                section_chunks = self._chunk_section(
                    section
                )

                for content in section_chunks:

                    metadata = document.metadata.copy()

                    metadata["chunk_id"] = chunk_id

                    final_chunks.append(
                        Chunk(
                            content=content,
                            metadata=metadata
                        )
                    )

                    chunk_id += 1

        return final_chunks

    def _split_sections(self, text):

        lines = text.splitlines()

        sections = []
        current_section = []

        for line in lines:

            # Markdown heading
            if line.strip().startswith("#"):

                if current_section:

                    sections.append(
                        "\n".join(current_section).strip()
                    )

                    current_section = []

            current_section.append(line)

        if current_section:

            sections.append(
                "\n".join(current_section).strip()
            )

        return [
            section
            for section in sections
            if section
        ]

    def _chunk_section(self, section):

        if len(section) <= self.chunk_size:
            return [section]

        lines = section.splitlines()

        chunks = []
        current = ""

        for line in lines:

            if not line.strip():
                continue

            candidate = (
                current + "\n" + line
                if current
                else line
            )

            if len(candidate) <= self.chunk_size:

                current = candidate

            else:

                if current:
                    chunks.append(
                        current.strip()
                    )

                overlap = self._get_overlap(
                    current
                )

                candidate = (
                    overlap + "\n" + line
                    if overlap
                    else line
                )

                if len(candidate) <= self.chunk_size:

                    current = candidate

                else:

                    chunks.append(line.strip())

                    current = ""

        if current:
            chunks.append(
                current.strip()
            )

        return chunks

    def _get_overlap(self, text):

        if not text or self.chunk_overlap <= 0:
            return ""

        words = text.split()

        overlap_words = []
        current_length = 0

        for word in reversed(words):

            word_length = len(word)

            if (
                current_length
                + word_length
                + 1
                > self.chunk_overlap
            ):
                break

            overlap_words.insert(
                0,
                word
            )

            current_length += (
                word_length + 1
            )

        return " ".join(overlap_words)