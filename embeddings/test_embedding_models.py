import time
from pathlib import Path

from loaders.loader_factory import LoaderFactory
from parsers.parser_factory import ParserFactory
from chunkers.chunker_factory import ChunkerFactory
from embeddings.embedding_factory import EmbeddingFactory


# ============================================================
# SOURCE
# ============================================================

SOURCE = Path(
    r"C:\Users\Hp-Laptop\PycharmProjects\GenericRAG\files\cibil.pdf"
)


print("=" * 80)
print("EMBEDDING PIPELINE TEST")
print("=" * 80)

print(f"\nSource : {SOURCE}")
print(f"Exists : {SOURCE.exists()}")


# ============================================================
# 1. LOAD
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
    f"Loading Time : {loading_time:.4f} sec"
)


# ============================================================
# 2. PARSE
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

documents = parser.parse(loaded_data)

parsing_time = time.perf_counter() - start

print(
    f"Parsing Time : {parsing_time:.4f} sec"
)

print(
    "Documents :",
    len(documents)
)


# ============================================================
# 3. CHUNK
# ============================================================

print("\n" + "=" * 80)
print("3. CHUNKER")
print("=" * 80)

chunker = ChunkerFactory.create(
    "recursive",
    chunk_size=500,
    chunk_overlap=50
)

print(
    "Selected Chunker :",
    chunker.__class__.__name__
)

start = time.perf_counter()

chunks = chunker.chunk(documents)

chunking_time = time.perf_counter() - start

print(
    f"Chunking Time : {chunking_time:.4f} sec"
)

print(
    "Chunks :",
    len(chunks)
)


# ============================================================
# 4. EMBEDDING MODEL
# ============================================================

print("\n" + "=" * 80)
print("4. EMBEDDING MODEL")
print("=" * 80)

start = time.perf_counter()

embedding_model = EmbeddingFactory.create("qwen")

model_load_time = time.perf_counter() - start

print(
    "Selected Model :",
    embedding_model.__class__.__name__
)

print(
    f"Model Load Time : "
    f"{model_load_time:.4f} sec"
)


# ============================================================
# 5. EMBED DOCUMENTS
# ============================================================

print("\n" + "=" * 80)
print("5. DOCUMENT EMBEDDINGS")
print("=" * 80)
print("\n" + "=" * 80)
print("EMBEDDING PERFORMANCE TEST")
print("=" * 80)

# One chunk
start = time.perf_counter()

one_embedding = embedding_model.embed_documents(
    chunks[:1]
)

single_time = time.perf_counter() - start

print(
    f"1 chunk embedding time : {single_time:.4f} sec"
)


# All chunks
start = time.perf_counter()

all_embeddings = embedding_model.embed_documents(
    chunks
)

batch_time = time.perf_counter() - start

print(
    f"31 chunks embedding time : {batch_time:.4f} sec"
)
start = time.perf_counter()

embeddings = embedding_model.embed_documents(
    chunks
)

embedding_time = time.perf_counter() - start

print(
    f"Embedding Time : "
    f"{embedding_time:.4f} sec"
)

print(
    "Embedding Type :",
    type(embeddings)
)

print(
    "Embedding Shape :",
    embeddings.shape
)


# ============================================================
# 6. QUERY EMBEDDING
# ============================================================

print("\n" + "=" * 80)
print("6. QUERY EMBEDDING")
print("=" * 80)

query = "What factors affect the CIBIL score?"

start = time.perf_counter()

query_embedding = embedding_model.embed_query(
    query
)

query_embedding_time = (
    time.perf_counter() - start
)

print(
    f"Query : {query}"
)

print(
    f"Query Embedding Time : "
    f"{query_embedding_time:.4f} sec"
)

print(
    "Query Embedding Shape :",
    query_embedding.shape
)


# ============================================================
# 7. FINAL SUMMARY
# ============================================================

print("\n" + "=" * 80)
print("TIMING SUMMARY")
print("=" * 80)

print(
    f"Loading           : {loading_time:.4f} sec"
)

print(
    f"Parsing           : {parsing_time:.4f} sec"
)

print(
    f"Chunking          : {chunking_time:.4f} sec"
)

print(
    f"Model Loading     : {model_load_time:.4f} sec"
)

print(
    f"Document Embedding: {embedding_time:.4f} sec"
)

print(
    f"Query Embedding   : "
    f"{query_embedding_time:.4f} sec"
)