"""
Scan result model.

Provides a friendly container for API responses and internal processing
so the code returns consistent data shapes.
"""
from dataclasses import dataclass, asdict
from typing import Dict, Any

@dataclass
class ScanResult:
    hash: str
    result: str
    score: float
    risk: str
    features: Dict[str, Any]

    def to_json(self) -> Dict[str, Any]:
        return asdict(self)
