from dataclasses import dataclass, field

@dataclass
class Document:
    """
    Standard document objecr produced by every loader.
    """
    content: str
    metadata: dict = field(default_factory=dict)