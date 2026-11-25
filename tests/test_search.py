"""Tests for the keyword search on the home page."""

from datetime import date

import pytest
from flask.testing import FlaskClient

from app import app
from data_models import Author, Book, db


@pytest.mark.parametrize(
    ("search", "expected"),
    [("left", "The Left Hand of Darkness"), ("dragon", 'No books found for "dragon".')],
)
def test_search_filters_books_by_title(client: FlaskClient, search: str, expected: str) -> None:
    with app.app_context():
        author = Author(name="Ursula K. Le Guin", birth_date=date(1929, 10, 21))
        db.session.add_all([Book(isbn="1", title="The Left Hand of Darkness", author=author),
                            Book(isbn="2", title="The Dispossessed", author=author)])
        db.session.commit()

    html = client.get(f"/?q={search}").get_data(as_text=True)

    assert expected in html
    assert "The Dispossessed" not in html
