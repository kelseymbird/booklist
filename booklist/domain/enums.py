from enum import Enum


class BookStatus(str, Enum):
    OWNED = "owned"
    READING = "reading"
    READ = "read"
    WANT = "want"
