"""Tests for rating a book."""

from datetime import date

import pytest
from flask.testing import FlaskClient

from app import app
from data_models import Author, Book, db


@pytest.mark.parametrize(
    ("value", "saved_rating", "message"),
    [
        ("7", 7, "Success: Book &#39;Earthsea&#39; was rated 3.5 of 5 stars."),
        ("0", None, "Error: Please choose a rating from 0.5 to 5 stars."),
        ("11", None, "Error: Please choose a rating from 0.5 to 5 stars."),
        ("7.5", None, "Error: Please choose a rating from 0.5 to 5 stars."),
    ],
)
def test_rate_book(client: FlaskClient, value: str, saved_rating: int | None, message: str) -> None:
    with app.app_context():
        author = Author(name="Ursula K. Le Guin", birth_date=date(1929, 10, 21))
        db.session.add(Book(isbn="111", title="Earthsea", author=author))
        db.session.commit()

    response = client.post("/book/1/rate", data={"rating": value}, follow_redirects=True)

    assert message in response.get_data(as_text=True)
    with app.app_context():
        assert db.session.execute(db.select(Book.rating)).scalar_one() == saved_rating
