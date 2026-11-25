"""Tests for the /add_book route."""

from datetime import date

import pytest
from flask.testing import FlaskClient

from app import app
from data_models import Author, Book, db


def create_author_with_book() -> int:
    """Store an author with one book (ISBN 111) and return the author's id."""
    with app.app_context():
        author = Author(name="Ursula K. Le Guin", birth_date=date(1929, 10, 21))
        db.session.add(author)
        db.session.flush()
        db.session.add(Book(isbn="111", title="Earthsea", author_id=author.id))
        db.session.commit()
        return author.id


def test_add_book_saves_book(client: FlaskClient) -> None:
    author_id = create_author_with_book()
    assert f'<option value="{author_id}">' in client.get("/add_book").get_data(as_text=True)
    form = {"isbn": "222", "title": "The Dispossessed", "publication_year": "1974",
            "author_id": str(author_id)}

    response = client.post("/add_book", data=form, follow_redirects=True)

    assert "Success:" in response.get_data(as_text=True)
    with app.app_context():
        book = Book.query.filter_by(isbn="222").one()
        assert (book.title, book.publication_year, book.author_id) == (
            "The Dispossessed", 1974, author_id
        )


@pytest.mark.parametrize(
    ("overrides", "message"),
    [
        ({"title": " "}, "Title and ISBN are required."),
        ({"isbn": ""}, "Title and ISBN are required."),
        ({"publication_year": "1974a"}, "The publication year must be a whole number."),
        ({"author_id": "999"}, "Please choose an existing author."),
        ({"isbn": "111"}, "A book with this ISBN already exists."),
    ],
)
def test_add_book_rejects_invalid_input(
    client: FlaskClient, overrides: dict[str, str], message: str
) -> None:
    author_id = create_author_with_book()
    form = {"isbn": "222", "title": "The Dispossessed", "publication_year": "",
            "author_id": str(author_id), **overrides}

    response = client.post("/add_book", data=form, follow_redirects=True)

    assert f"Error: {message}" in response.get_data(as_text=True)
    with app.app_context():
        assert Book.query.count() == 1
