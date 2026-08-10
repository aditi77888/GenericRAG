import re
import json

from agents.base_agent import BaseAgent
from agents.semantic_intent_classifier import get_intent_classifier
from llms.llm_factory import LLMFactory


class SupervisorAgent(BaseAgent):

    def __init__(self):

        self.llm = LLMFactory.create(
            llm_name="fallback"
        )

        self.intent_classifier = get_intent_classifier()

    # =====================================================
    # MAIN HANDLER
    # =====================================================

    def handle(self, query: str) -> dict:

        query = query.strip()

        if not query:
            return {
                "agent": "greeting",
                "intent": "greeting",
                "language": "english"
            }

        local_route = self._local_route(query)

        if local_route is not None:

            print(
                "[SUPERVISOR] Local route:",
                local_route,
                flush=True
            )

            return local_route

        print(
            "[SUPERVISOR] Ambiguous query -> LLM fallback",
            flush=True
        )

        prompt = self._build_prompt(query)

        try:

            response = self.llm.generate(prompt)

            print(
                "\nRAW SUPERVISOR LLM RESPONSE:",
                response,
                flush=True
            )

            return self._parse_response(response)

        except Exception as e:

            print(
                "[SUPERVISOR] LLM routing failed:",
                repr(e),
                flush=True
            )

            # IMPORTANT:
            # Never default an unknown query to RAG.
            # That can cause hallucinated/out-of-context answers.

            return {
                "agent": "blocked",
                "intent": "out_of_scope",
                "language": "english"
            }

    # =====================================================
    # LOCAL ROUTING
    # =====================================================

    def _local_route(self, query: str):

        normalized = query.lower().strip()

        language = self._detect_language(
            normalized
        )

        # =================================================
        # TIER 1 — CLEAR DOCUMENT REFERENCES
        # =================================================

        document_terms = {
            "pdf",
            "document",
            "resume",
            "cv",
            "file",
            "uploaded",
            "report",
            "paper",
            "this pdf",
            "this document",
            "the pdf",
            "the document",
            "uploaded pdf",
            "uploaded document",
        }

        if any(
            term in normalized
            for term in document_terms
        ):

            return {
                "agent": "rag",
                "intent": "document_question",
                "language": language
            }

        # =================================================
        # TIER 2 — CLEAR DOCUMENT INFORMATION QUESTIONS
        # =================================================

        document_question_patterns = [

            r"\bskills?\b",
            r"\bskillset\b",
            r"\btechnologies\b",
            r"\btechnical skills?\b",

            r"\beducation\b",
            r"\beducational background\b",
            r"\bqualification\b",
            r"\bqualifications\b",
            r"\bdegree\b",
            r"\bcollege\b",
            r"\buniversity\b",
            r"\bschool\b",

            r"\bwork experience\b",
            r"\bprofessional experience\b",
            r"\binternship\b",
            r"\binternships\b",
            r"\bprojects?\b",
            r"\bproject experience\b",

            r"\broll number\b",
            r"\broll no\b",
            r"\brollno\b",

            r"\bemail\b",
            r"\bphone number\b",
            r"\bcontact\b",
            r"\baddress\b",

            r"\bachievements?\b",
            r"\bcertifications?\b",

        ]

        if any(
            re.search(
                pattern,
                normalized
            )
            for pattern in document_question_patterns
        ):

            return {
                "agent": "rag",
                "intent": "document_question",
                "language": language
            }

        # =================================================
        # TIER 3 — DOCUMENT SUMMARY
        # =================================================

        summary_patterns = [

            r"what is this about",
            r"what's this about",
            r"what does this contain",
            r"what is it about",

            r"tell me about this",
            r"tell me about the document",
            r"tell me about the pdf",

            r"summarize this",
            r"summarise this",
            r"summary of this",
            r"give me a summary",

        ]

        if any(
            re.search(
                pattern,
                normalized
            )
            for pattern in summary_patterns
        ):

            return {
                "agent": "rag",
                "intent": "document_summary",
                "language": language
            }

        # =================================================
        # TIER 4 — OBVIOUS GENERAL KNOWLEDGE / OUT OF SCOPE
        #
        # These MUST NOT reach Pinecone.
        # =================================================

        out_of_scope_patterns = [

            # ---------------------------------------------
            # Person / entity knowledge
            # ---------------------------------------------

            r"^who is\b",
            r"^who was\b",
            r"^who are\b",

            r"^do you know\b",
            r"^do you know about\b",

            r"^tell me about\b",

            # ---------------------------------------------
            # General knowledge
            # ---------------------------------------------

            r"^what is\b",
            r"^what are\b",
            r"^what was\b",
            r"^what were\b",

            r"^explain\b",
            r"^define\b",

            r"^meaning of\b",
            r"^what does .* mean\b",

            r"^how does .* work\b",
            r"^how do .* work\b",

            # ---------------------------------------------
            # External/current information
            # ---------------------------------------------

            r"\btoday\b",
            r"\blatest\b",
            r"\bnews\b",
            r"\bweather\b",
            r"\bcurrent\b",
            r"\brecent\b",

        ]

        if any(
            re.search(
                pattern,
                normalized
            )
            for pattern in out_of_scope_patterns
        ):

            return {
                "agent": "blocked",
                "intent": "out_of_scope",
                "language": language
            }

        # =================================================
        # TIER 5 — SEMANTIC CLASSIFIER
        # =================================================

        semantic_label, semantic_score = (
            self.intent_classifier.classify(
                normalized
            )
        )

        if semantic_label is not None:

            print(
                f"[SUPERVISOR] Semantic route: "
                f"{semantic_label} "
                f"(score={semantic_score:.3f})",
                flush=True
            )

            if semantic_label == "document_question":

                return {
                    "agent": "rag",
                    "intent": "document_question",
                    "language": language
                }

            return {
                "agent": "greeting",
                "intent": semantic_label,
                "language": language
            }

        # =================================================
        # TIER 6 — UNKNOWN
        # =================================================

        return None

    # =====================================================
    # LANGUAGE DETECTION
    # =====================================================

    @staticmethod
    def _detect_language(query: str) -> str:

        query = query.lower().strip()

        if re.search(
            r"[\u0900-\u097F]",
            query
        ):
            return "hindi"

        hinglish_words = {
            "kya",
            "kaise",
            "kaisa",
            "kyu",
            "kyon",
            "kyunki",
            "hai",
            "hain",
            "haan",
            "nahi",
            "nhi",
            "aap",
            "aapka",
            "aapki",
            "apka",
            "apki",
            "mera",
            "meri",
            "mere",
            "mujhe",
            "mujhko",
            "batao",
            "bataiye",
            "chahiye",
            "karna",
            "karo",
            "karen",
            "kaun",
            "kab",
            "kahan",
            "kaha",
            "iska",
            "iske",
            "uska",
            "uske",
            "se",
            "ke",
            "ki",
            "ko",
            "mein",
            "me",
        }

        words = set(
            re.findall(
                r"\b[a-zA-Z]+\b",
                query
            )
        )

        hindi_matches = words.intersection(
            hinglish_words
        )

        if hindi_matches:
            return "hinglish"

        return "english"

    # =====================================================
    # SUPERVISOR LLM PROMPT
    # =====================================================

    @staticmethod
    def _build_prompt(query: str) -> str:

        return f"""
You are the Supervisor Agent of a strict document-grounded
Agentic RAG system.

Your job is ONLY to classify the user's query.

You MUST choose exactly one of these three routes:

1. greeting

Use "greeting" for conversational requests that do not
require information from an uploaded document.

Examples:

- hi
- hello
- how are you?
- how can you help me?
- what can you do?
- thanks
- thank you
- bye
- casual conversation

2. rag

Use "rag" ONLY when the user is asking for information
that should come from an uploaded PDF or document.

Examples:

- What skills are mentioned in the resume?
- What is the candidate's education?
- Summarize this PDF.
- What projects are mentioned in the uploaded document?
- What is the email address in the resume?

3. blocked

Use "blocked" when the user asks a general-knowledge,
external-knowledge, current-information, or unrelated
question that cannot be answered from an uploaded document.

Examples:

- Who is Rahul Gandhi?
- Who is Virat Kohli?
- What is Python?
- Explain machine learning.
- What is the capital of India?
- What is today's weather?
- What happened today?
- Tell me the latest news.

IMPORTANT:

A question about a person, technology, concept, country,
event, or general fact is NOT a RAG question unless the
user explicitly asks for information about that subject
FROM THE UPLOADED DOCUMENT.

For example:

"Who is Rahul Gandhi?"
=> blocked

"What does the uploaded PDF say about Rahul Gandhi?"
=> rag

"Who is the candidate mentioned in the resume?"
=> rag

Do NOT answer the user's question.

Return ONLY valid JSON.

Format:

{{
    "agent": "greeting" or "rag" or "blocked",
    "intent": "...",
    "language": "english" or "hindi" or "hinglish"
}}

Language rules:

- English -> english
- Hindi written in Devanagari -> hindi
- Hindi written using English characters -> hinglish

User query:

{query}
"""

    # =====================================================
    # PARSE SUPERVISOR RESPONSE
    # =====================================================

    @staticmethod
    def _parse_response(response: str) -> dict:

        try:

            cleaned = response.strip()

            if cleaned.startswith("```json"):
                cleaned = cleaned[7:]

            elif cleaned.startswith("```"):
                cleaned = cleaned[3:]

            if cleaned.endswith("```"):
                cleaned = cleaned[:-3]

            cleaned = cleaned.strip()

            result = json.loads(cleaned)

            if result.get("agent") not in {
                "greeting",
                "rag",
                "blocked"
            }:

                raise ValueError(
                    "Invalid agent returned."
                )

            if result.get("language") not in {
                "english",
                "hindi",
                "hinglish"
            }:

                result["language"] = "english"

            return result

        except Exception as e:

            print(
                "[SUPERVISOR] Failed to parse "
                "LLM response:",
                e,
                flush=True
            )

            # SAFETY DEFAULT:
            # Unknown queries must NEVER go to RAG.

            return {
                "agent": "blocked",
                "intent": "out_of_scope",
                "language": "english"
            }