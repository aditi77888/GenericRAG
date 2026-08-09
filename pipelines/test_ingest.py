import time
from pathlib import Path

from chunkers.recursive_chunker import RecursiveChunker
from embeddings.embedding_factory import EmbeddingFactory
from llms.llm_factory import LLMFactory
from prompts.prompt_builder import PromptBuilder
from retriever.retriever_factory import RetrieverFactory
from vectorstore.vectorstore_factory import VectorStoreFactory

from pipelines.rag_pipeline import RAGPipeline


# ============================================================
# CONFIGURATION
# ============================================================

SOURCE = Path(
    r"C:\Users\Hp-Laptop\PycharmProjects\GenericRAG\files\cibil.pdf"
)
QUESTION = "What factors affect the CIBIL score?"
# ============================================================
# PATH CHECK
# ============================================================

print("=" * 80)
print("DOCUMENT INGESTION + RAG TEST")
print("=" * 80)

print("\nSource :", SOURCE)
print("Exists :", SOURCE.exists())


if not SOURCE.exists():
    raise FileNotFoundError(
        f"File not found: {SOURCE}"
    )


# ============================================================
# 1. CREATE CHUNKER
# ============================================================

print("\n" + "=" * 80)
print("1. CHUNKER")
print("=" * 80)

chunker = RecursiveChunker(
    chunk_size=500,
    chunk_overlap=50
)

print(
    "Chunker :",
    chunker.__class__.__name__
)


# ============================================================
# 2. CREATE EMBEDDING MODEL
# ============================================================

print("\n" + "=" * 80)
print("2. EMBEDDING MODEL")
print("=" * 80)

start = time.perf_counter()

embedding_model = EmbeddingFactory.create(
    "bge"
)

embedding_time = time.perf_counter() - start

print(
    "Embedding Model :",
    embedding_model.__class__.__name__
)

print(
    f"Creation Time   : {embedding_time:.3f} sec"
)


# ============================================================
# 3. CREATE VECTOR STORE
# ============================================================

print("\n" + "=" * 80)
print("3. VECTOR STORE")
print("=" * 80)

start = time.perf_counter()

vector_store = VectorStoreFactory.create(
    "pinecone"
)

vector_store_time = time.perf_counter() - start

print(
    "Vector Store :",
    vector_store.__class__.__name__
)

print(
    f"Creation Time : {vector_store_time:.3f} sec"
)


# ============================================================
# 4. CREATE RETRIEVER
# ============================================================

print("\n" + "=" * 80)
print("4. RETRIEVER")
print("=" * 80)

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
# 5. CREATE LLM
# ============================================================

print("\n" + "=" * 80)
print("5. LLM")
print("=" * 80)

start = time.perf_counter()

llm = LLMFactory.create(
    llm_name="gemini",
    model_name="gemini-3.6-flash"
)

llm_time = time.perf_counter() - start

print(
    "LLM :",
    llm.__class__.__name__
)

print(
    f"Creation Time : {llm_time:.3f} sec"
)


# ============================================================
# 6. CREATE PROMPT BUILDER
# ============================================================

print("\n" + "=" * 80)
print("6. PROMPT BUILDER")
print("=" * 80)

prompt_builder = PromptBuilder()

print(
    "Prompt Builder :",
    prompt_builder.__class__.__name__
)


# ============================================================
# 7. CREATE RAG PIPELINE
# ============================================================

print("\n" + "=" * 80)
print("7. RAG PIPELINE")
print("=" * 80)

rag = RAGPipeline(

    chunker=chunker,

    embedding_model=embedding_model,

    vector_store=vector_store,

    retriever=retriever,

    llm=llm,

    prompt_builder=prompt_builder
)

print(
    "RAG Pipeline :",
    rag.__class__.__name__
)


# ============================================================
# 8. INGEST DOCUMENT
# ============================================================

print("\n" + "=" * 80)
print("8. DOCUMENT INGESTION")
print("=" * 80)

print("\nUploading and indexing document...")

start = time.perf_counter()

document_id = rag.ingest(
    SOURCE
)

ingestion_time = time.perf_counter() - start

print(
    "\nDocument ID :",
    document_id
)

print(
    f"Ingestion Time : {ingestion_time:.3f} sec"
)


# ============================================================
# 9. ASK QUESTION
# ============================================================

print("\n" + "=" * 80)
print("9. QUESTION")
print("=" * 80)

print(
    "\nQuestion :",
    QUESTION
)

print("\nGenerating answer...")

start = time.perf_counter()

result = rag.ask(
    question=QUESTION,
    document_id=document_id,
    top_k=5
)

query_time = time.perf_counter() - start


# ============================================================
# 10. ANSWER
# ============================================================

print("\n" + "=" * 80)
print("10. ANSWER")
print("=" * 80)

print("\n" + result["answer"])


# ============================================================
# 11. SOURCES
# ============================================================

print("\n" + "=" * 80)
print("11. SOURCES")
print("=" * 80)

for source in result["sources"]:
    print(
        "-",
        source
    )


# ============================================================
# 12. RETRIEVED CHUNKS
# ============================================================

print("\n" + "=" * 80)
print("12. RETRIEVED CHUNKS")
print("=" * 80)

print(
    "\nChunks Retrieved :",
    len(result["chunks"])
)

for index, chunk in enumerate(
        result["chunks"],
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


# ============================================================
# 13. FINAL SUMMARY
# ============================================================

print("\n" + "=" * 80)
print("FINAL SUMMARY")
print("=" * 80)

print(
    "Document ID      :",
    document_id
)

print(
    "Chunks Retrieved :",
    len(result["chunks"])
)

print(
    f"Ingestion Time   : {ingestion_time:.3f} sec"
)

print(
    f"Query Time       : {query_time:.3f} sec"
)

print("\n" + "=" * 80)
print("DOCUMENT INGESTION TEST COMPLETE")
print("=" * 80)