from abc import ABC, abstractmethod
from booklist.domain.book import Book


class BaseBookRepository(ABC):

    @abstractmethod
    def add(self, book: Book) -> Book:
        pass

    @abstractmethod
    def get_all(self) -> list[Book]:
        pass

    @abstractmethod
    def delete(self, book_id: int) -> None:
        pass
