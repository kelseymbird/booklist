import sqlite3
from booklist.domain.book import Book
from booklist.domain.tag import Tag
from booklist.domain.enums import ReadingStatus, OwnershipStatus

DB_FILE = "books.db"


class SQLiteBookRepository:
    def __init__(self):
        with sqlite3.connect(DB_FILE) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS books (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title TEXT NOT NULL,
                    author TEXT NOT NULL,
                    reading_status TEXT,
                    ownership_status TEXT,
                    rating INTEGER,
                    series_name TEXT,
                    series_position INTEGER
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
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS albums (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL COLLATE NOCASE UNIQUE
                )
            """)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS book_albums (
                    book_id INTEGER NOT NULL,
                    album_id INTEGER NOT NULL,
                    PRIMARY KEY (book_id, album_id),
                    FOREIGN KEY(book_id) REFERENCES books(id) ON DELETE CASCADE,
                    FOREIGN KEY(album_id) REFERENCES albums(id) ON DELETE CASCADE
                )
            """)
            conn.commit()

    def _save_book_albums(self, cursor, book_id, album_names):
        cursor.execute("DELETE FROM book_albums WHERE book_id=?", (book_id,))
        names = dict.fromkeys(
            name.strip() for name in (album_names or []) if name.strip()
        )
        for name in names:
            cursor.execute("INSERT OR IGNORE INTO albums (name) VALUES (?)", (name,))
            cursor.execute("SELECT id FROM albums WHERE name=? COLLATE NOCASE", (name,))
            album_id = cursor.fetchone()[0]
            cursor.execute(
                "INSERT OR IGNORE INTO book_albums (book_id, album_id) VALUES (?, ?)",
                (book_id, album_id),
            )

    def add(self, book: Book):
        with sqlite3.connect(DB_FILE) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO books
                (title, author, reading_status, ownership_status, rating, series_name, series_position)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                book.title, book.author, book.reading_status.value,
                book.ownership_status.value, book.rating, book.series_name,
                book.series_position,
            ))
            book.id = cursor.lastrowid
            for tag in book.tags:
                cursor.execute(
                    "INSERT INTO tags (book_id, name) VALUES (?, ?)",
                    (book.id, tag.name),
                )
            self._save_book_albums(cursor, book.id, book.albums)
            conn.commit()
        return book

    def update(self, book: Book):
        with sqlite3.connect(DB_FILE) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE books
                SET title=?, author=?, reading_status=?, ownership_status=?, rating=?,
                    series_name=?, series_position=?
                WHERE id=?
            """, (
                book.title, book.author, book.reading_status.value,
                book.ownership_status.value, book.rating, book.series_name,
                book.series_position, book.id,
            ))
            cursor.execute("DELETE FROM tags WHERE book_id=?", (book.id,))
            for tag in book.tags:
                cursor.execute(
                    "INSERT INTO tags (book_id, name) VALUES (?, ?)",
                    (book.id, tag.name),
                )
            self._save_book_albums(cursor, book.id, book.albums)
            conn.commit()
        return book

    def delete(self, book_id: int):
        with sqlite3.connect(DB_FILE) as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM tags WHERE book_id=?", (book_id,))
            cursor.execute("DELETE FROM book_albums WHERE book_id=?", (book_id,))
            cursor.execute("DELETE FROM books WHERE id=?", (book_id,))
            conn.commit()

    def get_all(self):
        with sqlite3.connect(DB_FILE) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT id, title, author, reading_status, ownership_status,
                       rating, series_name, series_position
                FROM books ORDER BY title COLLATE NOCASE
            """)
            rows = cursor.fetchall()
            books = []
            for row in rows:
                (book_id, title, author, reading_status, ownership_status,
                 rating, series_name, series_position) = row
                cursor.execute("SELECT name FROM tags WHERE book_id=?", (book_id,))
                tags = [Tag(id=None, name=r[0]) for r in cursor.fetchall()]
                cursor.execute("""
                    SELECT a.name FROM albums a
                    JOIN book_albums ba ON ba.album_id = a.id
                    WHERE ba.book_id=? ORDER BY a.name COLLATE NOCASE
                """, (book_id,))
                albums = [r[0] for r in cursor.fetchall()]
                books.append(Book(
                    id=book_id, title=title, author=author,
                    reading_status=ReadingStatus(reading_status),
                    ownership_status=OwnershipStatus(ownership_status),
                    rating=rating, tags=tags, series_name=series_name,
                    series_position=series_position, albums=albums,
                ))
        return books

    def list_albums(self):
        with sqlite3.connect(DB_FILE) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT a.id, a.name, COUNT(ba.book_id)
                FROM albums a LEFT JOIN book_albums ba ON ba.album_id=a.id
                GROUP BY a.id, a.name ORDER BY a.name COLLATE NOCASE
            """)
            return [
                {"id": row[0], "name": row[1], "book_count": row[2]}
                for row in cursor.fetchall()
            ]

    def delete_album(self, album_id):
        with sqlite3.connect(DB_FILE) as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM book_albums WHERE album_id=?", (album_id,))
            cursor.execute("DELETE FROM albums WHERE id=?", (album_id,))
            conn.commit()

    def get_album(self, album_id):
        with sqlite3.connect(DB_FILE) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id, name FROM albums WHERE id=?", (album_id,))
            row = cursor.fetchone()
            if not row:
                return None, []
            album = {"id": row[0], "name": row[1]}
            cursor.execute("""
                SELECT b.id, b.title, b.author, b.reading_status, b.ownership_status,
                       b.rating, b.series_name, b.series_position
                FROM books b JOIN book_albums ba ON ba.book_id=b.id
                WHERE ba.album_id=? ORDER BY b.title COLLATE NOCASE
            """, (album_id,))
            books = []
            for row in cursor.fetchall():
                (book_id, title, author, reading_status, ownership_status,
                 rating, series_name, series_position) = row
                cursor.execute("SELECT name FROM tags WHERE book_id=?", (book_id,))
                tags = [Tag(id=None, name=r[0]) for r in cursor.fetchall()]
                cursor.execute("""
                    SELECT a.name FROM albums a JOIN book_albums ba ON ba.album_id=a.id
                    WHERE ba.book_id=? ORDER BY a.name COLLATE NOCASE
                """, (book_id,))
                albums = [r[0] for r in cursor.fetchall()]
                books.append(Book(
                    id=book_id, title=title, author=author,
                    reading_status=ReadingStatus(reading_status),
                    ownership_status=OwnershipStatus(ownership_status),
                    rating=rating, tags=tags, series_name=series_name,
                    series_position=series_position, albums=albums,
                ))
            return album, books

    def filter(self, reading_status=None, ownership_status=None, tag=None):
        books = self.get_all()
        if reading_status:
            books = [b for b in books if b.reading_status == reading_status]
        if ownership_status:
            books = [b for b in books if b.ownership_status == ownership_status]
        if tag:
            books = [b for b in books if any(t.name == tag for t in b.tags)]
        return books
