from dataclasses import dataclass, field

@dataclass
class OCRResult:
    """
       Standard OCR result returned by every OCR engine.
    """
    text: str
    confidence: float = 1.0
    metadata: dict = field(default_factory=dict)