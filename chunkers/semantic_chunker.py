from models.chunk import Chunk
from chunkers.base_chunker import BaseChunker


class SemanticChunker(BaseChunker):

    def __init__(
            self,
            embedding_model,
            similarity_threshold=0.7
    ):

        self.embedding_model = embedding_model
        self.similarity_threshold = similarity_threshold

    def chunk(self, documents):

        final_chunks = []
        chunk_id = 0

        for document in documents:

            sentences = self._split_sentences(
                document.content
            )

            if not sentences:
                continue

            embeddings = self._embed_sentences(
                sentences
            )

            groups = self._group_sentences(
                sentences,
                embeddings
            )

            for group in groups:

                metadata = document.metadata.copy()

                metadata["chunk_id"] = chunk_id

                final_chunks.append(
                    Chunk(
                        content=" ".join(group),
                        metadata=metadata
                    )
                )

                chunk_id += 1

        return final_chunks

    def _split_sentences(self, text):

        sentences = []

        current = ""

        for character in text:

            current += character

            if character in ".!?":

                sentence = current.strip()

                if sentence:
                    sentences.append(sentence)

                current = ""

        if current.strip():

            sentences.append(
                current.strip()
            )

        return sentences

    def _embed_sentences(self, sentences):

        return self.embedding_model.embed_documents(
            sentences
        )

    def _group_sentences(
            self,
            sentences,
            embeddings
    ):

        groups = []

        current_group = [
            sentences[0]
        ]

        for index in range(1, len(sentences)):

            similarity = self._cosine_similarity(
                embeddings[index - 1],
                embeddings[index]
            )

            if similarity >= self.similarity_threshold:

                current_group.append(
                    sentences[index]
                )

            else:

                groups.append(
                    current_group
                )

                current_group = [
                    sentences[index]
                ]

        if current_group:

            groups.append(
                current_group
            )

        return groups

    def _cosine_similarity(
            self,
            vector_a,
            vector_b
    ):

        dot_product = sum(
            a * b
            for a, b in zip(
                vector_a,
                vector_b
            )
        )

        magnitude_a = sum(
            a * a
            for a in vector_a
        ) ** 0.5

        magnitude_b = sum(
            b * b
            for b in vector_b
        ) ** 0.5

        if magnitude_a == 0 or magnitude_b == 0:
            return 0.0

        return (
            dot_product
            / (magnitude_a * magnitude_b)
        )