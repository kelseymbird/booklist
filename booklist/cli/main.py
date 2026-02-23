from booklist.repository.sqlite_repository import SQLiteBookRepository
from booklist.services.library_service import LibraryService
from booklist.domain.book import Book
from booklist.domain.tag import Tag
from booklist.domain.enums import ReadingStatus, OwnershipStatus


def prompt_reading_status():
    print("Reading status options: not read, reading, finished, dnf")
    choice = input("Reading status: ").lower()
    return ReadingStatus(choice)

def prompt_ownership_status():
    print("Ownership options: owned, not owned, want")
    choice = input("Ownership status: ").lower()
    return OwnershipStatus(choice)


def prompt_tags():
    raw = input("Tags (comma separated): ")
    if not raw.strip():
        return []
    return [Tag(id=None, name=t.strip()) for t in raw.split(",")]


def main():
    repo = SQLiteBookRepository()
    service = LibraryService(repo)

    while True:
        print("\n1. Add book")
        print("2. List books")
        print("3. Filter books")
        print("4. Delete book")
        print("5. Exit")

        choice = input("Choose: ")

        if choice == "1":
            title = input("Title: ")
            author = input("Author: ")
            reading_status = prompt_reading_status()
            ownership_status = prompt_ownership_status()
            rating = input("Rating (1-5 or blank): ")
            rating = int(rating) if rating else None
            tags = prompt_tags()

            book = Book(
                id=None,
                title=title,
                author=author,
                reading_status=reading_status,
                ownership_status=ownership_status,
                rating=rating,
                tags=tags
            )

            service.add_book(book)
            print("Book added.")

        elif choice == "2":
            books = service.list_books()
            for b in books:
                tag_str = ", ".join(t.name for t in b.tags)
                print(f"{b.id}: {b.title} by {b.author} [{b.status.value}] ({tag_str})")

        elif choice == "3":
            tag = input("Filter by tag (or blank): ")
            books = service.filter_books(tag=tag if tag else None)
            for b in books:
                print(f"{b.id}: {b.title}")

        elif choice == "4":
            book_id = int(input("Book ID to delete: "))
            service.delete_book(book_id)
            print("Deleted.")

        elif choice == "5":
            break


if __name__ == "__main__":
    main()
