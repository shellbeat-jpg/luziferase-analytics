from fastapi import APIRouter, HTTPException

from app.models.nowplaying import NowPlayingResponse
from app.simulation.simulator import get_simulated_nowplaying

router = APIRouter(prefix="/mock", tags=["mock-azuracast"])


@router.get("/nowplaying/{station_shortcode}", response_model=NowPlayingResponse)
async def mock_nowplaying(station_shortcode: str) -> NowPlayingResponse:
    """
    Simuliert den AzuraCast-Endpoint GET /api/nowplaying/{station}.
    Spaeter 1:1 durch die echte AzuraCast-Basis-URL ersetzbar, da der
    Ingestion-Worker nur diese Pydantic-Response-Struktur kennt, nicht
    die konkrete Quelle.
    """
    try:
        return get_simulated_nowplaying(station_shortcode)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
