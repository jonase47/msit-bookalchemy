"""Tests for deleting an author."""

from datetime import date

from flask.testing import FlaskClient

from app import app
from data_models import Author, Book, db


def test_delete_author_removes_their_books(client: FlaskClient) -> None:
    with app.app_context():
        le_guin = Author(name="Ursula K. Le Guin", birth_date=date(1929, 10, 21))
        other = Author(name="Octavia E. Butler", birth_date=date(1947, 6, 22))
        db.session.add_all([
            Book(isbn="1", title="Earthsea", author=le_guin),
            Book(isbn="2", title="The Dispossessed", author=le_guin),
            Book(isbn="3", title="Kindred", author=other),
        ])
        db.session.commit()

    response = client.post("/author/1/delete", follow_redirects=True)

    assert "and 2 book(s) were deleted successfully." in response.get_data(as_text=True)
    with app.app_context():
        remaining = db.session.execute(db.select(Book.title)).scalars().all()
        assert remaining == ["Kindred"]
        assert db.session.get(Author, 1) is None
