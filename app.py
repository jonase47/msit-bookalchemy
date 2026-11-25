"""Book Alchemy: a digital library built with Flask and Flask-SQLAlchemy."""

import os
import secrets
from datetime import date

from flask import Flask, flash, redirect, render_template, request, url_for
from werkzeug.wrappers import Response

from data_models import db, Author, Book

# Case-insensitive sort expressions for the home page, keyed by the "sort" query parameter.
SORT_COLUMNS = {"title": db.func.lower(Book.title), "author": db.func.lower(Author.name)}

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY") or secrets.token_hex(32)

basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{os.path.join(basedir, 'data/library.sqlite')}"
# Allow overriding settings via FLASK_* environment variables (used by the tests).
app.config.from_prefixed_env()

db.init_app(app)

with app.app_context():
    db.create_all()


def parse_date(value: str) -> date | None:
    """Convert a 'YYYY-MM-DD' form value into a date, or None if it is empty.

    Raises ValueError if the value is not a valid ISO date.
    """
    value = value.strip()
    if not value:
        return None
    return date.fromisoformat(value)


def parse_year(value: str) -> int | None:
    """Convert an optional year form value into an int, or None if it is empty.

    Raises ValueError if the value is not a whole number.
    """
    value = value.strip()
    if not value:
        return None
    return int(value)


def find_author(value: str) -> Author | None:
    """Return the author whose id is given as form value, or None if there is none."""
    try:
        author_id = int(value)
    except ValueError:
        return None
    return db.session.get(Author, author_id)


def reject(message: str, endpoint: str) -> Response:
    """Flash an error message and redirect back to the given endpoint."""
    flash(message, "error")
    return redirect(url_for(endpoint))


@app.route("/add_author", methods=["GET", "POST"])
def add_author() -> str | Response:
    """Show the author form (GET) or save a new author (POST)."""
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        try:
            birth_date = parse_date(request.form.get("birthdate", ""))
            date_of_death = parse_date(request.form.get("date_of_death", ""))
        except ValueError:
            return reject("Please enter valid dates.", "add_author")
        if not name or birth_date is None:
            return reject("Name and birthdate are required.", "add_author")

        author = Author(name=name, birth_date=birth_date, date_of_death=date_of_death)
        db.session.add(author)
        db.session.commit()
        flash(f"Author '{author.name}' was added successfully.", "success")
        return redirect(url_for("add_author"))

    return render_template("add_author.html")


@app.route("/add_book", methods=["GET", "POST"])
def add_book() -> str | Response:
    """Show the book form (GET) or save a new book (POST)."""
    if request.method == "POST":
        title = request.form.get("title", "").strip()
        isbn = request.form.get("isbn", "").strip()
        if not title or not isbn:
            return reject("Title and ISBN are required.", "add_book")
        try:
            publication_year = parse_year(request.form.get("publication_year", ""))
        except ValueError:
            return reject("The publication year must be a whole number.", "add_book")
        author = find_author(request.form.get("author_id", ""))
        if author is None:
            return reject("Please choose an existing author.", "add_book")
        existing_book = db.session.execute(db.select(Book).filter_by(isbn=isbn)).scalar_one_or_none()
        if existing_book is not None:
            return reject("A book with this ISBN already exists.", "add_book")

        book = Book(isbn=isbn, title=title, publication_year=publication_year, author=author)
        db.session.add(book)
        db.session.commit()
        flash(f"Book '{book.title}' was added successfully.", "success")
        return redirect(url_for("add_book"))

    authors = db.session.execute(db.select(Author).order_by(Author.name)).scalars().all()
    return render_template("add_book.html", authors=authors)


@app.route("/")
def home() -> str:
    """Show the books with their author and cover image.

    Supports sorting by title or author and an optional keyword search in the title.
    """
    sort = request.args.get("sort", "title")
    if sort not in SORT_COLUMNS:
        sort = "title"
    search = request.args.get("q", "").strip()

    query = db.select(Book).join(Book.author)
    if search:
        query = query.where(Book.title.like(f"%{search}%"))
    query = query.order_by(SORT_COLUMNS[sort], SORT_COLUMNS["title"])
    books = db.session.execute(query).scalars().all()
    return render_template("home.html", books=books, sort=sort, search=search)


@app.route("/book/<int:book_id>/delete", methods=["POST"])
def delete_book(book_id: int) -> Response:
    """Delete a book and also its author if the author has no other books."""
    book = db.get_or_404(Book, book_id)
    author = book.author
    # Check before deleting: author.books still lists the book until the commit.
    author_has_no_other_books = author.books == [book]

    db.session.delete(book)
    message = f"Book '{book.title}' was deleted successfully."
    if author_has_no_other_books:
        db.session.delete(author)
        message += f" Author '{author.name}' had no other books and was deleted too."
    db.session.commit()

    flash(message, "success")
    return redirect(url_for("home"))


@app.route("/author/<int:author_id>/delete", methods=["POST"])
def delete_author(author_id: int) -> Response:
    """Delete an author; the relationship cascade deletes all of their books."""
    author = db.get_or_404(Author, author_id)
    book_count = len(author.books)

    db.session.delete(author)
    db.session.commit()

    flash(f"Author '{author.name}' and {book_count} book(s) were deleted successfully.", "success")
    return redirect(url_for("home"))
