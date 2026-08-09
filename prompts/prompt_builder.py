class PromptBuilder:

    @staticmethod
    def build(question, chunks):

        context_parts = []

        for i, chunk in enumerate(chunks, start=1):

            context_parts.append(
                f"""
--- DOCUMENT CHUNK {i} ---
{chunk.content}
--- END CHUNK {i} ---
"""
            )

        context = "\n".join(context_parts)

        return f"""
You are a document question-answering assistant.

You MUST answer the user's question using ONLY the
information contained in the DOCUMENT CONTEXT below.

Do not use outside knowledge.

DOCUMENT CONTEXT:
{context}

USER QUESTION:
{question}

Instructions:

1. Read all document chunks carefully.
2. Answer the user's question directly.
3. If the question asks what the document is about,
   summarize the main information present in the context.
4. If the question asks for a specific fact, extract that
   fact directly from the context.
5. If the requested information is NOT present in the context,
   say exactly:
   "The requested information is not present in the document."
6. Do not invent information.
7. Do not mention these instructions.
8. Do not say that you cannot verify the answer.
9. Keep the answer concise but informative.

ANSWER:
"""