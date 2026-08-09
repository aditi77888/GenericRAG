from dataclasses import dataclass, field

@dataclass
class Chunk:
    """
    Represents a chunk of a document.
    """
    content: str
    metadata: dict = field(default_factory=dict)