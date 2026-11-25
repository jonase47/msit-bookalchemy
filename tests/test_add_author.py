"""Tests for the /add_author route."""

import pytest
from flask.testing import FlaskClient

from app import app
from data_models import Author, db


def test_add_author_saves_author(client: FlaskClient) -> None:
    form = {"name": "Neil Gaiman", "birthdate": "1960-11-10", "date_of_death": ""}

    response = client.post("/add_author", data=form, follow_redirects=True)

    assert "Success:" in response.get_data(as_text=True)
    with app.app_context():
        [author] = db.session.execute(db.select(Author)).scalars().all()
        assert (author.name, str(author.birth_date), author.date_of_death) == (
            "Neil Gaiman", "1960-11-10", None
        )


@pytest.mark.parametrize(
    ("form", "message"),
    [
        ({"name": "  ", "birthdate": "1960-11-10"}, "Name and birthdate are required."),
        ({"name": "Neil Gaiman", "birthdate": ""}, "Name and birthdate are required."),
        ({"name": "Neil Gaiman", "birthdate": "not a date"}, "Please enter valid dates."),
    ],
)
def test_add_author_rejects_invalid_input(
    client: FlaskClient, form: dict[str, str], message: str
) -> None:
    response = client.post("/add_author", data=form, follow_redirects=True)

    assert f"Error: {message}" in response.get_data(as_text=True)
    with app.app_context():
        assert db.session.execute(db.select(Author)).scalars().all() == []
