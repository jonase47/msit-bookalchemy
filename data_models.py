"""Database models for the Book Alchemy library."""

from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


# db.Model is created at runtime, so mypy cannot resolve it as a base class.
class Author(db.Model):  # type: ignore[name-defined]
    """An author who has written one or more books."""

    __tablename__ = "authors"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String, nullable=False)
    birth_date = db.Column(db.Date, nullable=False)
    date_of_death = db.Column(db.Date)

    def __repr__(self) -> str:
        return f"<Author id={self.id} name={self.name!r}>"

    def __str__(self) -> str:
        return self.name


# db.Model is created at runtime, so mypy cannot resolve it as a base class.
class Book(db.Model):  # type: ignore[name-defined]
    """A book in the library, written by exactly one author."""

    __tablename__ = "books"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    isbn = db.Column(db.String, nullable=False, unique=True)
    title = db.Column(db.String, nullable=False)
    publication_year = db.Column(db.Integer)
    author_id = db.Column(db.Integer, db.ForeignKey("authors.id"), nullable=False)

    def __repr__(self) -> str:
        return f"<Book id={self.id} title={self.title!r}>"

    def __str__(self) -> str:
        return f"{self.title} ({self.publication_year})"
