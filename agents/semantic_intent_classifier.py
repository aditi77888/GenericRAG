import numpy as np

from embeddings.embedding_singleton import get_embedding_model


class SemanticIntentClassifier:
    """
    Classifies a query into a small set of conversational
    intents (small_talk, thanks, goodbye) using local embedding
    similarity — NOT an LLM call, NOT a vector DB lookup.

    This exists to catch the "infinite phrasing" problem that a
    hardcoded keyword list can't scale to: "how are you?",
    "what's up?", "aap kaise ho?", "kaisa hai sab" all mean the
    same thing as far as routing is concerned, but none of them
    match a fixed phrase list.

    A `document_question` example set is included ONLY as a
    negative class, to stop conversational phrasing from being
    confused with real document questions. It is never returned
    as a classification result — actual document-question
    routing stays in SupervisorAgent's existing keyword/regex
    rules, which are already reliable and cheap.
    """

    EXAMPLES = {

        "small_talk": [
            "how are you",
            "how are you doing",
            "how are you doing today",
            "how's it going",
            "how's everything",
            "how's everything going",
            "what's up",
            "whats up",
            "what are you doing",
            "what's new",
            "how have you been",
            "you good?",
            "you doing okay?",
            "aap kaise ho",
            "aap kaise hain",
            "aap kese ho",
            "kaise ho",
            "kaisa hai",
            "kaisa hai tu",
            "kya haal hai",
            "sab thik",
            "kya chal raha hai",
            "kaise chal raha hai",
        ],

        "thanks": [
            "thanks",
            "thank you",
            "thanks a lot",
            "thanks a ton",
            "thank you so much",
            "really appreciate it",
            "i really appreciate the help",
            "you're a lifesaver",
            "appreciate the help",
            "dhanyavad",
            "bahut dhanyavad",
            "shukriya",
            "shukriya bhai",
        ],

        "goodbye": [
            "bye",
            "goodbye",
            "see you later",
            "see you soon",
            "talk to you later",
            "catch you later",
            "i'm leaving now",
            "gotta go",
            "i'm done for now",
            "alvida",
            "chalta hoon",
            "chalti hoon",
            "phir milte hain",
            "phir baat karte hain",
        ],

        # Negative class only — never returned by classify().
        "document_question": [
            "what is my roll number",
            "what does the pdf contain",
            "summarize the document",
            "what is written on page 2",
            "what are my skills",
            "tell me about the uploaded file",
            "what is the candidate's experience",
            "give me the contact details",
        ],
    }

    ROUTABLE_LABELS = {"small_talk", "thanks", "goodbye"}

    def __init__(
            self,
            embedding_model=None,
            threshold: float = 0.62,
            margin: float = 0.05
    ):
        """
        threshold: minimum similarity for a match to count at all.
        margin: how much higher the best routable score must be
                than the document_question score, so genuinely
                ambiguous queries don't get misrouted.

        These defaults are a reasonable starting point, NOT
        guaranteed-correct numbers — tune them by watching the
        "[SEMANTIC CLASSIFIER] scores:" log line against real
        queries from your users.
        """

        self.embedding_model = (
            embedding_model
            if embedding_model is not None
            else get_embedding_model()
        )

        self.threshold = threshold
        self.margin = margin

        self._example_embeddings = {}
        self._build_example_embeddings()

    def _build_example_embeddings(self):

        print(
            "[SEMANTIC CLASSIFIER] Precomputing example "
            "embeddings...",
            flush=True
        )

        for label, phrases in self.EXAMPLES.items():

            vectors = [
                np.asarray(
                    self.embedding_model.embed_query(phrase),
                    dtype=float
                )
                for phrase in phrases
            ]

            self._example_embeddings[label] = vectors

        print(
            "[SEMANTIC CLASSIFIER] Example embeddings ready.",
            flush=True
        )

    @staticmethod
    def _cosine_similarity(a, b):

        denom = (
            np.linalg.norm(a) * np.linalg.norm(b)
        )

        if denom == 0:
            return 0.0

        return float(
            np.dot(a, b) / denom
        )

    def classify(self, query: str):
        """
        Returns (label, score):
            label -> one of "small_talk", "thanks", "goodbye",
                     or None if nothing routable matched
                     confidently enough.
            score -> the best similarity score found (for logging).
        """

        if not query or not query.strip():
            return None, 0.0

        query_vector = np.asarray(
            self.embedding_model.embed_query(query),
            dtype=float
        )

        scores = {}

        for label, vectors in self._example_embeddings.items():

            best = max(
                self._cosine_similarity(query_vector, v)
                for v in vectors
            )

            scores[label] = best

        print(
            "[SEMANTIC CLASSIFIER] scores:",
            {k: round(v, 3) for k, v in scores.items()},
            flush=True
        )

        best_label = max(scores, key=scores.get)
        best_score = scores[best_label]

        if best_label not in self.ROUTABLE_LABELS:
            return None, best_score

        if best_score < self.threshold:
            return None, best_score

        doc_score = scores.get("document_question", 0.0)

        if best_score - doc_score < self.margin:
            return None, best_score

        return best_label, best_score


_CLASSIFIER = None


def get_intent_classifier():

    global _CLASSIFIER

    if _CLASSIFIER is None:
        _CLASSIFIER = SemanticIntentClassifier()

    return _CLASSIFIER