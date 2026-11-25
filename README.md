# Book Alchemy

Digitale Bibliothek als Flask-App mit Flask-SQLAlchemy und SQLite.
Codio-Projekt aus dem MSIT-Kurs „AI for Developers“, Track OOP mit Python, Woche 4.

## Starten

```bash
uv sync
uv run flask run --host=0.0.0.0 --port=5002
```

Die App läuft dann unter http://localhost:5002. In Codio ist Port 5002 Pflicht.

## Aufbau

| Pfad | Zweck |
| --- | --- |
| `app.py` | Flask-App, Konfiguration und Routen |
| `data_models.py` | Modelle `Author` und `Book` |
| `templates/` | Jinja-Templates |
| `data/library.sqlite` | SQLite-Datenbank |
