from dataclasses import dataclass, field
from datetime import date
from typing import List
from .tag import Tag
from .enums import ReadingStatus, OwnershipStatus

@dataclass
class Book:
    def __init__(
        self,
        title,
        author,
        reading_status,
        ownership_status,
        rating=None,
        tags=None,
        id=None,
        series_name=None,
        series_position=None
    ):
        self.id = id
        self.title = title
        self.author = author
        self.reading_status = reading_status
        self.ownership_status = ownership_status
        self.rating = rating
        self.tags = tags if tags else []
        self.series_name = series_name
        self.series_position = series_position
