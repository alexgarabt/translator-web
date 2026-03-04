import torch
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    device: str = "cuda" if torch.cuda.is_available() else "cpu"
    hf_cache_dir: str = "hub_cache"
    cors_origins: list[str] = [
        "http://localhost:5173",
        "http://cognito",
        "http://cognito:5173",
    ]
    default_beam_width: int = 5
    max_input_length: int = 500

    model_config = {"env_prefix": "TRANSLATOR_"}


settings = Settings()
