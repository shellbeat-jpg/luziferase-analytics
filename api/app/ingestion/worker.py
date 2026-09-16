"""
Async Ingestion-Worker.

Pollt periodisch GET /mock/nowplaying/{station} (spaeter: die echte AzuraCast-URL)
fuer jede konfigurierte Station und schreibt jedes Ergebnis als Rohzeile in
raw.nowplaying_events. Bewusst append-only / kein Upsert -- dbt (Woche 2)
uebernimmt Deduplizierung/Transformation in den Staging-Modellen.

Umschalten von Mock auf echte API: nur BASE_URL unten anpassen (bzw. spaeter
per Env-Variable AZURACAST_BASE_URL steuern) -- der Rest der Pipeline bleibt
unveraendert, weil beide Seiten dasselbe Pydantic-Schema (app.models.nowplaying)
nutzen.
"""
from __future__ import annotations

import asyncio
import logging

import httpx

from app.config import settings
from app.db import async_session, raw_nowplaying_events
from app.models.nowplaying import NowPlayingResponse

logger = logging.getLogger("ingestion.worker")

# Woche 1: zeigt auf den eigenen Mock-Endpoint. Spaeter per Env ersetzbar.
BASE_URL = "http://localhost:8000/mock"


async def _fetch_nowplaying(client: httpx.AsyncClient, station: str) -> NowPlayingResponse | None:
    try:
        resp = await client.get(f"{BASE_URL}/nowplaying/{station}", timeout=10.0)
        resp.raise_for_status()
        return NowPlayingResponse.model_validate(resp.json())
    except (httpx.HTTPError, ValueError) as exc:
        logger.warning("Fehler beim Abruf fuer Station %s: %s", station, exc)
        return None


async def _store_event(data: NowPlayingResponse, station: str) -> None:
    async with async_session() as session:
        await session.execute(
            raw_nowplaying_events.insert().values(
                station_shortcode=station,
                listeners_current=data.listeners.current,
                listeners_unique=data.listeners.unique,
                track_artist=data.now_playing.song.artist,
                track_title=data.now_playing.song.title,
                track_genre=data.now_playing.song.genre,
                played_at_unix=data.now_playing.played_at,
                raw_payload=data.model_dump(mode="json"),
            )
        )
        await session.commit()


async def poll_once(client: httpx.AsyncClient) -> None:
    # Alle konfigurierten Stationen parallel abfragen (async, nicht seriell)
    results = await asyncio.gather(
        *(_fetch_nowplaying(client, station) for station in settings.mock_station_list)
    )
    for station, result in zip(settings.mock_station_list, results):
        if result is not None:
            await _store_event(result, station)
            logger.info(
                "Station %s: %s - %s (%d Hoerer)",
                station,
                result.now_playing.song.artist,
                result.now_playing.song.title,
                result.listeners.current,
            )


async def run_forever() -> None:
    logger.info(
        "Ingestion-Worker gestartet: Stationen=%s, Intervall=%ss",
        settings.mock_station_list,
        settings.ingestion_poll_interval_seconds,
    )
    async with httpx.AsyncClient() as client:
        while True:
            await poll_once(client)
            await asyncio.sleep(settings.ingestion_poll_interval_seconds)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(run_forever())
