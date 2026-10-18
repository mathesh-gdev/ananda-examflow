"""
models.py — Data structures and domain models for the Exam Cell application.

Using Python dataclasses provides:
  1. Type safety and IDE autocompletion.
  2. Clear self-documentation for interviewers reading your code.
  3. Easy conversion to and from standard Python dictionaries (JSON serializable).
"""

from dataclasses import dataclass, field, asdict
from typing import Optional, List, Dict, Any


@dataclass
class Student:
    """Represents an individual student attending an examination."""
    roll: str
    year: int  # 1 to 5 (1-3: UG, 4-5: PG)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class Seat:
    """Represents a specific assigned seat in an exam hall."""
    roll: str
    year: int
    seat_no: int

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class HallRow:
    """
    Represents one row of desks in an exam hall.
    Each row contains a Left Desk (3 seats) and a Right Desk (3 seats).
    """
    row_num: int
    left_desk: List[Optional[Dict[str, Any]]] = field(default_factory=list)
    right_desk: List[Optional[Dict[str, Any]]] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class HallStats:
    """Student count statistics for a hall broken down by academic year."""
    y1: int = 0
    y2: int = 0
    y3: int = 0
    total: int = 0

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class Hall:
    """Represents an entire examination hall with arranged seating and statistics."""
    name: str
    rows: List[Dict[str, Any]] = field(default_factory=list)
    stats: Dict[str, int] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class MasterRecord:
    """Flattened record for the master notice board list."""
    roll: str
    year: int
    hall: str
    location: str

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)
