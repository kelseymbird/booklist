# booklist/domain/enums.py
from enum import Enum

class ReadingStatus(str, Enum):
    NOT_READ = "not read"
    READING = "reading"
    FINISHED = "finished"
    DNF = "dnf"  # Did Not Finish

class OwnershipStatus(str, Enum):
    OWNED = "owned"
    NOT_OWNED = "not owned"
    WANT = "want"
