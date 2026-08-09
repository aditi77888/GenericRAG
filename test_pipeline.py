from loaders.loader_factory import LoaderFactory
from chunkers.recursive_chunker import RecursiveChunker
from embeddings.embedding_factory import EmbeddingFactory

loader = LoaderFactory.create("files/sample.pdf")

documents = loader.load("sample.pdf")

chunker = RecursiveChunker()

chunks = chunker.chunk(documents)

embedding_model = EmbeddingFactory.create("qwen")
embeddings = self.model.encode(
    texts,
    batch_size=32,
    show_progress_bar=True,
    convert_to_numpy=True,
    normalize_embeddings=True
)
vectors = embedding_model.embed_documents(chunks)

print(f"Documents : {len(documents)}")
print(f"Chunks    : {len(chunks)}")
print(f"Vectors   : {vectors.shape}")


"""from loaders.loader_factory import LoaderFactory
from chunkers.recursive_chunker import RecursiveChunker
from embeddings.embedding_factory import EmbeddingFactory

loader = LoaderFactory.create("sample.pdf")
documents = loader.load("sample.pdf")

chunker = RecursiveChunker(
    chunk_size=500,
    chunk_overlap=20
)

chunks = chunker.chunk(documents)

print("=" * 80)
print("CHUNKS")
print("=" * 80)

for i, chunk in enumerate(chunks, start=1):
    print(f"\nChunk {i}")
    print("-" * 80)
    print("Metadata:", chunk.metadata)
    print()
    print(chunk.content)

embedding_model = EmbeddingFactory.create("qwen")
vectors = embedding_model.embed_documents(chunks)

print("\n" + "=" * 80)
print("SUMMARY")
print("=" * 80)

print(f"Documents : {len(documents)}")
print(f"Chunks    : {len(chunks)}")
print(f"Vectors   : {vectors.shape}")"""