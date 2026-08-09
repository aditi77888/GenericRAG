from embeddings.embedding_factory import EmbeddingFactory
from retriever.retriever_factory import RetrieverFactory
from vectorstore.vectorstore_factory import VectorStoreFactory


# ============================================================
# CONFIG
# ============================================================

QUERY = "What factors affect the CIBIL score?"

NAMESPACE = "cibil_test"

TOP_K = 5


# ============================================================
# EMBEDDING
# ============================================================

print("=" * 80)
print("RETRIEVER TEST")
print("=" * 80)

print("\nCreating embedding model...")

embedding_model = EmbeddingFactory.create(
    "bge"
)

print(
    "Embedding Model :",
    embedding_model.__class__.__name__
)


# ============================================================
# VECTOR STORE
# ============================================================

print("\nCreating vector store...")

vector_store = VectorStoreFactory.create(
    "pinecone"
)

print(
    "Vector Store :",
    vector_store.__class__.__name__
)


# ============================================================
# RETRIEVER
# ============================================================

print("\nCreating retriever...")

retriever = RetrieverFactory.create(
    retriever_name="vector",
    embedding_model=embedding_model,
    vector_store=vector_store
)

print(
    "Retriever :",
    retriever.__class__.__name__
)


# ============================================================
# RETRIEVE
# ============================================================

print("\n" + "=" * 80)
print("QUERY")
print("=" * 80)

print(
    "Query :",
    QUERY
)

print(
    "Top K :",
    TOP_K
)

print(
    "Namespace :",
    NAMESPACE
)


results = retriever.retrieve(
    query=QUERY,
    top_k=TOP_K,
    namespace=NAMESPACE
)


# ============================================================
# RESULTS
# ============================================================

print("\n" + "=" * 80)
print("RETRIEVED CHUNKS")
print("=" * 80)

print(
    "Results :",
    len(results)
)


for index, chunk in enumerate(
        results,
        start=1
):

    print(
        f"\nResult {index}"
    )

    print("-" * 60)

    print(
        "Score :",
        chunk.metadata.get("score")
    )

    print(
        "Page :",
        chunk.metadata.get("page")
    )

    print(
        "Chunk ID :",
        chunk.metadata.get("chunk_id")
    )

    print("\nContent:\n")

    print(
        chunk.content[:500]
    )


print("\n" + "=" * 80)
print("RETRIEVER TEST COMPLETE")
print("=" * 80)