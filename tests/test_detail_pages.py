"""Tests for the book and author detail pages."""

from datetime import date

import pytest
from flask.testing import FlaskClient

from app import app
from data_models import Author, Book, db


@pytest.mark.parametrize(
    ("url", "status", "expected"),
    [
        ("/book/1", 200, ['href="/author/1">Ursula K. Le Guin</a>', "1968"]),
        ("/author/1", 200, ['href="/book/1">Earthsea</a>']),
        ("/book/99", 404, []),
        ("/author/99", 404, []),
    ],
)
def test_detail_pages(client: FlaskClient, url: str, status: int, expected: list[str]) -> None:
    with app.app_context():
        author = Author(name="Ursula K. Le Guin", birth_date=date(1929, 10, 21))
        db.session.add(Book(isbn="111", title="Earthsea", publication_year=1968, author=author))
        db.session.commit()

    response = client.get(url)

    assert response.status_code == status
    page = response.get_data(as_text=True)
    assert all(text in page for text in expected)
    assert "1929" not in page  # Life dates are deliberately not shown.
