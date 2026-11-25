"""Book Alchemy: a digital library built with Flask and Flask-SQLAlchemy."""

import os
import secrets
from datetime import date

from flask import Flask, flash, redirect, render_template, request, url_for
from werkzeug.wrappers import Response

from data_models import db, Author, Book

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY") or secrets.token_hex(32)

basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{os.path.join(basedir, 'data/library.sqlite')}"

db.init_app(app)

with app.app_context():
    db.create_all()


def parse_date(value: str) -> date | None:
    """Convert a 'YYYY-MM-DD' form value into a date, or None if it is empty.

    Raises ValueError if the value is not a valid ISO date.
    """
    value = value.strip()
    if not value:
        return None
    return date.fromisoformat(value)


def reject(message: str, endpoint: str) -> Response:
    """Flash an error message and redirect back to the given endpoint."""
    flash(message, "error")
    return redirect(url_for(endpoint))


@app.route("/add_author", methods=["GET", "POST"])
def add_author() -> str | Response:
    """Show the author form (GET) or save a new author (POST)."""
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        try:
            birth_date = parse_date(request.form.get("birthdate", ""))
            date_of_death = parse_date(request.form.get("date_of_death", ""))
        except ValueError:
            return reject("Please enter valid dates.", "add_author")
        if not name or birth_date is None:
            return reject("Name and birthdate are required.", "add_author")

        author = Author(name=name, birth_date=birth_date, date_of_death=date_of_death)
        db.session.add(author)
        db.session.commit()
        flash(f"Author '{author.name}' was added successfully.", "success")
        return redirect(url_for("add_author"))

    return render_template("add_author.html")
