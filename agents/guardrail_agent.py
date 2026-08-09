import re

from agents.base_agent import BaseAgent


class GuardrailAgent(BaseAgent):

    def __init__(self):
        pass

    # =========================================================
    # MAIN
    # =========================================================

    def handle(self, query: str) -> dict:

        # -----------------------------------------------------
        # Validate input
        # -----------------------------------------------------

        if query is None or not query.strip():

            return {
                "allowed": False,
                "category": "invalid_input",
                "reason": "The user query is empty.",
                "agent": "guardrail"
            }

        query = query.strip()

        # -----------------------------------------------------
        # Prompt Injection
        # -----------------------------------------------------

        prompt_injection_patterns = [

            r"ignore\s+(all\s+)?previous\s+instructions",

            r"ignore\s+(all\s+)?prior\s+instructions",

            r"forget\s+(all\s+)?previous\s+instructions",

            r"forget\s+(all\s+)?your\s+instructions",

            r"override\s+(your\s+)?instructions",

            r"disregard\s+(all\s+)?previous\s+instructions",

            r"bypass\s+(your\s+)?instructions",

        ]

        if self._matches(
            query,
            prompt_injection_patterns
        ):

            return {
                "allowed": False,
                "category": "prompt_injection",
                "reason": (
                    "The query attempts to override "
                    "system instructions."
                ),
                "agent": "guardrail"
            }

        # -----------------------------------------------------
        # Jailbreak
        # -----------------------------------------------------

        jailbreak_patterns = [

            r"pretend\s+(you\s+are|to\s+be)\s+unrestricted",

            r"act\s+as\s+(an?\s+)?unrestricted",

            r"act\s+as\s+if\s+you\s+have\s+no\s+rules",

            r"disable\s+(your\s+)?safety",

            r"remove\s+(your\s+)?restrictions",

            r"bypass\s+(your\s+)?safety",

            r"developer\s+mode",

            r"dan\s+mode",

        ]

        if self._matches(
            query,
            jailbreak_patterns
        ):

            return {
                "allowed": False,
                "category": "jailbreak",
                "reason": (
                    "The query attempts to bypass "
                    "system restrictions."
                ),
                "agent": "guardrail"
            }

        # -----------------------------------------------------
        # Internal Information
        # -----------------------------------------------------

        internal_information_patterns = [

            r"show\s+(me\s+)?your\s+system\s+prompt",

            r"what\s+is\s+your\s+system\s+prompt",

            r"give\s+me\s+your\s+system\s+prompt",

            r"reveal\s+(your\s+)?system\s+prompt",

            r"show\s+(me\s+)?your\s+instructions",

            r"what\s+are\s+your\s+instructions",

            r"show\s+(me\s+)?your\s+api\s+key",

            r"give\s+(me\s+)?your\s+api\s+key",

            r"show\s+(me\s+)?your\s+credentials",

            r"give\s+(me\s+)?your\s+credentials",

            r"show\s+(me\s+)?your\s+secret",

            r"tell\s+me\s+your\s+secret",

        ]

        if self._matches(
            query,
            internal_information_patterns
        ):

            return {
                "allowed": False,
                "category": "internal_information",
                "reason": (
                    "The query requests protected "
                    "internal information."
                ),
                "agent": "guardrail"
            }

        # -----------------------------------------------------
        # Unsafe / Harmful
        # -----------------------------------------------------

        unsafe_patterns = [

            r"how\s+can\s+i\s+hack",

            r"how\s+to\s+hack",

            r"how\s+can\s+i\s+steal\s+(someone'?s\s+)?password",

            r"how\s+to\s+steal\s+(someone'?s\s+)?password",

            r"how\s+can\s+i\s+break\s+into\s+(someone'?s\s+)?account",

            r"how\s+to\s+break\s+into\s+(someone'?s\s+)?account",

            r"how\s+can\s+i\s+create\s+malware",

            r"how\s+to\s+create\s+malware",

            r"create\s+(a\s+)?virus",

            r"create\s+(a\s+)?ransomware",

        ]

        if self._matches(
            query,
            unsafe_patterns
        ):

            return {
                "allowed": False,
                "category": "unsafe",
                "reason": (
                    "The query contains a potentially "
                    "harmful request."
                ),
                "agent": "guardrail"
            }

        # -----------------------------------------------------
        # Query Length
        # -----------------------------------------------------

        if len(query) > 10000:

            return {
                "allowed": False,
                "category": "invalid_input",
                "reason": (
                    "The query exceeds the maximum "
                    "allowed length."
                ),
                "agent": "guardrail"
            }

        # -----------------------------------------------------
        # Safe
        # -----------------------------------------------------

        return {
            "allowed": True,
            "category": "safe",
            "reason": "",
            "agent": "guardrail"
        }

    # =========================================================
    # HELPER
    # =========================================================

    @staticmethod
    def _matches(
        query: str,
        patterns: list[str]
    ) -> bool:

        query = query.lower()

        for pattern in patterns:

            if re.search(
                pattern,
                query
            ):
                return True

        return False