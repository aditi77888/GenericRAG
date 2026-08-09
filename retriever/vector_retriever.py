from retriever.base_retriever import BaseRetriever


class VectorRetriever(BaseRetriever):

    def __init__(
            self,
            embedding_model,
            vector_store
    ):
        self.embedding_model = embedding_model
        self.vector_store = vector_store

    def retrieve(
            self,
            query: str,
            top_k: int = 5,
            namespace: str = "default"
    ):

        query_embedding = self.embedding_model.embed_query(query)

        chunks = self.vector_store.search(
            query_embedding=query_embedding,
            top_k=top_k,
            namespace=namespace
        )

        return chunks