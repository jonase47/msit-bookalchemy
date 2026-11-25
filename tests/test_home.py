"""Tests for the home page."""

from datetime import date

from flask.testing import FlaskClient

from app import app
from data_models import Author, Book, db


def test_home_lists_books_with_author_and_cover(client: FlaskClient) -> None:
    with app.app_context():
        author = Author(name="Ursula K. Le Guin", birth_date=date(1929, 10, 21))
        db.session.add(Book(isbn="9780441478125", title="The Left Hand of Darkness", author=author))
        db.session.commit()

    html = client.get("/").get_data(as_text=True)

    assert "The Left Hand of Darkness" in html
    assert "Ursula K. Le Guin" in html
    assert "https://covers.openlibrary.org/b/isbn/9780441478125-M.jpg" in html
