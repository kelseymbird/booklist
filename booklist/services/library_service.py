from booklist.domain.enums import ReadingStatus, OwnershipStatus

class LibraryService:

    def __init__(self, repo):
        self.repo = repo

    def add_book(self, book):
        return self.repo.add(book)

    def list_books(self):
        return self.repo.get_all()

    def filter_books(self, reading_status=None, ownership_status=None, tag=None, min_rating=None, series_name=None):
        books = self.repo.get_all()

        if reading_status:
            books = [b for b in books if b.reading_status == reading_status]

        if ownership_status:
            books = [b for b in books if b.ownership_status == ownership_status]

        if tag:
            books = [b for b in books if any(t.name == tag for t in b.tags)]

        if min_rating:
            books = [b for b in books if b.rating and b.rating >= min_rating]
        if series_name:
            books = [b for b in books if b.series_name and series_name.lower() in b.series_name.lower()]


        return books

    def delete_book(self, book_id):
        self.repo.delete(book_id)

    def update_book(self, book):
        return self.repo.update(book)
