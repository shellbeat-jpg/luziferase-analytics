"""
Erzeugt eine simulierte NowPlayingResponse fuer eine gegebene Station.

Bewusst einfach in Woche 1: fester Beispiel-Katalog + zeitgewichtete Hoererzahl.
Der echte Track-Katalog aus dem Artist-Upload-Portal wird spaeter eingebunden
(z.B. per DB-Export/API), sobald die Grundpipeline steht.
"""
from __future__ import annotations

import random
import time
from datetime import datetime, timezone

from app.models.nowplaying import (
    Listeners,
    LiveInfo,
    NowPlayingEntry,
    NowPlayingResponse,
    SongInfo,
    StationInfo,
)
from app.simulation.weights import get_hourly_weight

# Platzhalter-Katalog -- bewusst klein, wird in Woche 1 ggf. erweitert.
_DEMO_CATALOG = [
    {"artist": "Kollektiv Turmstrasse", "title": "Ferner Osten", "genre": "Techno"},
    {"artist": "Recondite", "title": "On- Train", "genre": "Techno"},
    {"artist": "Robert Babicz", "title": "Made of Wood", "genre": "Deep House"},
    {"artist": "Acid Pauli", "title": "Trees", "genre": "Organic House"},
    {"artist": "Baldur", "title": "Elephant", "genre": "Melodic Techno"},
]

_STATIONS = {
    "luziferase": StationInfo(id=1, name="Luziferase on Air", shortcode="luziferase"),
    "modular": StationInfo(id=2, name="Luziferase Modular", shortcode="modular"),
    "bass": StationInfo(id=3, name="Luziferase Bass", shortcode="bass"),
}


def _base_listener_count(hour: int, weekday: int) -> int:
    """Grobe Basis-Hoererzahl: Stundengewicht * Tagesfaktor * Zufallsrauschen."""
    weekend_boost = 1.4 if weekday >= 5 else 1.0  # Sa/So (5,6) etwas mehr Hoerer
    base = get_hourly_weight(hour) * 400 * weekend_boost  # 400 = fiktive Tages-Gesamtreichweite
    noise = random.uniform(0.85, 1.15)
    return max(0, round(base * noise))


def get_simulated_nowplaying(station_shortcode: str) -> NowPlayingResponse:
    if station_shortcode not in _STATIONS:
        raise ValueError(f"Unbekannte Mock-Station: {station_shortcode}")

    now = datetime.now(timezone.utc)
    track = random.choice(_DEMO_CATALOG)
    current_listeners = _base_listener_count(now.hour, now.weekday())

    song = SongInfo(
        id=f"{track['artist']}-{track['title']}".lower().replace(" ", "-"),
        text=f"{track['artist']} - {track['title']}",
        artist=track["artist"],
        title=track["title"],
        genre=track["genre"],
    )
    now_playing = NowPlayingEntry(
        sh_id=int(time.time()),
        played_at=int(now.timestamp()),
        duration=random.randint(180, 420),
        playlist="default",
        is_request=False,
        song=song,
    )

    return NowPlayingResponse(
        station=_STATIONS[station_shortcode],
        listeners=Listeners(
            total=current_listeners,
            unique=max(0, current_listeners - random.randint(0, 3)),
            current=current_listeners,
        ),
        live=LiveInfo(is_live=False),
        now_playing=now_playing,
    )
