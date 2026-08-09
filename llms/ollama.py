import time

from llms.llm_factory import LLMFactory


# ============================================================
# TEST CONFIGURATION
# ============================================================

PROMPT = """
You are a helpful assistant.

Answer the following question in one short paragraph.

Question:
What is Retrieval-Augmented Generation (RAG)?
"""


# ============================================================
# TEST GEMINI
# ============================================================

print("=" * 80)
print("LLM TEST")
print("=" * 80)

print("\nCreating Gemini LLM...")

start = time.perf_counter()

llm = LLMFactory.create(
    llm_name="gemini",
    model_name="gemini-3.6-flash"
)

creation_time = time.perf_counter() - start

print(
    f"LLM Creation Time : {creation_time:.4f} sec"
)

print(
    "Selected LLM      :",
    llm.__class__.__name__
)


# ============================================================
# GENERATE
# ============================================================

print("\nGenerating response...")

start = time.perf_counter()

response = llm.generate(
    prompt=PROMPT,
    temperature=0,
    max_tokens=300
)

generation_time = time.perf_counter() - start


# ============================================================
# OUTPUT
# ============================================================

print("\n" + "=" * 80)
print("RESPONSE")
print("=" * 80)

print(response)

print("\n" + "=" * 80)
print("TIMING")
print("=" * 80)

print(
    f"LLM Creation : {creation_time:.4f} sec"
)

print(
    f"Generation   : {generation_time:.4f} sec"
)

print("\nLLM TEST COMPLETE")