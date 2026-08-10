class ChatMemory:
    """
    Lightweight in-session conversational memory.

    Keeps the last N (question, answer) turns for a single chat
    session and formats them for injection into the RAG prompt,
    so follow-up questions like "what about his email?" or
    "and the second one?" can be resolved using recent context.

    This is per-session, in-memory only. It resets when the
    Chainlit session ends (e.g. on page refresh). It is NOT a
    database — it does not persist chat history across restarts.
    """

    def __init__(self, max_turns: int = 6):

        self.max_turns = max_turns

        # Each turn: {"question": ..., "answer": ...}
        self.turns = []

    def add_turn(self, question: str, answer: str):

        if not question or not answer:
            return

        self.turns.append({
            "question": question,
            "answer": answer
        })

        if len(self.turns) > self.max_turns:
            self.turns = self.turns[-self.max_turns:]

    def get_history_text(self, n: int = None) -> str:
        """
        Returns the last `n` turns (default: all stored turns,
        up to max_turns) formatted as plain text, oldest first.

        Returns an empty string if there is no history yet.
        """

        turns = self.turns

        if n is not None:
            turns = turns[-n:]

        if not turns:
            return ""

        lines = []

        for turn in turns:
            lines.append(f"User: {turn['question']}")
            lines.append(f"Assistant: {turn['answer']}")

        return "\n".join(lines)

    def clear(self):
        self.turns = []

    def __len__(self):
        return len(self.turns)