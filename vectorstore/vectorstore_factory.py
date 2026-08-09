from vectorstore.pinecone_vectorstore import PineconeVectorStore


class VectorStoreFactory:

    @staticmethod
    def create(name: str = "pinecone"):

        name = name.lower()

        if name == "pinecone":
            return PineconeVectorStore()

        raise ValueError(
            f"Unsupported vector store: {name}"
        )