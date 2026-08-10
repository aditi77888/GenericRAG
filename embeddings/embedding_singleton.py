"""
Shared embedding model singleton.

Loading BAAI/bge-small-en-v1.5 (or whichever model is configured)
takes several seconds. Multiple parts of the app need an
embedding model:

  - RAGPipeline, to embed document chunks + retrieval queries
  - SupervisorAgent's semantic intent classifier, to embed
    incoming user messages for routing

Without this singleton, each of those would load its own copy
of the model into memory and pay the load cost separately. This
module guarantees the model is created exactly once per process
and shared everywhere.
"""

from embeddings.embedding_factory import EmbeddingFactory

_EMBEDDING_MODEL = None


def get_embedding_model(model_name: str = "bge"):

    global _EMBEDDING_MODEL

    if _EMBEDDING_MODEL is None:

        print(
            "[EMBEDDING SINGLETON] Creating shared "
            f"embedding model ({model_name})...",
            flush=True
        )

        _EMBEDDING_MODEL = EmbeddingFactory.create(
            model_name
        )

        print(
            "[EMBEDDING SINGLETON] Shared embedding "
            "model ready.",
            flush=True
        )

    else:

        print(
            "[EMBEDDING SINGLETON] Reusing shared "
            "embedding model.",
            flush=True
        )

    return _EMBEDDING_MODEL