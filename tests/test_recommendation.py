"""Tests for the AI book recommendation; the real API is never called."""

import io
import json
import urllib.request
from datetime import date

import pytest
from flask.testing import FlaskClient

from app import app
from data_models import Author, Book, db

ANSWER = json.dumps({"choices": [{"message": {"content": "Try The Left Hand of Darkness."}}]})


@pytest.mark.parametrize(
    ("configured", "outcome", "expected"),
    [
        (False, None, "not set up on this server"),
        (True, ANSWER, "Try The Left Hand of Darkness."),
        (True, TimeoutError(), "Error: The recommendation service is currently unavailable."),
    ],
)
def test_recommendation(
    client: FlaskClient, monkeypatch: pytest.MonkeyPatch,
    configured: bool, outcome: str | Exception | None, expected: str,
) -> None:
    with app.app_context():
        author = Author(name="Ursula K. Le Guin", birth_date=date(1929, 10, 21))
        db.session.add(Book(isbn="111", title="Earthsea", rating=9, author=author))
        db.session.commit()
    for name in ("RECOMMENDER_API_URL", "RECOMMENDER_MODEL", "RECOMMENDER_API_KEY"):
        monkeypatch.delenv(name, raising=False)
    if configured:
        monkeypatch.setenv("RECOMMENDER_API_URL", "http://llm.invalid/v1")
        monkeypatch.setenv("RECOMMENDER_MODEL", "test-model")
    sent: list[dict] = []

    def fake_urlopen(request: urllib.request.Request, timeout: float) -> io.BytesIO:
        sent.append(json.loads(request.data))  # type: ignore[arg-type]
        if isinstance(outcome, Exception):
            raise outcome
        return io.BytesIO(str(outcome).encode())

    monkeypatch.setattr(urllib.request, "urlopen", fake_urlopen)

    page = client.post("/recommendation").get_data(as_text=True)

    assert expected in page
    expected_calls = [["- Earthsea – Ursula K. Le Guin – 9/10"]] if configured else []
    assert [[m["content"] for m in body["messages"][1:]] for body in sent] == expected_calls
