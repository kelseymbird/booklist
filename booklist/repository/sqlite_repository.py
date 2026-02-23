import sqlite3
from datetime import date
from booklist.domain.book import Book
from booklist.domain.tag import Tag
from booklist.domain.enums import ReadingStatus, OwnershipStatus

class SQLiteBookRepository:

    def __init__(self, db_path="books.db"):
        self.conn = sqlite3.connect(db_path)
        self.conn.row_factory = sqlite3.Row
        self._create_tables()

    def _create_tables(self):
        cursor = self.conn.cursor()

        cursor.execute("""
        CREATE TABLE IF NOT EXISTS books (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            author TEXT NOT NULL,
            reading_status TEXT NOT NULL DEFAULT 'not read',
            ownership_status TEXT NOT NULL DEFAULT 'not owned',
            rating INTEGER,
            date_started TEXT,
            date_finished TEXT,
            notes TEXT
        )
        """)

        cursor.execute("""
        CREATE TABLE IF NOT EXISTS tags (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE NOT NULL
        )
        """)

        cursor.execute("""
        CREATE TABLE IF NOT EXISTS book_tags (
            book_id INTEGER,
            tag_id INTEGER,
            PRIMARY KEY (book_id, tag_id),
            FOREIGN KEY(book_id) REFERENCES books(id),
            FOREIGN KEY(tag_id) REFERENCES tags(id)
        )
        """)

        self.conn.commit()

    def add(self, book: Book) -> Book:
        cursor = self.conn.cursor()

        cursor.execute("""
        INSERT INTO books (title, author, reading_status, ownership_status, rating, date_started, date_finished, notes)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            book.title,
            book.author,
            book.reading_status.value,
            book.ownership_status.value,
            book.rating,
            book.date_started.isoformat() if book.date_started else None,
            book.date_finished.isoformat() if book.date_finished else None,
            book.notes
        ))

        book_id = cursor.lastrowid

        for tag in book.tags:
            tag_id = self._get_or_create_tag(tag.name)
            cursor.execute(
                "INSERT OR IGNORE INTO book_tags (book_id, tag_id) VALUES (?, ?)",
                (book_id, tag_id)
            )

        self.conn.commit()
        book.id = book_id
        return book

    def _get_or_create_tag(self, name: str) -> int:
        cursor = self.conn.cursor()

        cursor.execute("SELECT id FROM tags WHERE name = ?", (name,))
        row = cursor.fetchone()

        if row:
            return row["id"]

        cursor.execute("INSERT INTO tags (name) VALUES (?)", (name,))
        return cursor.lastrowid

    def get_all(self) -> list[Book]:
        cursor = self.conn.cursor()

        cursor.execute("SELECT * FROM books")
        book_rows = cursor.fetchall()

        books = []

        for row in book_rows:
            book_id = row["id"]

            cursor.execute("""
                SELECT t.id, t.name
                FROM tags t
                JOIN book_tags bt ON bt.tag_id = t.id
                WHERE bt.book_id = ?
            """, (book_id,))
            tag_rows = cursor.fetchall()

            tags = [Tag(id=t["id"], name=t["name"]) for t in tag_rows]

            books.append(
                Book(
                    id=book_id,
                    title=row["title"],
                    author=row["author"],
                    reading_status=ReadingStatus(row["reading_status"]),
                    ownership_status=OwnershipStatus(row["ownership_status"]),
                    rating=row["rating"],
                    date_started=date.fromisoformat(row["date_started"]) if row["date_started"] else None,
                    date_finished=date.fromisoformat(row["date_finished"]) if row["date_finished"] else None,
                    notes=row["notes"],
                    tags=tags
                )
            )

        return books

    def delete(self, book_id: int) -> None:
        cursor = self.conn.cursor()
        cursor.execute("DELETE FROM book_tags WHERE book_id = ?", (book_id,))
        cursor.execute("DELETE FROM books WHERE id = ?", (book_id,))
        self.conn.commit()

    def update(self, book: Book) -> Book:
        cursor = self.conn.cursor()
        cursor.execute("""
            UPDATE books
            SET title = ?, author = ?, reading_status = ?, ownership_status = ?, rating = ?, date_started = ?, date_finished = ?, notes = ?
            WHERE id = ?
        """, (
            book.title,
            book.author,
            book.reading_status.value,
            book.ownership_status.value,
            book.rating,
            book.date_started.isoformat() if book.date_started else None,
            book.date_finished.isoformat() if book.date_finished else None,
            book.notes,
            book.id
        ))

        # Update tags: remove old, add new
        cursor.execute("DELETE FROM book_tags WHERE book_id = ?", (book.id,))
        for tag in book.tags:
            tag_id = self._get_or_create_tag(tag.name)
            cursor.execute(
                "INSERT OR IGNORE INTO book_tags (book_id, tag_id) VALUES (?, ?)",
                (book.id, tag_id)
            )

        self.conn.commit()
        return book
