"""
24h-Gewichtungskurve fuer den Hoerer-Simulator.

STAND JETZT: Platzhalter (leicht abgeflachte Tageskurve), rein zur lauffaehigen
Grundstruktur in Woche 1.

NAECHSTER SCHRITT (Last.fm-Integration): get_hourly_weights() durch echte,
aus Last.fm-Scrobbles abgeleitete Werte ersetzen -- z.B. via
`ingestion/lastfm_client.py` (noch zu bauen) Scrobbles fuer die Ziel-Tags
(z.B. "techno", "acid house", "modular") abfragen, Stunden-Histogramm bilden,
normalisieren (Summe = 1.0) und hier statt der Platzhalterwerte einsetzen.
"""
from __future__ import annotations

# Platzhalter: grobe Tageskurve (Index 0 = 00:00-01:00 Uhr, ... Index 23 = 23:00-24:00 Uhr)
# Noch NICHT aus echten Daten abgeleitet -- absichtlich einfach gehalten, damit
# die Pipeline (Mock -> Ingestion -> DB) end-to-end getestet werden kann, bevor
# die Last.fm-Kurve eingebaut wird.
_PLACEHOLDER_HOURLY_WEIGHTS = [
    0.010, 0.008, 0.006, 0.005, 0.004, 0.004,  # 00-06 Uhr: ruhig
    0.006, 0.012, 0.020, 0.028, 0.032, 0.035,  # 06-12 Uhr: steigend
    0.038, 0.040, 0.042, 0.045, 0.048, 0.052,  # 12-18 Uhr: Plateau, leicht steigend
    0.065, 0.080, 0.090, 0.085, 0.060, 0.030,  # 18-24 Uhr: Abend-Peak
]

_total = sum(_PLACEHOLDER_HOURLY_WEIGHTS)
NORMALIZED_HOURLY_WEIGHTS = [w / _total for w in _PLACEHOLDER_HOURLY_WEIGHTS]


def get_hourly_weight(hour: int) -> float:
    """Gibt das normalisierte Gewicht (0.0-1.0) fuer eine Stunde (0-23) zurueck."""
    if not 0 <= hour <= 23:
        raise ValueError("hour muss zwischen 0 und 23 liegen")
    return NORMALIZED_HOURLY_WEIGHTS[hour]
