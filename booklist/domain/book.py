# booklist/domain/book.py
from dataclasses import dataclass, field
from datetime import date
from typing import List
from .tag import Tag
from .enums import ReadingStatus, OwnershipStatus

@dataclass
class Book:
    id: int | None
    title: str
    author: str
    reading_status: ReadingStatus = ReadingStatus.NOT_READ
    ownership_status: OwnershipStatus = OwnershipStatus.NOT_OWNED
    rating: int | None = None
    date_started: date | None = None
    date_finished: date | None = None
    notes: str | None = None
    tags: List[Tag] = field(default_factory=list)
