# Book Alchemy

Digitale Bibliothek als Flask-App mit Flask-SQLAlchemy und SQLite.
Codio-Projekt aus dem MSIT-Kurs „AI for Developers“, Track OOP mit Python, Woche 4.

## Funktionen

- Autoren und Bücher über Formulare anlegen, Bücher mit Autor-Auswahl
- Startseite mit allen Büchern als Karten, mit Cover, Autor und Bewertung
- Sortieren nach Titel oder Autor, Stichwortsuche im Titel
- Detailseiten für Bücher und Autoren
- Bücher mit 0,5 bis 5 Sternen bewerten (gespeichert als ganze Zahl von 1 bis 10)
- Buch löschen: Hat der Autor danach keine Bücher mehr, wird er mitgelöscht
- Autor löschen (auf seiner Detailseite): Seine Bücher werden mitgelöscht
- KI-Buchempfehlung auf Basis der Bibliothek, über eine frei wählbare Schnittstelle
- Ein gemeinsames Stylesheet mit Dark Mode, bedienbar per Tastatur und auf schmalen Bildschirmen

## Starten

Mit [uv](https://docs.astral.sh/uv/):

```bash
uv sync
uv run flask run --host=0.0.0.0 --port=5002
```

Oder mit pip:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
flask run --host=0.0.0.0 --port=5002
```

Die App läuft dann unter http://localhost:5002. In Codio ist Port 5002 Pflicht.
Die Datenbank `data/library.sqlite` mit Beispieldaten liegt im Repo.

## Tests und Typprüfung

```bash
uv run pytest
uv run mypy .
```

Mit pip vorher `pip install pytest mypy`, dann `pytest` und `mypy .`.
Die Tests nutzen eine Datenbank im Arbeitsspeicher und rufen keine externe Schnittstelle auf.

## Routen

| Route | Methode | Zweck |
| --- | --- | --- |
| `/` | GET | Startseite, Parameter `sort` (`title`, `author`) und `q` (Suche) |
| `/add_author` | GET, POST | Autor anlegen |
| `/add_book` | GET, POST | Buch anlegen |
| `/book/<book_id>` | GET | Detailseite eines Buchs |
| `/book/<book_id>/rate` | POST | Buch bewerten (1–10, angezeigt als 0,5–5 Sterne) |
| `/book/<book_id>/delete` | POST | Buch löschen |
| `/author/<author_id>` | GET | Detailseite eines Autors |
| `/author/<author_id>/delete` | POST | Autor mit allen Büchern löschen |
| `/recommendation` | GET, POST | KI-Buchempfehlung |

## Cover

Die Cover kommen von [Open Library](https://openlibrary.org/dev/docs/api/covers) über die ISBN,
z. B. `https://covers.openlibrary.org/b/isbn/<isbn>-M.jpg`. Der Browser lädt sie direkt,
der Server ruft Open Library nicht auf. Für unbekannte ISBNs erscheint ein grauer Platzhalter.

## KI-Buchempfehlung

Die Empfehlung funktioniert mit jeder Schnittstelle im OpenAI-kompatiblen Chat-Format,
auch mit lokalen Servern wie Ollama. Konfiguriert wird sie über Umgebungsvariablen:

| Variable | Pflicht | Bedeutung |
| --- | --- | --- |
| `RECOMMENDER_API_URL` | ja | Basisadresse, die App hängt `/chat/completions` an |
| `RECOMMENDER_MODEL` | ja | Name des Modells |
| `RECOMMENDER_API_KEY` | nein | Schlüssel, wird als `Authorization: Bearer …` gesendet |

Beispiel mit Anthropic:

```bash
export RECOMMENDER_API_URL="https://api.anthropic.com/v1/"
export RECOMMENDER_MODEL="claude-haiku-5-5"
export RECOMMENDER_API_KEY="…"   # eigenen Schlüssel einsetzen, nie ins Repo
```

Ohne `RECOMMENDER_API_URL` und `RECOMMENDER_MODEL` zeigt die Seite einen Hinweis statt eines Fehlers.
Der Aufruf bricht nach 30 Sekunden ab. Bei Fehlern erscheint eine verständliche Meldung,
die Einzelheiten stehen im Server-Log.

## Datenfluss

- **Cover:** Der Browser der Besucher lädt die Bilder von Open Library (USA).
  Dabei erhält Open Library die IP-Adresse und die ISBN.
- **KI-Empfehlung:** Erst nach Klick auf „Get recommendation“ sendet der Server
  Titel, Autor und Bewertung aller Bücher an die konfigurierte Adresse. Sonst nichts,
  also keine ISBN, keine Lebensdaten und keine Daten der Besucher.
  Wohin die Daten gehen, bestimmt allein `RECOMMENDER_API_URL`. Mit einem lokalen Server
  bleiben sie auf der eigenen Infrastruktur.
- Alle übrigen Daten bleiben in `data/library.sqlite`.

## Bekannte Grenzen

- **Keine Rückfrage vor dem Löschen.** Die Oberfläche kommt ohne JavaScript aus, deshalb gibt es kein `confirm()`.
  Ein Klick auf „Delete book“ oder „Delete author“ löscht sofort.
- **Umlaute:** Sortierung und Suche unterscheiden bei Ä, Ö und Ü Groß- und Kleinschreibung,
  weil SQLite `lower()` und `LIKE` nur für A–Z ohne Rücksicht auf die Schreibung behandelt.
- **Cover-Bilder** übertragen die IP-Adresse der Besucher an Open Library in den USA (siehe Datenfluss).
- **Kein CSRF-Schutz** für die Formulare. Für ein öffentlich betriebenes System wäre z. B. Flask-WTF nötig.

## Aufbau

| Pfad | Zweck |
| --- | --- |
| `app.py` | Flask-App, Konfiguration und Routen |
| `data_models.py` | Modelle `Author` und `Book` mit Beziehung |
| `recommender.py` | Aufruf der KI-Schnittstelle |
| `templates/` | Jinja-Templates, alle erben von `base.html` |
| `static/style.css` | Gemeinsames Stylesheet |
| `tests/` | pytest-Tests |
| `data/library.sqlite` | SQLite-Datenbank mit Beispieldaten |
| `requirements.txt` | Abhängigkeiten für pip, `pyproject.toml` und `uv.lock` für uv |
