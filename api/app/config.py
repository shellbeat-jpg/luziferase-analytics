from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    database_url: str
    lastfm_api_key: str = ""
    mock_stations: str = "luziferase"
    ingestion_poll_interval_seconds: int = 30

    @property
    def mock_station_list(self) -> list[str]:
        return [s.strip() for s in self.mock_stations.split(",") if s.strip()]


settings = Settings()
