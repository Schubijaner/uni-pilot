# Database Initialization Scripts

Diese Skripte dienen zur Initialisierung und Befüllung der SQLite-Datenbank mit Mock-Daten für Tests und Entwicklung.

## Voraussetzungen

1. **Conda Environment aktivieren:**
   ```bash
   conda env create -f environment.yml
   conda activate uni_pilot
   ```

   Oder falls das Environment bereits existiert:
   ```bash
   conda activate uni_pilot
   ```

2. **Dependencies installieren:**
   ```bash
   pip install -r requirements.txt
   ```

## Verwendung

### Datenbank initialisieren

Das Hauptskript `init_db.py` erstellt die Datenbank und befüllt sie mit Mock-Daten:

```bash
python scripts/init_db.py
```

**Optionen:**
- `--drop`: Löscht die vorhandene Datenbank automatisch, falls sie existiert (ohne Nachfrage)

Beispiel:
```bash
python scripts/init_db.py --drop
```

### Was wird erstellt?

Die Skripte erstellen eine vollständige SQLite-Datenbank (`uni_pilot.db`) mit:

- **3 Universitäten**: TU Darmstadt, TUM, LMU München
- **4 Studiengänge**: Informatik (Bachelor/Master) an verschiedenen Universitäten, Wirtschaftsinformatik
- **11 Module**: Realistische Module für Informatik-Studiengang (Pflicht- und Wahlmodule)
- **5 Topic Fields**: Full Stack Development, Backend, Frontend, Data Science, Machine Learning
- **Career Tree**: Hierarchische Struktur mit 3 Ebenen
- **3 Roadmaps**: Vollständige Roadmaps für verschiedene Topic Fields
- **Roadmap Items**: Zeitlich strukturiert (Semester + Semesterferien)
- **3 Test-User**: Mit Profilen, Fortschritt und Beispiel-Chats
- **Empfehlungen**: Bücher, Kurse, Projekte
- **Chat Sessions**: Beispiel-Chats mit Messages
- **Module Imports**: Import-Historie

### Test-User

Die Mock-Daten enthalten folgende Test-User:

1. **Max Mustermann** (TU Darmstadt)
   - Email: `max.mustermann@stud.tu-darmstadt.de`
   - Password: `password123`
   - Semester: 4
   - Topic Field: Full Stack Development
   - Hat bereits einige Module abgeschlossen und Fortschritt in der Roadmap

2. **Anna Schmidt** (TU Darmstadt)
   - Email: `anna.schmidt@stud.tu-darmstadt.de`
   - Password: `password123`
   - Semester: 3
   - Topic Field: Backend Development

3. **Tom Weber** (TUM)
   - Email: `tom.weber@stud.tum.de`
   - Password: `password123`
   - Semester: 2
   - Noch kein Topic Field ausgewählt

## Skripte

### `init_db.py`
Hauptskript zur Datenbank-Initialisierung:
- Erstellt alle Tabellen
- Befüllt die Datenbank mit Mock-Daten
- Bietet Option zum Löschen vorhandener Datenbank

### `seed_database.py`
Enthält die Logik zum Befüllen der Datenbank:
- Kann auch direkt verwendet werden (erfordert bereits vorhandene Tabellen)
- Funktion `seed_database(db: Session)` kann in Tests wiederverwendet werden

### `view_db.py`
Schnelles Skript zum Anzeigen von Datenbankinhalten in der CLI:
```bash
# Alle Daten anzeigen
python scripts/view_db.py

# Nur Zusammenfassung
python scripts/view_db.py --summary

# Details für spezifischen User
python scripts/view_db.py --user 1
```

## Datenbank-Datei

Die SQLite-Datenbank wird als `uni_pilot.db` im Root-Verzeichnis des Projekts erstellt.

**Wichtig:** Die Datei wird durch `init_db.py --drop` gelöscht. Bei Produktionsdaten bitte vorsichtig sein!

## Troubleshooting

### "Module not found" Fehler
Stelle sicher, dass das Conda Environment aktiviert ist und alle Dependencies installiert sind:
```bash
conda activate uni_pilot
pip install -r requirements.txt
```

### "Database is locked" Fehler
Stelle sicher, dass keine anderen Prozesse auf die Datenbank zugreifen. Schließe alle Datenbankverbindungen oder starte das Skript neu.

### Datenbank zurücksetzen
Um die Datenbank komplett neu zu erstellen:
```bash
python scripts/init_db.py --drop
```

## Weiterentwicklung

Bei Änderungen am Datenbankschema:
1. Aktualisiere `database/models.py`
2. Führe `init_db.py --drop` aus, um die Datenbank neu zu erstellen

Für Produktion sollte stattdessen Alembic für Migrations verwendet werden.

