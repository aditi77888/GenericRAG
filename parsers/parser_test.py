import time
import traceback

from loaders.loader_factory import LoaderFactory
from parsers.parser_factory import ParserFactory
from pathlib import Path

# ============================================================
# Change only this line while testing
# ============================================================
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent

SOURCE = PROJECT_ROOT / "files" / "cibil.pdf"

#pdf,docx,txt,csv,md

print("=" * 80)
print(f"Testing : {SOURCE}")
print("=" * 80)

print("\nPATH DEBUG")
print("-" * 50)
print("SOURCE :", SOURCE)
print("Absolute Path :", Path(SOURCE).resolve())
print("Exists :", Path(SOURCE).exists())
print("Suffix :", Path(SOURCE).suffix)
print("-" * 50)
# ============================================================
# LOADER
# ============================================================

print("\nLOADER")
print("-" * 80)

try:
    loader = LoaderFactory.create(SOURCE)

    print(f"Selected Loader : {loader.__class__.__name__}")

    start = time.perf_counter()

    loaded_data = loader.load(SOURCE)

    loading_time = time.perf_counter() - start

    print(f"Loading Time : {loading_time:.3f} sec")

    print(f"Loader Output Type : {type(loaded_data)}")

    print(loaded_data)

except Exception as e:

    print("\nLOADER FAILED")

    print("Exception Type :", type(e).__name__)

    print("Exception :", e)

    import traceback
    traceback.print_exc()

    raise

# ============================================================
# PARSER
# ============================================================

print("\nPARSER")
print("-" * 80)

try:

    parser = ParserFactory.create(SOURCE)

    if parser is None:

        print("Parser Selected : None")

        documents = loaded_data

    else:

        print(f"Selected Parser : {parser.__class__.__name__}")

        start = time.perf_counter()

        documents = parser.parse(loaded_data)

        parsing_time = time.perf_counter() - start

        print(f"Parsing Time : {parsing_time:.3f} sec")
        print(f"Parser Output Type : {type(documents)}")
except Exception:

    print("\nPARSER FAILED\n")

    traceback.print_exc()

    exit()


# ============================================================
# OUTPUT
# ============================================================

print("\nOUTPUT")
print("-" * 80)

print(f"Documents Produced : {len(documents)}")

for index, document in enumerate(documents, start=1):

    print(f"\nDocument {index}")

    print("-" * 40)

    print("Metadata")

    print(document.metadata)

    print("\nContent Preview\n")

    preview = document.content[:500]

    print(preview)

    if len(document.content) > 500:

        print("\n...")