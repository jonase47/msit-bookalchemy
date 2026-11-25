"""Shared pytest fixtures for the Book Alchemy tests."""

import os
from collections.abc import Iterator

import pytest
from flask.testing import FlaskClient

# Point the app at an in-memory database before it is imported,
# so the tests never touch data/library.sqlite.
os.environ["FLASK_SQLALCHEMY_DATABASE_URI"] = "sqlite://"

from app import app as flask_app
from data_models import db


@pytest.fixture
def client() -> Iterator[FlaskClient]:
    """Yield a test client backed by a fresh, empty database."""
    flask_app.config["TESTING"] = True
    with flask_app.app_context():
        db.drop_all()
        db.create_all()
    with flask_app.test_client() as test_client:
        yield test_client
