import time
from pathlib import Path

from chunkers.recursive_chunker import RecursiveChunker
from embeddings.embedding_factory import EmbeddingFactory
from llms.llm_factory import LLMFactory
from prompts.prompt_builder import PromptBuilder
from pipelines.rag_pipeline import RAGPipeline
from retriever.retriever_factory import RetrieverFactory
from vectorstore.vectorstore_factory import VectorStoreFactory


# ============================================================
# CONFIG
# ============================================================

#PROJECT_ROOT = Path(__file__).resolve().parents[2]
SOURCE = Path(
    r"C:\Users\Hp-Laptop\PycharmProjects\GenericRAG\files\cibil.pdf"
)

#SOURCE = PROJECT_ROOT / "files" / "cibil.pdf"

NAMESPACE = "cibil_final_test"

QUESTION = "What factors affect the CIBIL score?"


# ============================================================
# CREATE COMPONENTS
# ============================================================

print("=" * 80)
print("FULL RAG PIPELINE TEST")
print("=" * 80)

print("\nSource :", SOURCE)
print("Exists :", SOURCE.exists())
print("Namespace :", NAMESPACE)


chunker = RecursiveChunker(
    chunk_size=500,
    chunk_overlap=50
)

embedding_model = EmbeddingFactory.create(
    "bge"
)

vector_store = VectorStoreFactory.create(
    "pinecone"
)

retriever = RetrieverFactory.create(
    retriever_name="vector",
    embedding_model=embedding_model,
    vector_store=vector_store
)

llm = LLMFactory.create(
    llm_name="gemini",
    model_name="gemini-3.6-flash"
)

prompt_builder = PromptBuilder()


rag = RAGPipeline(
    chunker=chunker,
    embedding_model=embedding_model,
    vector_store=vector_store,
    retriever=retriever,
    llm=llm,
    prompt_builder=prompt_builder
)


# ============================================================
# INDEX
# ============================================================

print("\n" + "=" * 80)
print("1. INDEXING DOCUMENT")
print("=" * 80)

start = time.perf_counter()

chunks_indexed = rag.index_document(
    source=SOURCE,
    namespace=NAMESPACE
)

indexing_time = time.perf_counter() - start

print("\nChunks Indexed :", chunks_indexed)
print(f"Indexing Time  : {indexing_time:.3f} sec")


# ============================================================
# ASK
# ============================================================

print("\n" + "=" * 80)
print("2. QUERY")
print("=" * 80)

print("\nQuestion :", QUESTION)

start = time.perf_counter()

result = rag.ask(
    question=QUESTION,
    namespace=NAMESPACE,
    top_k=5
)

query_time = time.perf_counter() - start


# ============================================================
# ANSWER
# ============================================================

print("\n" + "=" * 80)
print("3. ANSWER")
print("=" * 80)

print("\n", result["answer"])


# ============================================================
# SOURCES
# ============================================================

print("\n" + "=" * 80)
print("4. SOURCES")
print("=" * 80)

for source in result["sources"]:
    print("-", source)


# ============================================================
# SUMMARY
# ============================================================

print("\n" + "=" * 80)
print("5. SUMMARY")
print("=" * 80)

print("Chunks Indexed :", chunks_indexed)
print("Sources Used   :", len(result["sources"]))
print(f"Indexing Time  : {indexing_time:.3f} sec")
print(f"Query Time     : {query_time:.3f} sec")

print("\n" + "=" * 80)
print("FULL RAG TEST COMPLETE")
print("=" * 80)