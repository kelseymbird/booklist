from booklist.domain.enums import BookStatus


class LibraryService:

    def __init__(self, repo):
        self.repo = repo

    def add_book(self, book):
        return self.repo.add(book)

    def list_books(self):
        return self.repo.get_all()

    def filter_books(self, status=None, tag=None, min_rating=None):
        books = self.repo.get_all()

        if status:
            books = [b for b in books if b.status == status]

        if tag:
            books = [b for b in books if any(t.name == tag for t in b.tags)]

        if min_rating:
            books = [b for b in books if b.rating and b.rating >= min_rating]

        return books

    def delete_book(self, book_id):
        self.repo.delete(book_id)
