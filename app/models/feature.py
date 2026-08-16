"""
Feature model structures.

This module contains small, self-documenting data structures used by the
application to represent extracted features. Keep these lightweight and
serializable; they exist primarily for developer clarity and testing.
"""
from dataclasses import dataclass, asdict
from typing import Dict

@dataclass
class FeatureVector:
    """Container for basic extracted features.

    Attributes:
        length: length of the sample (characters)
        num_digits: number of digit characters
        num_lines: number of lines in the sample
    """
    length: int = 0
    num_digits: int = 0
    num_lines: int = 0

    def to_dict(self) -> Dict[str, int]:
        """Return a plain dict representation suitable for ML code."""
        return asdict(self)
