from retriever.vector_retriever import VectorRetriever


class RetrieverFactory:

    @staticmethod
    def create(
            retriever_name,
            embedding_model,
            vector_store
    ):

        retriever_name = retriever_name.lower()

        if retriever_name == "vector":
            return VectorRetriever(
                embedding_model,
                vector_store
            )

        raise ValueError(
            f"Unsupported retriever: {retriever_name}"
        )