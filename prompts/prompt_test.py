from models.chunk import Chunk
from prompts.prompt_builder import PromptBuilder


# ============================================================
# TEST CHUNKS
# ============================================================

chunks = [

    Chunk(
        content="""
        CREDIT UTILISATION refers to the amount of available
        credit being used. Higher credit utilisation may indicate
        higher credit risk.
        """,
        metadata={
            "page": 1,
            "chunk_id": 0
        }
    ),

    Chunk(
        content="""
        PAYMENT HISTORY is one of the factors considered when
        determining creditworthiness. Late or missed payments
        can negatively affect the CIBIL Score.
        """,
        metadata={
            "page": 1,
            "chunk_id": 1
        }
    ),

    Chunk(
        content="""
        AGE OF CREDIT refers to the length of time credit accounts
        have been held. A longer credit history can indicate
        stability and reliability.
        """,
        metadata={
            "page": 1,
            "chunk_id": 2
        }
    )
]


# ============================================================
# QUESTION
# ============================================================

question = "What factors affect the CIBIL score?"


# ============================================================
# BUILD PROMPT
# ============================================================

builder = PromptBuilder()

prompt = builder.build(
    question=question,
    chunks=chunks
)


# ============================================================
# OUTPUT
# ============================================================

print("=" * 80)
print("PROMPT BUILDER TEST")
print("=" * 80)

print("\nQuestion:")
print(question)

print("\nGenerated Prompt:")
print("-" * 80)

print(prompt)

print("\n" + "=" * 80)
print("PROMPT BUILDER TEST COMPLETE")
print("=" * 80)