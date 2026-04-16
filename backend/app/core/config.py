from __future__ import annotations

from pydantic import BaseModel


class Settings(BaseModel):
    app_name: str = "Code Understanding MVP Backend"
    app_version: str = "0.1.0"
    api_prefix: str = "/api"


settings = Settings()
