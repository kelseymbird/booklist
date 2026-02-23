import sqlite3
from booklist.domain.book import Book
from booklist.domain.tag import Tag
from booklist.domain.enums import ReadingStatus, OwnershipStatus
from datetime import date

DB_FILE = "books.db"

class SQLiteBookRepository:
    def __init__(self):
        # Create tables if they don't exist
        with sqlite3.connect(DB_FILE) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS books (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title TEXT NOT NULL,
                    author TEXT NOT NULL,
                    reading_status TEXT,
                    ownership_status TEXT,
                    rating INTEGER
                )
            """)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS tags (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    book_id INTEGER,
                    name TEXT,
                    FOREIGN KEY(book_id) REFERENCES books(id)
                )
            """)
            conn.commit()

    # Add a book
    def add(self, book: Book):
        with sqlite3.connect(DB_FILE) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO books (title, author, reading_status, ownership_status, rating)
                VALUES (?, ?, ?, ?, ?)
            """, (
                book.title,
                book.author,
                book.reading_status.value,
                book.ownership_status.value,
                book.rating
            ))
            book.id = cursor.lastrowid

            for tag in book.tags:
                cursor.execute("""
                    INSERT INTO tags (book_id, name) VALUES (?, ?)
                """, (book.id, tag.name))

            conn.commit()
        return book

    # Update a book
    def update(self, book: Book):
        with sqlite3.connect(DB_FILE) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE books
                SET title=?, author=?, reading_status=?, ownership_status=?, rating=?
                WHERE id=?
            """, (
                book.title,
                book.author,
                book.reading_status.value,
                book.ownership_status.value,
                book.rating,
                book.id
            ))

            # Delete old tags
            cursor.execute("DELETE FROM tags WHERE book_id=?", (book.id,))
            # Insert new tags
            for tag in book.tags:
                cursor.execute("""
                    INSERT INTO tags (book_id, name) VALUES (?, ?)
                """, (book.id, tag.name))

            conn.commit()
        return book

    # Delete a book
    def delete(self, book_id: int):
        with sqlite3.connect(DB_FILE) as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM tags WHERE book_id=?", (book_id,))
            cursor.execute("DELETE FROM books WHERE id=?", (book_id,))
            conn.commit()

    # Get all books
    def get_all(self):
        with sqlite3.connect(DB_FILE) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id, title, author, reading_status, ownership_status, rating FROM books")
            rows = cursor.fetchall()
            books = []
            for row in rows:
                book_id, title, author, reading_status, ownership_status, rating = row

                cursor.execute("SELECT name FROM tags WHERE book_id=?", (book_id,))
                tag_rows = cursor.fetchall()
                tags = [Tag(id=None, name=tr[0]) for tr in tag_rows]

                books.append(Book(
                    id=book_id,
                    title=title,
                    author=author,
                    reading_status=ReadingStatus(reading_status),
                    ownership_status=OwnershipStatus(ownership_status),
                    rating=rating,
                    tags=tags
                ))
        return books

    # Optional: filter books
    def filter(self, reading_status=None, ownership_status=None, tag=None):
        books = self.get_all()
        if reading_status:
            books = [b for b in books if b.reading_status == reading_status]
        if ownership_status:
            books = [b for b in books if b.ownership_status == ownership_status]
        if tag:
            books = [b for b in books if any(t.name == tag for t in b.tags)]
        return books
