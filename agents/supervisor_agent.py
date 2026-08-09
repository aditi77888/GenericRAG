import re
import json

from agents.base_agent import BaseAgent
from llms.llm_factory import LLMFactory


class SupervisorAgent(BaseAgent):

    def __init__(self):

        # Gemini is ONLY a fallback for genuinely ambiguous queries.
        self.llm = LLMFactory.create(
            llm_name="gemini",
            model_name="gemini-3.6-flash"
        )

    # =========================================================
    # MAIN
    # =========================================================

    def handle(self, query: str) -> dict:

        query = query.strip()

        if not query:
            return {
                "agent": "greeting",
                "intent": "greeting",
                "language": "english"
            }

        # -----------------------------------------------------
        # 1. LOCAL ROUTING
        # -----------------------------------------------------

        local_route = self._local_route(query)

        if local_route is not None:
            print(
                "[SUPERVISOR] Local route:",
                local_route,
                flush=True
            )
            return local_route

        # -----------------------------------------------------
        # 2. GEMINI FALLBACK
        #
        # ONLY genuinely ambiguous queries reach here.
        # -----------------------------------------------------

        print(
            "[SUPERVISOR] Ambiguous query -> Gemini fallback",
            flush=True
        )

        prompt = self._build_prompt(query)

        response = self.llm.generate(prompt)

        print(
            "\nRAW GEMINI RESPONSE:",
            response,
            flush=True
        )

        return self._parse_response(response)

    # =========================================================
    # LOCAL ROUTING
    # =========================================================

    def _local_route(self, query: str):

        normalized = query.lower().strip()

        # =====================================================
        # LANGUAGE
        # =====================================================

        language = self._detect_language(normalized)

        # =====================================================
        # GREETINGS
        # =====================================================

        greeting_words = {
            "hi",
            "hello",
            "hey",
            "hii",
            "hiii",
            "namaste",
            "namaskar",
            "pranam",
            "नमस्ते",
            "नमस्कार",
            "प्रणाम",
        }

        if normalized in greeting_words:

            return {
                "agent": "greeting",
                "intent": "greeting",
                "language": language
            }

        # =====================================================
        # THANKS
        # =====================================================

        thanks_words = {
            "thanks",
            "thank you",
            "thankyou",
            "thanks a lot",
            "thank you so much",
            "धन्यवाद",
            "शुक्रिया",
        }

        if normalized in thanks_words:

            return {
                "agent": "greeting",
                "intent": "thanks",
                "language": language
            }

        # =====================================================
        # GOODBYE
        # =====================================================

        goodbye_words = {
            "bye",
            "goodbye",
            "good bye",
            "see you",
            "see you later",
            "अलविदा",
        }

        if normalized in goodbye_words:

            return {
                "agent": "greeting",
                "intent": "goodbye",
                "language": language
            }

        # =====================================================
        # OBVIOUS DOCUMENT QUESTIONS
        # =====================================================

        # -----------------------------------------------------
        # Explicit document words
        # -----------------------------------------------------

        document_terms = {
            "pdf",
            "document",
            "resume",
            "cv",
            "file",
            "uploaded",
            "document",
            "report",
            "paper",
            "this pdf",
            "this document",
            "the pdf",
            "the document",
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

        # -----------------------------------------------------
        # Common information requests
        #
        # These are extremely common RAG questions.
        # -----------------------------------------------------

        document_question_patterns = [

            # skills
            r"\bskills?\b",
            r"\bskillset\b",
            r"\btechnologies\b",
            r"\btechnical skills?\b",

            # education
            r"\beducation\b",
            r"\beducational background\b",
            r"\bqualification\b",
            r"\bqualifications\b",
            r"\bdegree\b",
            r"\bcollege\b",
            r"\buniversity\b",
            r"\bschool\b",

            # experience
            r"\bexperience\b",
            r"\bwork experience\b",
            r"\bprofessional experience\b",
            r"\binternship\b",
            r"\binternships\b",
            r"\bprojects?\b",
            r"\bproject experience\b",

            # personal/document fields
            r"\broll number\b",
            r"\broll no\b",
            r"\brollno\b",
            r"\bname of\b",
            r"\bemail\b",
            r"\bphone number\b",
            r"\bcontact\b",
            r"\baddress\b",

            # resume information
            r"\bprofile\b",
            r"\bsummary\b",
            r"\bobjective\b",
            r"\bachievements?\b",
            r"\bcertifications?\b",
            r"\blanguages?\b",

            # retrieval verbs
            r"\bfetch\b",
            r"\bfethc\b",
            r"\bfind\b",
            r"\bextract\b",
            r"\bget\b",
            r"\bshow\b",
            r"\btell me\b",
            r"\bgive me\b",
        ]

        if any(
            re.search(pattern, normalized)
            for pattern in document_question_patterns
        ):

            return {
                "agent": "rag",
                "intent": "document_question",
                "language": language
            }

        # -----------------------------------------------------
        # Broad document summary questions
        # -----------------------------------------------------

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
            re.search(pattern, normalized)
            for pattern in summary_patterns
        ):

            return {
                "agent": "rag",
                "intent": "document_summary",
                "language": language
            }

        # =====================================================
        # NOT OBVIOUS
        # =====================================================

        return None

    # =========================================================
    # LANGUAGE DETECTION
    # =========================================================

    @staticmethod
    def _detect_language(query: str) -> str:

        query = query.lower().strip()

        # -----------------------------------------------------
        # Hindi script
        # -----------------------------------------------------

        if re.search(
            r"[\u0900-\u097F]",
            query
        ):
            return "hindi"

        # -----------------------------------------------------
        # Strong Hindi / Hinglish indicators
        # -----------------------------------------------------

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

        # Require at least one strong Hindi indicator.
        if hindi_matches:

            return "hinglish"

        # -----------------------------------------------------
        # Default
        # -----------------------------------------------------

        return "english"

    # =========================================================
    # GEMINI PROMPT
    # =========================================================

    @staticmethod
    def _build_prompt(query: str) -> str:

        return f"""
You are the Supervisor Agent of a generic Agentic RAG system.

Classify the user's query.

Available agents:

1. greeting
   - greetings
   - thanks
   - goodbye

2. rag
   - questions about an uploaded document
   - questions that require retrieving information
     from an uploaded PDF/document/resume

Return ONLY valid JSON.

Format:

{{
    "agent": "greeting" or "rag",
    "intent": "...",
    "language": "english", "hindi", or "hinglish"
}}

Important:

- Do NOT answer the question.
- Do NOT use outside knowledge.
- If the query asks for information from an uploaded
  document, choose "rag".
- Identify the language based on the actual language
  of the query.
- English queries must be classified as "english".
- Hindi written in Devanagari must be "hindi".
- Hindi written using English characters must be "hinglish".

User query:

{query}
"""

    # =========================================================
    # PARSE RESPONSE
    # =========================================================

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
                "rag"
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
                "[SUPERVISOR] Failed to parse LLM response:",
                e,
                flush=True
            )

            return {
                "agent": "rag",
                "intent": "document_question",
                "language": "english"
            }