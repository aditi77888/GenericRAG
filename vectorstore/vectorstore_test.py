import time
from pathlib import Path

from loaders.loader_factory import LoaderFactory
from parsers.parser_factory import ParserFactory
from chunkers.chunker_factory import ChunkerFactory
from embeddings.embedding_factory import EmbeddingFactory
from vectorstore.vectorstore_factory import VectorStoreFactory


# ============================================================
# SOURCE
# ============================================================


SOURCE = Path(
    r"C:\Users\Hp-Laptop\PycharmProjects\GenericRAG\files\cibil.pdf"
)

NAMESPACE = "cibil_test"


print("=" * 80)
print("PINECONE VECTOR STORE TEST")
print("=" * 80)

print("\nSource :", SOURCE)
print("Exists :", SOURCE.exists())
print("Namespace :", NAMESPACE)


# ============================================================
# 1. LOADER
# ============================================================

print("\n" + "=" * 80)
print("1. LOADER")
print("=" * 80)

loader = LoaderFactory.create(SOURCE)

print(
    "Selected Loader :",
    loader.__class__.__name__
)

start = time.perf_counter()

loaded_data = loader.load(SOURCE)

loading_time = time.perf_counter() - start

print(
    f"Loading Time    : {loading_time:.4f} sec"
)


# ============================================================
# 2. PARSER
# ============================================================

print("\n" + "=" * 80)
print("2. PARSER")
print("=" * 80)

parser = ParserFactory.create(SOURCE)

print(
    "Selected Parser :",
    parser.__class__.__name__
)

start = time.perf_counter()

documents = parser.parse(
    loaded_data
)

parsing_time = time.perf_counter() - start

print(
    f"Parsing Time    : {parsing_time:.4f} sec"
)

print(
    "Documents       :",
    len(documents)
)


# ============================================================
# 3. CHUNKER
# ============================================================

print("\n" + "=" * 80)
print("3. CHUNKER")
print("=" * 80)

chunker = ChunkerFactory.create(
    "recursive"
)

print(
    "Selected Chunker :",
    chunker.__class__.__name__
)

start = time.perf_counter()

chunks = chunker.chunk(
    documents
)

chunking_time = time.perf_counter() - start

print(
    f"Chunking Time    : {chunking_time:.4f} sec"
)

print(
    "Chunks           :",
    len(chunks)
)


# ============================================================
# 4. EMBEDDING
# ============================================================

print("\n" + "=" * 80)
print("4. EMBEDDING")
print("=" * 80)

embedding_model = EmbeddingFactory.create(
    "bge"
)

print(
    "Selected Model :",
    embedding_model.__class__.__name__
)

start = time.perf_counter()

embeddings = embedding_model.embed_documents(
    chunks
)

embedding_time = time.perf_counter() - start

print(
    f"Embedding Time  : {embedding_time:.4f} sec"
)

print(
    "Embedding Type  :",
    type(embeddings)
)

print(
    "Embedding Shape :",
    embeddings.shape
)


# ============================================================
# 5. PINECONE
# ============================================================

print("\n" + "=" * 80)
print("5. PINECONE")
print("=" * 80)

vector_store = VectorStoreFactory.create(
    "pinecone"
)

print(
    "Selected Store :",
    vector_store.__class__.__name__
)


# ============================================================
# DELETE OLD TEST DATA
# ============================================================

print("\nDeleting old namespace data...")

vector_store.delete_namespace(
    NAMESPACE
)

print(
    "Old namespace deleted."
)


# ============================================================
# UPSERT
# ============================================================

print("\nUpserting vectors into Pinecone...")

start = time.perf_counter()

vector_store.add(
    chunks,
    embeddings,
    namespace=NAMESPACE
)

upsert_time = time.perf_counter() - start

print(
    f"Upsert Time : {upsert_time:.4f} sec"
)

print(
    f"Successfully uploaded {len(chunks)} vectors."
)


# ============================================================
# WAIT
# ============================================================

print("\nWaiting for Pinecone index...")

time.sleep(2)


# ============================================================
# QUERY
# ============================================================

query = "What factors affect the CIBIL score?"

print("\n" + "=" * 80)
print("6. VECTOR SEARCH")
print("=" * 80)

print(
    "Query :",
    query
)

start = time.perf_counter()

query_embedding = embedding_model.embed_query(
    query
)

results = vector_store.search(
    query_embedding,
    top_k=5,
    namespace=NAMESPACE
)

search_time = time.perf_counter() - start

print(
    f"\nSearch Time : {search_time:.4f} sec"
)

print(
    "Results     :",
    len(results)
)


# ============================================================
# DISPLAY RESULTS
# ============================================================

print("\n" + "=" * 80)
print("RETRIEVED CHUNKS")
print("=" * 80)

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
        chunk.metadata.get(
            "score"
        )
    )

    print(
        "Source :",
        chunk.metadata.get(
            "source"
        )
    )

    print(
        "Page :",
        chunk.metadata.get(
            "page"
        )
    )

    print(
        "Chunk ID :",
        chunk.metadata.get(
            "chunk_id"
        )
    )

    print(
        "\nContent:"
    )

    print(
        chunk.content[:500]
    )


# ============================================================
# SUMMARY
# ============================================================

print("\n" + "=" * 80)
print("SUMMARY")
print("=" * 80)

print(
    f"Documents        : {len(documents)}"
)

print(
    f"Chunks           : {len(chunks)}"
)

print(
    f"Embedding Shape  : {embeddings.shape}"
)

print(
    f"Vectors Upserted : {len(chunks)}"
)

print(
    f"Upsert Time      : {upsert_time:.4f} sec"
)

print(
    f"Search Time      : {search_time:.4f} sec"
)

print(
    "\nPINECONE TEST COMPLETE"
)