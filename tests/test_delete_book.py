"""Tests for deleting a book."""

from datetime import date

import pytest
from flask.testing import FlaskClient

from app import app
from data_models import Author, Book, db


@pytest.mark.parametrize(("book_count", "author_remains"), [(1, False), (2, True)])
def test_delete_book_removes_author_without_other_books(
    client: FlaskClient, book_count: int, author_remains: bool
) -> None:
    with app.app_context():
        author = Author(name="Ursula K. Le Guin", birth_date=date(1929, 10, 21))
        db.session.add_all([Book(isbn=str(i), title=f"Book {i}", author=author) for i in range(book_count)])
        db.session.commit()

    response = client.post("/book/1/delete", follow_redirects=True)

    assert "was deleted successfully." in response.get_data(as_text=True)
    with app.app_context():
        assert db.session.get(Book, 1) is None
        assert (db.session.get(Author, 1) is not None) == author_remains
