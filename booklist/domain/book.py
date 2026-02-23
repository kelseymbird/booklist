from dataclasses import dataclass, field
from datetime import date
from typing import List
from .enums import BookStatus
from .tag import Tag


@dataclass
class Book:
    id: int | None
    title: str
    author: str
    status: BookStatus
    rating: int | None = None
    date_started: date | None = None
    date_finished: date | None = None
    notes: str | None = None
    tags: List[Tag] = field(default_factory=list)
