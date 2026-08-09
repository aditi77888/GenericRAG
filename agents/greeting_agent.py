import random

from agents.base_agent import BaseAgent


class GreetingAgent(BaseAgent):

    def __init__(self):

        # =====================================================
        # ENGLISH
        # =====================================================

        self.responses = {

            "english": {

                "greeting": [

                    "Hello! What would you like to know?",

                    "Hi! How can I help you?",

                    "Hey! What can I help you with?",

                    "Hello! I'm ready to help.",

                ],

                "thanks": [

                    "You're welcome!",

                    "Happy to help!",

                    "Anytime!",

                    "Glad I could help!",

                ],

                "goodbye": [

                    "Goodbye! Have a great day.",

                    "Take care!",

                    "See you later!",

                    "Goodbye! Feel free to come back anytime.",

                ],
            },

            # =================================================
            # HINDI
            # =================================================

            "hindi": {

                "greeting": [

                    "नमस्ते! मैं आपकी कैसे सहायता कर सकता हूँ?",

                    "प्रणाम! आप क्या जानना चाहते हैं?",

                    "नमस्कार! मैं आपकी मदद करने के लिए यहाँ हूँ।",

                ],

                "thanks": [

                    "कोई बात नहीं!",

                    "आपका स्वागत है!",

                    "खुशी हुई मदद करके!",

                ],

                "goodbye": [

                    "अलविदा! आपका दिन शुभ हो।",

                    "फिर मिलेंगे!",

                    "अपना ध्यान रखिए!",

                ],
            },

            # =================================================
            # HINGLISH
            # =================================================

            "hinglish": {

                "greeting": [

                    "Hello! Main aapki help karne ke liye ready hoon.",

                    "Hi! Main aapki kaise help kar sakta hoon?",

                    "Hello! Bataiye, main aapki kya help kar sakta hoon?",

                ],

                "thanks": [

                    "Koi baat nahi!",

                    "You're welcome!",

                    "Anytime!",

                ],

                "goodbye": [

                    "Bye! Apna dhyan rakhna.",

                    "See you later!",

                    "Phir milte hain!",

                ],
            },
        }

    # =========================================================
    # HANDLE
    # =========================================================

    def handle(
        self,
        query: str,
        intent: str,
        language: str
    ) -> str:

        # -----------------------------------------------------
        # Normalize language
        # -----------------------------------------------------

        language = language.lower().strip()

        if language not in self.responses:

            language = "english"

        # -----------------------------------------------------
        # Normalize intent
        # -----------------------------------------------------

        if intent not in self.responses[language]:

            intent = "greeting"

        # -----------------------------------------------------
        # Select random response
        # -----------------------------------------------------

        return random.choice(
            self.responses[language][intent]
        )