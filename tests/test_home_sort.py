"""Tests for sorting the home page."""

from datetime import date

import pytest
from flask.testing import FlaskClient

from app import app
from data_models import Author, Book, db


@pytest.mark.parametrize(
    ("sort", "expected_order"),
    [("title", ["Alpha", "Beta"]), ("author", ["Beta", "Alpha"]), ("unknown", ["Alpha", "Beta"])],
)
def test_home_sorts_books(client: FlaskClient, sort: str, expected_order: list[str]) -> None:
    with app.app_context():
        zoe = Author(name="Zoe Writer", birth_date=date(1950, 1, 1))
        adam = Author(name="Adam Writer", birth_date=date(1950, 1, 1))
        db.session.add_all([Book(isbn="1", title="Alpha", author=zoe), Book(isbn="2", title="Beta", author=adam)])
        db.session.commit()

    html = client.get(f"/?sort={sort}").get_data(as_text=True)

    positions = [html.index(f"<h3>{title}</h3>") for title in expected_order]
    assert positions == sorted(positions)
