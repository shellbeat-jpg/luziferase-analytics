import asyncio
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.db import init_db
from app.ingestion.worker import run_forever
from app.routers import health, mock_nowplaying

logging.basicConfig(level=logging.INFO)


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    worker_task = asyncio.create_task(run_forever())
    yield
    worker_task.cancel()


app = FastAPI(
    title="Luziferase Analytics API",
    description="Ingestion + Auslieferung der Now-Playing-/Hoererdaten (Woche 1: Mock-Quelle)",
    version="0.1.0",
    lifespan=lifespan,
)

app.include_router(health.router)
app.include_router(mock_nowplaying.router)


@app.get("/")
async def root() -> dict:
    return {"service": "luziferase-analytics-api", "status": "running"}
