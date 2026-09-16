# Luziferase Analytics Dashboard

Portfolio-Referenzprojekt: Analytics-Pipeline für Azuracast Radio.
Stack: FastAPI + Pydantic (async) → Postgres → dbt → Next.js (Woche 4).

**Status Woche 1:** Mock-API (bildet AzuraCast Now-Playing-API nach) + async
Ingestion-Worker + Postgres-Rohdatenablage. Noch keine echten Hörerdaten,
noch keine dbt-Modelle, noch kein Frontend.

## Architekturprinzip

Der Ingestion-Worker kennt nur die Pydantic-Schemas in `app/models/nowplaying.py`,
nicht deren Quelle. Aktuell zeigt er auf `/mock/nowplaying/{station}` (Simulator).
Sobald echte Hörer da sind, wird nur `BASE_URL` in `app/ingestion/worker.py` auf
die echte AzuraCast-Instanz umgestellt — der Rest der Pipeline bleibt unverändert.

Die Hörerzahl-Simulation nutzt aktuell eine Platzhalter-Tageskurve
(`app/simulation/weights.py`). Nächster Schritt: durch eine aus Last.fm-Scrobbles
abgeleitete, genre-spezifische 24h-Gewichtungskurve ersetzen.

## Setup (lokal oder auf dem Hetzner-Server)

### 1. Environment vorbereiten

```bash
cp .env.example .env
# POSTGRES_PASSWORD in .env setzen (starkes Passwort, nicht committen)
```

**Erfolgskriterium:** `.env` existiert und ist in `.gitignore` erfasst (bereits vorbereitet).
**Rollback:** `.env` löschen, keine weiteren Auswirkungen (Datei wird nicht committet).
**Risiko:** none.

### 2. Stack starten

```bash
docker compose build
docker compose up -d
```

**Erfolgskriterium:**
```bash
docker compose ps                     # beide Services "healthy"/"running"
curl -s http://localhost:18100/health   # {"status":"ok","database":true}
```

**Rollback:**
```bash
docker compose down          # Container stoppen, Volume (DB-Daten) bleibt erhalten
docker compose down -v       # zusätzlich Postgres-Volume löschen (nur wenn wirklich gewünscht)
```
**Risiko:** low — neuer, isolierter Stack (eigenes Docker-Netzwerk, eigenes Volume,
kein Eingriff in bestehende Luziferase-/Breviarium-Container).

### 3. Ingestion prüfen

```bash
docker compose logs -f api | grep ingestion
```
Sollte alle `INGESTION_POLL_INTERVAL_SECONDS` (Standard: 30s) eine Zeile pro
Station loggen (`Station <x>: <artist> - <title> (<n> Hörer)`).

**Erfolgskriterium:** Nach 2-3 Minuten Laufzeit mehrere Zeilen pro Station im Log.

### 4. Rohdaten in Postgres stichprobenartig prüfen

```bash
docker compose -f docker-compose.yml -f docker-compose.dev.yml up -d db
psql "postgresql://analytics:<PASSWORT>@localhost:5433/luziferase_analytics" \
  -c "SELECT station_shortcode, count(*) FROM raw.nowplaying_events GROUP BY 1;"
```
**Hinweis:** `docker-compose.dev.yml` öffnet den Postgres-Port nur lokal — auf dem
Hetzner-Server nicht verwenden, dort stattdessen `docker compose exec db psql ...`.

## Deployment auf dem Hetzner-Server (Übersicht, Details in Woche 4)

- Separates Verzeichnis, z. B. `/opt/luziferase-analytics` — eigenständiges Repo,
  analog zu Breviarium, kein Eingriff in die bestehende Luziferase-Bind-Mount-Struktur.
- API intern: Container-Port `8000`.
- Host-Binding: `127.0.0.1:18100`.
- nginx upstream: `http://127.0.0.1:18100`.
- Public URL: `https://analytics.luziferase.de`.
- Zugriff von außen ausschließlich über nginx (`nginx/analytics_luziferase.conf.example`).
- Eigenes Let's-Encrypt-Zertifikat für `analytics.luziferase.de`; nicht das bestehende
  Luziferase-Zertifikat wiederverwenden.

## Nächste Schritte (Woche 2)

1. `dbt/models/staging/stg_nowplaying_events.sql` — Rohdaten bereinigen/deduplizieren
2. `dbt/models/marts/fct_plays.sql` — ein Play pro tatsächlichem Trackwechsel
   (aktuell schreibt der Worker jede Poll-Runde, auch wenn sich der Track nicht geändert hat)
3. `dbt/models/marts/mart_listener_curve.sql` — Hörerzahl pro Stunde/Station
4. Last.fm-Client (`app/ingestion/lastfm_client.py`) für die echte Gewichtungskurve

