import time

from embeddings.embedding_factory import EmbeddingFactory
from llms.llm_factory import LLMFactory
from prompts.prompt_builder import PromptBuilder
from pipelines.rag_pipeline import RAGPipeline
from retriever.retriever_factory import RetrieverFactory
from vectorstore.vectorstore_factory import VectorStoreFactory


# ============================================================
# CONFIGURATION
# ============================================================

QUERY = "What factors affect the CIBIL score?"

NAMESPACE = "cibil_test"

TOP_K = 5


print("=" * 80)
print("END-TO-END RAG QUERY TEST")
print("=" * 80)

print("\nQuery     :", QUERY)
print("Namespace :", NAMESPACE)
print("Top K     :", TOP_K)


# ============================================================
# 1. EMBEDDING MODEL
# ============================================================

print("\n" + "=" * 80)
print("1. EMBEDDING MODEL")
print("=" * 80)

start = time.perf_counter()

embedding_model = EmbeddingFactory.create(
    "bge"
)

embedding_creation_time = (
    time.perf_counter() - start
)

print(
    "Selected Model :",
    embedding_model.__class__.__name__
)

print(
    f"Creation Time   : {embedding_creation_time:.4f} sec"
)


# ============================================================
# 2. VECTOR STORE
# ============================================================

print("\n" + "=" * 80)
print("2. VECTOR STORE")
print("=" * 80)

start = time.perf_counter()

vector_store = VectorStoreFactory.create(
    "pinecone"
)

vector_store_time = (
    time.perf_counter() - start
)

print(
    "Selected Store :",
    vector_store.__class__.__name__
)

print(
    f"Creation Time  : {vector_store_time:.4f} sec"
)


# ============================================================
# 3. RETRIEVER
# ============================================================

print("\n" + "=" * 80)
print("3. RETRIEVER")
print("=" * 80)

retriever = RetrieverFactory.create(
    retriever_name="vector",
    embedding_model=embedding_model,
    vector_store=vector_store
)

print(
    "Selected Retriever :",
    retriever.__class__.__name__
)


# ============================================================
# 4. LLM
# ============================================================

print("\n" + "=" * 80)
print("4. LLM")
print("=" * 80)

start = time.perf_counter()

llm = LLMFactory.create(
    llm_name="gemini",
    model_name="gemini-3.6-flash"
)

llm_creation_time = (
    time.perf_counter() - start
)

print(
    "Selected LLM :",
    llm.__class__.__name__
)

print(
    f"Creation Time : {llm_creation_time:.4f} sec"
)


# ============================================================
# 5. PROMPT BUILDER
# ============================================================

print("\n" + "=" * 80)
print("5. PROMPT BUILDER")
print("=" * 80)

prompt_builder = PromptBuilder()

print(
    "Selected Builder :",
    prompt_builder.__class__.__name__
)


# ============================================================
# 6. CREATE RAG PIPELINE
# ============================================================

rag = RAGPipeline(

    chunker=None,

    embedding_model=embedding_model,

    vector_store=vector_store,

    retriever=retriever,

    llm=llm,

    prompt_builder=prompt_builder
)

print(
    "\nRAG Pipeline :",
    rag.__class__.__name__
)


# ============================================================
# 7. RETRIEVE
# ============================================================

print("\n" + "=" * 80)
print("6. RETRIEVAL")
print("=" * 80)

start = time.perf_counter()

chunks = retriever.retrieve(
    query=QUERY,
    top_k=TOP_K,
    namespace=NAMESPACE
)

retrieval_time = (
    time.perf_counter() - start
)

print(
    f"Retrieval Time : {retrieval_time:.4f} sec"
)

print(
    "Chunks Retrieved :",
    len(chunks)
)


# ============================================================
# DISPLAY RETRIEVED CHUNKS
# ============================================================

for index, chunk in enumerate(
        chunks,
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

    print("\nContent:")

    print(
        chunk.content[:400]
    )


# ============================================================
# 8. BUILD PROMPT
# ============================================================

print("\n" + "=" * 80)
print("7. PROMPT BUILDING")
print("=" * 80)

start = time.perf_counter()

prompt = prompt_builder.build(
    question=QUERY,
    chunks=chunks
)

prompt_time = (
    time.perf_counter() - start
)

print(
    f"Prompt Building Time : {prompt_time:.4f} sec"
)

print(
    "Prompt Length :",
    len(prompt),
    "characters"
)


# ============================================================
# 9. LLM GENERATION
# ============================================================

print("\n" + "=" * 80)
print("8. LLM GENERATION")
print("=" * 80)

start = time.perf_counter()

answer = llm.generate(
    prompt=prompt,
    temperature=0,
    max_tokens=1500
)

generation_time = (
    time.perf_counter() - start
)

print(
    f"Generation Time : {generation_time:.4f} sec"
)


# ============================================================
# 10. SOURCES
# ============================================================

sources = []

for chunk in chunks:

    metadata = chunk.metadata

    source = (
        f"{metadata.get('source', 'Unknown source')}"
        f" (Page {metadata.get('page', '-')})"
    )

    if source not in sources:
        sources.append(source)


# ============================================================
# FINAL ANSWER
# ============================================================

print("\n" + "=" * 80)
print("FINAL RAG ANSWER")
print("=" * 80)

print("\nANSWER REPR:")
print(repr(answer))

print("\nANSWER LENGTH:")
print(len(answer))

print("\nANSWER:")
print(answer)


# ============================================================
# SOURCES
# ============================================================

print("\n" + "=" * 80)
print("SOURCES")
print("=" * 80)

for source in sources:
    print(
        "-",
        source
    )




# ============================================================
# TIMING
# ============================================================

total_query_time = (
    retrieval_time
    + prompt_time
    + generation_time
)

print("\n" + "=" * 80)
print("TIMING SUMMARY")
print("=" * 80)

print(
    f"Retrieval          : {retrieval_time:.4f} sec"
)

print(
    f"Prompt Building    : {prompt_time:.4f} sec"
)

print(
    f"LLM Generation     : {generation_time:.4f} sec"
)

print(
    f"Total Query Time   : {total_query_time:.4f} sec"
)

print("\n" + "=" * 80)
print("RAG TEST COMPLETE")
print("=" * 80)