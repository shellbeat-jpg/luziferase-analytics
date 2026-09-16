"""
Pydantic-Schemas fuer die AzuraCast Now-Playing-API.

Nachgebaut nach der oeffentlich dokumentierten Struktur (Endpoint: /api/nowplaying/{station}).
WICHTIG: Vor dem Umschalten von Mock -> echte API einmal gegen eine echte Response
(z.B. https://<deine-azuracast-domain>/api/nowplaying/luziferase) validieren und
Feldnamen/Optionalitaet bei Bedarf anpassen -- AzuraCast aendert Details gelegentlich
zwischen Versionen.
"""
from __future__ import annotations

from typing import Optional
from pydantic import BaseModel, Field


class SongInfo(BaseModel):
    id: str
    text: str
    artist: str
    title: str
    album: Optional[str] = None
    genre: Optional[str] = None
    art: Optional[str] = None


class NowPlayingEntry(BaseModel):
    sh_id: int
    played_at: int = Field(..., description="Unix-Timestamp")
    duration: int = Field(..., description="Tracklaenge in Sekunden")
    playlist: Optional[str] = None
    streamer: Optional[str] = None
    is_request: bool = False
    song: SongInfo


class Listeners(BaseModel):
    total: int
    unique: int
    current: int


class LiveInfo(BaseModel):
    is_live: bool = False
    streamer_name: Optional[str] = None


class StationInfo(BaseModel):
    id: int
    name: str
    shortcode: str
    description: Optional[str] = None


class NowPlayingResponse(BaseModel):
    station: StationInfo
    listeners: Listeners
    live: LiveInfo
    now_playing: NowPlayingEntry
    playing_next: Optional[NowPlayingEntry] = None
