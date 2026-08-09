from dataclasses import dataclass
from typing import Dict


@dataclass
class OCRResponse:

    text: str

    confidence: float | None = None

    metadata: Dict = None