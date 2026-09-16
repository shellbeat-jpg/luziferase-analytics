from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy import MetaData, Table, Column, Integer, String, BigInteger, JSON, DateTime, func
from sqlalchemy.schema import CreateSchema

from app.config import settings

engine = create_async_engine(settings.database_url, pool_pre_ping=True)
async_session = async_sessionmaker(engine, expire_on_commit=False)

metadata = MetaData(schema="raw")

# Staging-Tabelle fuer rohe Now-Playing-Events. dbt (Woche 2) baut darauf auf.
raw_nowplaying_events = Table(
    "nowplaying_events",
    metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("station_shortcode", String, nullable=False, index=True),
    Column("polled_at", DateTime(timezone=True), server_default=func.now(), nullable=False),
    Column("listeners_current", Integer, nullable=False),
    Column("listeners_unique", Integer, nullable=False),
    Column("track_artist", String, nullable=False),
    Column("track_title", String, nullable=False),
    Column("track_genre", String, nullable=True),
    Column("played_at_unix", BigInteger, nullable=False),
    Column("raw_payload", JSON, nullable=False),
)


async def init_db() -> None:
    async with engine.begin() as conn:
        await conn.execute(CreateSchema("raw", if_not_exists=True))
        await conn.run_sync(metadata.create_all)
