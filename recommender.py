"""Book recommendations from any OpenAI-compatible chat completions API.

Configured via environment variables:
    RECOMMENDER_API_URL  base URL of the API, e.g. ending in /v1 (required)
    RECOMMENDER_MODEL    model name (required)
    RECOMMENDER_API_KEY  bearer token (optional, local servers often need none)
"""

import json
import os
import urllib.request
from collections.abc import Iterable

from data_models import Book

TIMEOUT_SECONDS = 30
SYSTEM_PROMPT = (
    "You are a librarian. Based on the user's library (title – author – rating), "
    "recommend one book that is not in the list and explain your choice in two or three sentences."
)


class RecommenderError(Exception):
    """Raised when no recommendation could be fetched; the message is safe to show to users."""


def is_configured() -> bool:
    """Return True if the API address and model name are set."""
    return bool(os.environ.get("RECOMMENDER_API_URL") and os.environ.get("RECOMMENDER_MODEL"))


def describe_books(books: Iterable[Book]) -> str:
    """List the books with title, author and rating only; nothing else is sent to the API."""
    lines = []
    for book in books:
        rating = f"{book.rating}/10" if book.rating else "not rated"
        lines.append(f"- {book.title} – {book.author.name} – {rating}")
    return "\n".join(lines)


def recommend_book(books: Iterable[Book]) -> str:
    """Ask the configured API for a book recommendation and return its answer text."""
    api_url = os.environ.get("RECOMMENDER_API_URL", "").rstrip("/")
    headers = {"Content-Type": "application/json"}
    api_key = os.environ.get("RECOMMENDER_API_KEY")
    if api_key:
        headers["Authorization"] = f"Bearer {api_key}"
    payload = {
        "model": os.environ.get("RECOMMENDER_MODEL", ""),
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": describe_books(books)},
        ],
    }
    request = urllib.request.Request(
        f"{api_url}/chat/completions", data=json.dumps(payload).encode(), headers=headers
    )
    try:
        with urllib.request.urlopen(request, timeout=TIMEOUT_SECONDS) as response:
            answer = json.load(response)
        return str(answer["choices"][0]["message"]["content"]).strip()
    # OSError covers timeouts, network and HTTP errors; the others cover unexpected answers.
    except (OSError, ValueError, KeyError, IndexError, TypeError) as error:
        raise RecommenderError(
            "The recommendation service is currently unavailable. Please try again later."
        ) from error
