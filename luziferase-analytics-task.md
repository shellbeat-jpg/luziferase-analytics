# Claude Task Template — Production-Safe Change Request

## 1) Task summary
**Title:** Luziferase Analytics Dashboard — Referenzprojekt (Mock-API → dbt → Next.js)
**Date:** 2026-09-16
**Requested by:** Daniel
**Priority:** Medium
**Type:** Feature (Neuaufbau, isolierter Stack)

## 2) Objective (direct outcome)
Ein eigenständiges, portfoliotaugliches Analytics-System für Azuracast Radio: async
Python/Pydantic-Ingestion → Postgres → dbt-Transformationen → Next.js-Dashboard.
Datenquelle ist zunächst eine Mock-API (bildet die AzuraCast-Now-Playing-API nach,
Hörer-Simulation über eine aus Last.fm-Scrobbles abgeleitete 24h-Gewichtungskurve),
architektonisch so entkoppelt, dass sie später ohne Codeänderung durch die echte
AzuraCast-Instanz ersetzt werden kann.

- **Was ist nach Abschluss wahr?** Ein live erreichbares Dashboard unter
  `analytics.luziferase.de` zeigt Hörerkurven, Top-Tracks und Sendezeiten-Auswertung.
- **Wer profitiert?** Daniel selbst (Referenzprojekt für Bewerbungen), perspektivisch
  auch Artists/Admins des Azuracast-Portals (echte Nutzungszahlen).
- **„Done" heißt:** Vier Wochenmeilensteine (s. Abschnitt 9) abgeschlossen, Stack läuft
  produktiv auf dem Hetzner-Server, README/Runbook aktuell.

## 3) Scope

### In scope
- Mock-API + async Ingestion-Worker + Postgres-Rohdatenablage (Woche 1)
- dbt-Projekt: Staging- und Mart-Modelle (Woche 2)
- Last.fm-API-Client für genre-spezifische Hörer-Gewichtungskurve (Woche 2)
- FastAPI-Auslieferungs-Layer mit Pydantic-Response-Modellen (Woche 3)
- Next.js/TypeScript-Dashboard (Woche 4)
- Deployment auf Hetzner als eigenständiger, isolierter Stack (Woche 4)

### Out of scope
- Anbindung der echten AzuraCast-Hörerdaten (folgt erst, wenn reale Hörerzahlen existieren)
- Änderungen an bestehenden Azuracast-/Breviarium-Containern oder deren nginx-Configs
- Last.fm-Scrobbling der eigenen Station (separates, späteres Vorhaben)
- Automatische Genre-Tag-Anreicherung im Artist-Upload-Portal (separates Vorhaben)

## 4) Environment/context
- **Runtime:** Hetzner Ubuntu, systemd, nginx, Docker Compose
- **Related service(s):** Neuer, isolierter Stack (`db`, `api`; `web` ab Woche 4);
  kein Bind-Mount- oder Netzwerk-Bezug zu AzuraCast/Artist-Upload-Portal
- **Related repo(s):** Neues, eigenständiges Repo `luziferase-analytics` (analog zu
  [[cloud-breviarium]] — kein Zusammenlegen mit dem Hauptsystem)
- **Branch target:** `main` (bislang keine Branches/CI definiert)
- **Domain/DNS touch required?** Ja — aber erst Woche 4 (neue Subdomain
  `analytics.luziferase.de`, eigenes Let's-Encrypt-Zertifikat)
- **DB touch required?** Ja — neue, eigenständige Postgres-Instanz (Container), kein
  Zugriff auf bestehende DBs
- **Email touch required?** Nein

## 5) Constraints & guardrails (must follow)
- Keine Secrets in Output/Code/Logs/PR-Text
- Kein lokales Postfix/mailutils
- Kleinstmögliche, reversible Änderungen bevorzugen
- Pre-Checks, Verifikation, Rollback bei jedem Schritt
- Idempotente Befehle wo möglich
- Bei hoher Unsicherheit: stoppen und nachfragen, bevor riskante Operationen ausgeführt werden

## 6) Inputs provided
- **Error logs:** — (Neuaufbau, noch keine Incidents)
- **Relevant config/files:** `docker-compose.yml`, `.env.example`, `nginx/analytics_luziferase.conf.example`,
  `dbt/dbt_project.yml` (siehe Woche-1-Lieferung)
- **URLs/endpoints:** `/health`, `/mock/nowplaying/{station}` (lokal, Port 8100);
  echte AzuraCast-Now-Playing-URL noch nachzutragen, sobald Umschaltung ansteht
- **Sample payloads:** Mock-Response folgt `app/models/nowplaying.py` (nachgebautes
  AzuraCast-Schema, noch nicht gegen echte Response validiert)
- **Reproduction steps:** n/a (Neuaufbau)
- **Current behavior:** Mock-API + Ingestion-Worker + Rohdatenablage lauffähig (lokal
  getestet: App-Import, Routen-Registrierung, Simulator-Output — kein Docker/Postgres
  in der Entwicklungs-Sandbox verfügbar, daher noch kein Full-Stack-Testlauf)
- **Expected behavior:** `docker compose up -d` startet Stack, `/health` liefert
  `{"status":"ok","database":true}`, Ingestion-Log zeigt periodische Einträge

## 7) Assumptions
1. Subdomain `analytics.luziferase.de` ist verfügbar und gewünscht (sonst in Woche 4 anpassen)
2. Stationsliste `luziferase, modular, bass` entspricht den aktuellen AzuraCast-Shortcodes
3. Postgres läuft isoliert im eigenen Docker-Netzwerk, kein Port-Konflikt mit
   bestehenden Services auf dem Hetzner-Server (vor Deployment in Woche 4 zu prüfen)

*Falls eine Annahme falsch ist: Task pausiert, Rückfrage vor Fortsetzung.*

## 8) Risk assessment
**Risk level:** Low (Wochen 1–3, lokal/isoliert) → Low–Medium (Woche 4, DNS/nginx-Berührung)
**Why:** Neuer, vollständig isolierter Stack ohne Eingriff in produktive Azuracast-/
Breviarium-Komponenten; einziger Berührungspunkt mit bestehender Infrastruktur ist
die neue nginx-Server-Block-Datei in Woche 4.
**Potential impact areas:** nginx (nur neue Datei, Woche 4) / app (isoliert) / db (isoliert) / DNS (neuer A-Record, Woche 4)
**Downtime expected:** None für bestehende Services; für das neue Dashboard selbst
ggf. kurze Unterbrechungen während Deployment/SSL-Einrichtung (Woche 4)

## 9) Implementation plan requested from Claude — Meilensteine

| Woche | Zeitraum | Meilenstein | Status |
|---|---|---|---|
| 1 | 16.09.–22.09.2026 | Mock-API (Pydantic-Schemas nach AzuraCast-Vorbild), async Ingestion-Worker, Postgres-Rohdatenablage (`raw.nowplaying_events`) | Grundgerüst geliefert; `docker compose up` durch Daniel noch zu verifizieren |
| 2 | 23.09.–29.09.2026 | dbt-Modelle (Staging → `fct_plays` → Marts), Last.fm-API-Client zur Ableitung der genre-spezifischen 24h-Gewichtungskurve (ersetzt Platzhalter in `weights.py`) | Offen |
| 3 | 30.09.–06.10.2026 | FastAPI-Auslieferungs-Layer (Pydantic-Response-Modelle für die dbt-Marts), Tests (pytest) | Offen |
| 4 | 07.10.–13.10.2026 | Next.js/TypeScript-Dashboard, Deployment auf Hetzner (eigener Stack, Subdomain, SSL-Zertifikat, nginx-Konfiguration scharf schalten) | Offen |

**Pufferhinweis:** Bei Verzögerung in Woche 2 (dbt/Last.fm ist erfahrungsgemäß der
aufwendigste Block) zuerst Woche 3 kürzen (API-Layer ist mit den Marts aus Woche 2
vergleichsweise schnell), nicht Woche 4 — das Deployment ist der sichtbarste Teil
fürs Portfolio und sollte nicht gestrichen werden.

1. **Plan:** siehe Wochenmeilensteine oben; je Woche eigener Pre-Check/Verifikation/Rollback-Block
2. **Exact commands/code changes:** siehe Woche-1-Lieferung (`docker-compose.yml`, App-Code);
   Wochen 2–4 folgen als jeweils eigene Lieferung
3. **Verification:** siehe README (`curl /health`, Ingestion-Log-Check, DB-Stichprobe)
4. **Rollback:** siehe README (`docker compose down` / `down -v`)
5. **Post-change monitoring:** nach Woche-4-Deployment 15–60 Min. `docker compose logs -f`
   und `tail -f /var/log/nginx/error.log` beobachten

## 10) Mandatory pre-checks (before any change)
```bash
df -h
uptime
docker compose ps
docker stats --no-stream
sudo tail -n 100 /var/log/nginx/error.log
```

Task-spezifisch (vor Woche-1-Start bzw. vor jedem `docker compose up`):
```bash
# Ports 8100 (API) und 3100 (Next.js, ab Woche 4) noch frei?
ss -tulpn | grep -E ':8100|:3100'
# Kein Namenskonflikt mit bestehenden Docker-Netzwerken/Volumes
docker network ls | grep luziferase
docker volume ls | grep luziferase
```

Vor Woche-4-DNS/nginx-Änderung zusätzlich:
```bash
# Bestehende Azuracast-/Breviarium-Configs unberührt?
nginx -t
ls /etc/letsencrypt/live/ | grep -i luziferase
```

## 11) Acceptance criteria
- [ ] Primäres Feature/Ziel funktioniert (siehe je Wochenmeilenstein)
- [ ] Keine neuen nginx-/Config-Fehler
- [ ] Kein Container-Crash/Restart-Loop
- [ ] Keine sensiblen Daten exponiert (`.env` nicht committet, Secrets nicht in Logs)
- [ ] Rollback getestet bzw. validiert
- [ ] Monitoring nach Änderungsfenster stabil

Task-spezifisch:
- [ ] Woche 1: `/health` liefert `database: true`, Ingestion-Log zeigt Einträge für alle 3 Stationen
- [ ] Woche 2: `dbt run` läuft fehlerfrei durch, Marts enthalten plausible (nicht-leere) Daten
- [ ] Woche 3: API liefert Marts-Daten typisiert (Pydantic) und mit Tests abgesichert aus
- [ ] Woche 4: Dashboard unter `https://analytics.luziferase.de` erreichbar, gültiges SSL-Zertifikat

## 12) Test plan

### Functional tests
- Ingestion-Worker: mehrere Poll-Zyklen laufen ohne Exceptions, Daten landen korrekt in Postgres
- dbt: `dbt test` (Schema-/Nullability-Checks) auf Staging- und Mart-Modellen
- API: Health-Check + mind. ein Endpoint pro Mart, Response-Schema per Pydantic validiert
- Frontend: Dashboard lädt, Charts zeigen Daten aus der API (nicht nur Platzhalter)

### Non-functional checks
- **Performance impact:** keiner auf bestehende Services (isolierter Stack); Ingestion-Intervall (Standard 30s) so gewählt, dass keine spürbare Last entsteht
- **Error rate:** Ingestion-Worker soll bei einzelnen fehlgeschlagenen Polls loggen, nicht abstürzen (bereits im Code über try/except abgesichert)
- **Resource usage (CPU/RAM/disk):** vor Woche-4-Deployment mit `docker stats` gegenprüfen, dass der neue Stack den Hetzner-Server nicht in Richtung der bekannten Disk-Alert-Schwellen treibt
- **Security checks:** `.env` nicht im Repo, Postgres nicht öffentlich exponiert (nur `127.0.0.1`-Bindings), eigenes SSL-Zertifikat statt Wiederverwendung des Luziferase-Zertifikats

## 13) Rollback trigger
- Ingestion-Worker crasht wiederholt (> 3 Neustarts in 15 Min.)
- `docker compose ps` zeigt Restart-Loop bei `api` oder `db`
- Nach Woche-4-Deployment: 5xx-Rate auf der neuen Subdomain > 10 % über 10 Min., oder bestehende Luziferase-/Breviarium-Domains zeigen nach der nginx-Änderung Fehler

## 14) Rollback plan
```bash
# Stack stoppen (Daten bleiben erhalten)
docker compose down

# Vollständig zurücksetzen (inkl. Postgres-Volume, nur wenn wirklich gewünscht)
docker compose down -v

# Woche 4 / nginx: neue Server-Block-Datei entfernen, bestehende Configs unberührt
sudo rm /etc/nginx/sites-enabled/analytics_luziferase.conf
nginx -t && systemctl reload nginx
```

## 15) Communication format required from Claude
1. Direkte Empfehlung zuerst
2. Dann „Plan"
3. Dann „Commands"
4. Dann „Verification"
5. Dann „Rollback"
6. Dann „Risk notes / assumptions"

Knapp halten, außer mehr Detail wird angefragt.

## 16) Deliverables
- [x] Woche 1: Patch/Datei-Blöcke (Mock-API, Ingestion-Worker, Docker-Compose-Stack)
- [ ] Woche 2: dbt-Modelle + Last.fm-Client
- [ ] Woche 3: API-Layer + Tests
- [ ] Woche 4: Next.js-Dashboard + Deployment
- [x] Verification-Checkliste (README)
- [x] Rollback-Anleitung (README)
- [ ] Kurze Operator-Notiz fürs Runbook (nach Woche-4-Deployment zu ergänzen)

## 17) Post-implementation notes (fill after execution)
**What changed:** *(nach Abschluss der jeweiligen Woche auszufüllen)*
**What was validated:** *(dito)*
**Any deviations from plan:** *(dito)*
**Follow-up tasks:** *(dito)*
**Incident/runbook update needed:** *(dito — voraussichtlich Ja nach Woche 4, da neue Subdomain/neues Zertifikat in [[hetzner-ops]] nachzutragen ist)*
