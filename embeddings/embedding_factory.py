from embeddings.qwen_embedding import QwenEmbedding
from embeddings.bge_embedding import BGEEmbedding
from embeddings.bge_large_embedding import BGELargeEmbedding


class EmbeddingFactory:

    @staticmethod
    def create(model_name: str = "bge"):

        model_name = model_name.lower()

        if model_name == "bge":
            return BGEEmbedding()

        elif model_name == "qwen":
            return QwenEmbedding()

        raise ValueError(
            f"Unsupported embedding model: {model_name}"
        )