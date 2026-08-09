import time
import traceback
from pathlib import Path

from loaders.loader_factory import LoaderFactory
from parsers.parser_factory import ParserFactory
from chunkers.recursive_chunker import RecursiveChunker


# ============================================================
# SOURCE
# ============================================================
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent

SOURCE = PROJECT_ROOT / "files" / "cibil.pdf"


# ============================================================
# HEADER
# ============================================================

print("=" * 80)
print("GENERIC RAG PIPELINE BENCHMARK")
print("=" * 80)

print(f"\nSource : {SOURCE}")
print(f"Exists : {SOURCE.exists()}")
print(f"Size   : {SOURCE.stat().st_size / 1024:.2f} KB")


# ============================================================
# TOTAL TIMER
# ============================================================

total_start = time.perf_counter()


# ============================================================
# 1. LOADER
# ============================================================

print("\n" + "=" * 80)
print("1. LOADER")
print("=" * 80)

loader_start = time.perf_counter()

try:

    loader = LoaderFactory.create(SOURCE)

    loader_selection_time = (
        time.perf_counter() - loader_start
    )

    print(
        f"Selected Loader : "
        f"{loader.__class__.__name__}"
    )

    print(
        f"Selection Time  : "
        f"{loader_selection_time:.4f} sec"
    )

except Exception:

    print("LOADER SELECTION FAILED")
    traceback.print_exc()
    raise


# ============================================================
# 2. LOADING
# ============================================================

print("\nLoading...")

loading_start = time.perf_counter()

try:

    loaded_data = loader.load(SOURCE)

    loading_time = (
        time.perf_counter() - loading_start
    )

    print(
        f"Loading Time    : "
        f"{loading_time:.4f} sec"
    )

    print(
        f"Output Type     : "
        f"{type(loaded_data)}"
    )

except Exception:

    print("LOADING FAILED")
    traceback.print_exc()
    raise


# ============================================================
# 3. PARSER
# ============================================================

print("\n" + "=" * 80)
print("2. PARSER")
print("=" * 80)

parser_start = time.perf_counter()

try:

    parser = ParserFactory.create(SOURCE)

    parser_selection_time = (
        time.perf_counter() - parser_start
    )

    print(
        f"Selected Parser : "
        f"{parser.__class__.__name__}"
    )

    print(
        f"Selection Time  : "
        f"{parser_selection_time:.4f} sec"
    )

except Exception:

    print("PARSER SELECTION FAILED")
    traceback.print_exc()
    raise


# ============================================================
# 4. PARSING
# ============================================================

print("\nParsing...")

parsing_start = time.perf_counter()

try:

    documents = parser.parse(loaded_data)

    parsing_time = (
        time.perf_counter() - parsing_start
    )

    print(
        f"Parsing Time    : "
        f"{parsing_time:.4f} sec"
    )

    print(
        f"Output Type     : "
        f"{type(documents)}"
    )

    print(
        f"Documents       : "
        f"{len(documents)}"
    )

except Exception:

    print("PARSING FAILED")
    traceback.print_exc()
    raise


# ============================================================
# 5. DOCUMENT SUMMARY
# ============================================================

print("\n" + "=" * 80)
print("3. DOCUMENT SUMMARY")
print("=" * 80)

total_characters = 0

for index, document in enumerate(
        documents,
        start=1
):

    content_length = len(document.content)

    total_characters += content_length

    print(
        f"Document {index:>3} : "
        f"{content_length:>6} characters"
    )

print(
    f"\nTotal Characters : "
    f"{total_characters}"
)


# ============================================================
# 6. CHUNKER
# ============================================================

print("\n" + "=" * 80)
print("4. CHUNKER")
print("=" * 80)

chunker_start = time.perf_counter()

try:

    chunker = RecursiveChunker(
        chunk_size=500,
        chunk_overlap=50
    )

    chunker_selection_time = (
        time.perf_counter() - chunker_start
    )

    print(
        f"Selected Chunker : "
        f"{chunker.__class__.__name__}"
    )

    print(
        f"Selection Time   : "
        f"{chunker_selection_time:.4f} sec"
    )

except Exception:

    print("CHUNKER CREATION FAILED")
    traceback.print_exc()
    raise


# ============================================================
# 7. CHUNKING
# ============================================================

print("\nChunking...")

chunking_start = time.perf_counter()

try:

    chunks = chunker.chunk(documents)

    chunking_time = (
        time.perf_counter() - chunking_start
    )

    print(
        f"Chunking Time    : "
        f"{chunking_time:.4f} sec"
    )

    print(
        f"Chunks Produced  : "
        f"{len(chunks)}"
    )

except Exception:

    print("CHUNKING FAILED")
    traceback.print_exc()
    raise


# ============================================================
# 8. CHUNK STATISTICS
# ============================================================

print("\n" + "=" * 80)
print("5. CHUNK STATISTICS")
print("=" * 80)

if chunks:

    chunk_lengths = [
        len(chunk.content)
        for chunk in chunks
    ]

    print(
        f"Minimum Chunk Size : "
        f"{min(chunk_lengths)}"
    )

    print(
        f"Maximum Chunk Size : "
        f"{max(chunk_lengths)}"
    )

    print(
        f"Average Chunk Size : "
        f"{sum(chunk_lengths) / len(chunk_lengths):.2f}"
    )


# ============================================================
# 9. SAMPLE CHUNKS
# ============================================================

print("\n" + "=" * 80)
print("6. SAMPLE CHUNKS")
print("=" * 80)

for index, chunk in enumerate(
        chunks[:5],
        start=1
):

    print(
        f"\nChunk {index}"
    )

    print("-" * 60)

    print(
        f"ID       : "
        f"{chunk.metadata.get('chunk_id')}"
    )

    print(
        f"Length   : "
        f"{len(chunk.content)}"
    )

    print(
        f"Metadata : "
        f"{chunk.metadata}"
    )

    print("\nContent:")

    print(chunk.content[:500])

    if len(chunk.content) > 500:
        print("...")


# ============================================================
# 10. TOTAL TIME
# ============================================================

total_time = (
    time.perf_counter() - total_start
)


print("\n" + "=" * 80)
print("7. TIMING SUMMARY")
print("=" * 80)

print(
    f"Loader Selection : "
    f"{loader_selection_time:.4f} sec"
)

print(
    f"Loading          : "
    f"{loading_time:.4f} sec"
)

print(
    f"Parser Selection : "
    f"{parser_selection_time:.4f} sec"
)

print(
    f"Parsing          : "
    f"{parsing_time:.4f} sec"
)

print(
    f"Chunker Creation : "
    f"{chunker_selection_time:.4f} sec"
)

print(
    f"Chunking         : "
    f"{chunking_time:.4f} sec"
)

print("-" * 80)

print(
    f"TOTAL            : "
    f"{total_time:.4f} sec"
)

print("=" * 80)

from chunkers.chunker_factory import ChunkerFactory


recursive = ChunkerFactory.create(
    "recursive",
    chunk_size=500,
    chunk_overlap=50
)

markdown = ChunkerFactory.create(
    "markdown",
    chunk_size=500,
    chunk_overlap=50
)


print(
    "Recursive:",
    recursive.__class__.__name__
)

print(
    "Markdown:",
    markdown.__class__.__name__
)