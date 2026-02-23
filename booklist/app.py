from flask import Flask, render_template, request, redirect, url_for
from booklist.repository.sqlite_repository import SQLiteBookRepository
from booklist.services.library_service import LibraryService
from booklist.domain.book import Book
from booklist.domain.tag import Tag
from booklist.domain.enums import ReadingStatus, OwnershipStatus

app = Flask(__name__)

repo = SQLiteBookRepository()
service = LibraryService(repo)


@app.route("/")
def index():
    books = service.list_books()
    return render_template("index.html", books=books)


@app.route("/add", methods=["GET", "POST"])
def add_book():
    if request.method == "POST":
        title = request.form["title"]
        author = request.form["author"]
        reading_status = ReadingStatus(request.form["reading_status"])
        ownership_status = OwnershipStatus(request.form["ownership_status"])
        rating = request.form.get("rating")
        rating = int(rating) if rating else None
        tags_raw = request.form.get("tags", "")
        tags = [Tag(id=None, name=t.strip()) for t in tags_raw.split(",") if t.strip()]

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
        return redirect(url_for("index"))

    return render_template("add_edit.html", book=None)


@app.route("/edit/<int:book_id>", methods=["GET", "POST"])
def edit_book(book_id):
    books = service.list_books()
    book = next((b for b in books if b.id == book_id), None)
    if not book:
        return redirect(url_for("index"))

    if request.method == "POST":
        book.title = request.form["title"]
        book.author = request.form["author"]
        book.reading_status = ReadingStatus(request.form["reading_status"])
        book.ownership_status = OwnershipStatus(request.form["ownership_status"])
        rating = request.form.get("rating")
        book.rating = int(rating) if rating else None
        tags_raw = request.form.get("tags", "")
        book.tags = [Tag(id=None, name=t.strip()) for t in tags_raw.split(",") if t.strip()]

        service.update_book(book)
        return redirect(url_for("index"))

    return render_template("add_edit.html", book=book)


@app.route("/delete/<int:book_id>")
def delete_book(book_id):
    service.delete_book(book_id)
    return redirect(url_for("index"))


@app.route("/filter", methods=["GET", "POST"])
def filter_books():
    if request.method == "POST":
        reading_status = request.form.get("reading_status")
        ownership_status = request.form.get("ownership_status")
        tag = request.form.get("tag")

        reading_status = ReadingStatus(reading_status) if reading_status else None
        ownership_status = OwnershipStatus(ownership_status) if ownership_status else None

        books = service.filter_books(
            reading_status=reading_status,
            ownership_status=ownership_status,
            tag=tag or None
        )

        return render_template("index.html", books=books)

    return render_template("filter.html")


if __name__ == "__main__":
    app.run(debug=True)
