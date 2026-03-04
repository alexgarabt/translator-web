from typing import Literal

from pydantic import BaseModel, Field


class TranslateRequest(BaseModel):
    text: str = Field(..., min_length=1, max_length=500)
    method: Literal["greedy", "beam"] = "beam"
    beam_width: int = Field(default=5, ge=1, le=20)


class TranslateResponse(BaseModel):
    translation: str
    method: str
    source_language: str = "en"
    target_language: str = "es"


class HealthResponse(BaseModel):
    status: str
    device: str
    model_loaded: bool
