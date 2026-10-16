from flask import Flask, render_template, request, redirect, url_for
from booklist.repository.sqlite_repository import SQLiteBookRepository
from booklist.services.library_service import LibraryService
from booklist.domain.book import Book
from booklist.domain.tag import Tag
from booklist.domain.enums import ReadingStatus, OwnershipStatus

app = Flask(__name__)

repo = SQLiteBookRepository()
service = LibraryService(repo)


def book_from_form(book=None):
    title = request.form["title"]
    author = request.form["author"]
    reading_status = ReadingStatus(request.form["reading_status"])
    ownership_status = OwnershipStatus(request.form["ownership_status"])
    rating = request.form.get("rating")
    series_position = request.form.get("series_position")
    tags = [
        Tag(id=None, name=name.strip())
        for name in request.form.get("tags", "").split(",")
        if name.strip()
    ]
    albums = list(dict.fromkeys(
        name.strip()
        for name in request.form.get("albums", "").split(",")
        if name.strip()
    ))
    values = {
        "title": title,
        "author": author,
        "reading_status": reading_status,
        "ownership_status": ownership_status,
        "rating": int(rating) if rating else None,
        "tags": tags,
        "series_name": request.form.get("series_name") or None,
        "series_position": int(series_position) if series_position else None,
        "albums": albums,
    }
    if book:
        for key, value in values.items():
            setattr(book, key, value)
        return book
    return Book(id=None, **values)


@app.route("/")
def index():
    return render_template("index.html", books=service.list_books())


@app.route("/albums")
def albums():
    return render_template("albums.html", albums=repo.list_albums())


@app.route("/albums/<int:album_id>")
def album_detail(album_id):
    album, books = repo.get_album(album_id)
    if not album:
        return redirect(url_for("albums"))
    return render_template("album_detail.html", album=album, books=books)


@app.route("/add", methods=["GET", "POST"])
def add_book():
    if request.method == "POST":
        service.add_book(book_from_form())
        return redirect(url_for("index"))
    return render_template("add_edit.html", book=None)


@app.route("/edit/<int:book_id>", methods=["GET", "POST"])
def edit_book(book_id):
    book = next((item for item in service.list_books() if item.id == book_id), None)
    if not book:
        return redirect(url_for("index"))
    if request.method == "POST":
        service.update_book(book_from_form(book))
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
        books = service.filter_books(
            reading_status=ReadingStatus(reading_status) if reading_status else None,
            ownership_status=OwnershipStatus(ownership_status) if ownership_status else None,
            tag=request.form.get("tag") or None,
            series_name=request.form.get("series_name") or None,
        )
        return render_template("filter.html", books=books)
    return render_template("filter.html", books=None)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
