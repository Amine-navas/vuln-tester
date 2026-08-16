"""
User model.

Minimal structure for users of the system (authentication is out of scope for
this simple scaffold). This file exists to make the `app.models` package
complete and human-friendly.
"""
from dataclasses import dataclass, asdict
from typing import Optional, Dict, Any

@dataclass
class User:
    username: str
    email: Optional[str] = None
    metadata: Dict[str, Any] = None

    def to_dict(self):
        return asdict(self)
