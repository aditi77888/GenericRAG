from pathlib import Path
import time

from models.chunk import Chunk
from embeddings.embedding_factory import EmbeddingFactory


chunks = [
    Chunk(
        content=f"""
        This is test document chunk number {i}.
        It contains some information about machine learning,
        artificial intelligence, retrieval augmented generation,
        and natural language processing.
        """,
        metadata={"chunk_id": i}
    )
    for i in range(31)
]


print("Loading bge...")

start = time.perf_counter()

embedding_model = EmbeddingFactory.create("bge-large")

load_time = time.perf_counter() - start

print(f"Model loading : {load_time:.3f} sec")


print("\nTesting 1 chunk...")

start = time.perf_counter()

result = embedding_model.embed_documents(
    chunks[:1]
)

single_time = time.perf_counter() - start

print(f"1 chunk : {single_time:.3f} sec")


print("\nTesting 31 chunks...")

start = time.perf_counter()

result = embedding_model.embed_documents(
    chunks
)

batch_time = time.perf_counter() - start

print(f"31 chunks : {batch_time:.3f} sec")

print("\nShape:", result.shape)