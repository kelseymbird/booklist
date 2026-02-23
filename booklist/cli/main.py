from booklist.repository.sqlite_repository import SQLiteBookRepository
from booklist.services.library_service import LibraryService
from booklist.domain.book import Book
from booklist.domain.tag import Tag
from booklist.domain.enums import ReadingStatus, OwnershipStatus

def prompt_reading_status(current=None):
    print("Reading status options: not read, reading, finished, dnf")
    prompt = f"Reading status [{current.value if current else 'not read'}]: "
    choice = input(prompt).lower()
    if choice in [rs.value for rs in ReadingStatus]:
        return ReadingStatus(choice)
    return current or ReadingStatus.NOT_READ

def prompt_ownership_status(current=None):
    print("Ownership options: owned, not owned, want")
    prompt = f"Ownership status [{current.value if current else 'not owned'}]: "
    choice = input(prompt).lower()
    if choice in [os.value for os in OwnershipStatus]:
        return OwnershipStatus(choice)
    return current or OwnershipStatus.NOT_OWNED

def prompt_tags(current=None):
    current_str = ", ".join(t.name for t in current) if current else ""
    raw = input(f"Tags (comma separated) [{current_str}]: ").strip()
    if not raw:
        return current or []
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
        print("6. Edit book")

        choice = input("Choose: ")

        if choice == "1":
            title = input("Title: ").strip()
            author = input("Author: ").strip()
            reading_status = prompt_reading_status()
            ownership_status = prompt_ownership_status()
            rating = input("Rating (1-5 or blank): ").strip()
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
                print(f"{b.id}: {b.title} by {b.author} "
                      f"[Reading: {b.reading_status.value}, Ownership: {b.ownership_status.value}] "
                      f"Rating: {b.rating or '-'} "
                      f"Tags: {tag_str}")

        elif choice == "3":
            print("Filter by (leave blank to skip):")
            rs_input = input("Reading status: ").lower()
            os_input = input("Ownership status: ").lower()
            tag_input = input("Tag: ").strip()

            reading_status = ReadingStatus(rs_input) if rs_input in [rs.value for rs in ReadingStatus] else None
            ownership_status = OwnershipStatus(os_input) if os_input in [os.value for os in OwnershipStatus] else None
            tag = tag_input if tag_input else None

            filtered_books = service.filter_books(
                reading_status=reading_status,
                ownership_status=ownership_status,
                tag=tag
            )

            if not filtered_books:
                print("No books matched your filters.")
            else:
                for b in filtered_books:
                    tag_str = ", ".join(t.name for t in b.tags)
                    print(f"{b.id}: {b.title} by {b.author} "
                          f"[Reading: {b.reading_status.value}, Ownership: {b.ownership_status.value}] "
                          f"Rating: {b.rating or '-'} "
                          f"Tags: {tag_str}")

        elif choice == "4":
            book_id = input("Book ID to delete: ").strip()
            if book_id.isdigit():
                service.delete_book(int(book_id))
                print("Deleted.")
            else:
                print("Invalid book ID.")

        elif choice == "6":
            book_id = input("Book ID to edit: ").strip()
            if not book_id.isdigit():
                print("Invalid ID.")
                continue
            book_id = int(book_id)
            books = service.list_books()
            book = next((b for b in books if b.id == book_id), None)
            if not book:
                print("Book not found.")
                continue

            book.title = input(f"Title [{book.title}]: ").strip() or book.title
            book.author = input(f"Author [{book.author}]: ").strip() or book.author
            book.reading_status = prompt_reading_status(book.reading_status)
            book.ownership_status = prompt_ownership_status(book.ownership_status)
            rating_input = input(f"Rating (1-5) [{book.rating or ''}]: ").strip()
            book.rating = int(rating_input) if rating_input else book.rating
            book.tags = prompt_tags(book.tags)
            service.update_book(book)
            print("Book updated.")

        elif choice == "5":
            break
        else:
            print("Invalid choice. Please try again.")

if __name__ == "__main__":
    main()
