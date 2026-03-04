import logging
from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from .config import settings
from .schemas import HealthResponse, TranslateRequest, TranslateResponse
from .translator import TranslatorService

logger = logging.getLogger(__name__)

translator_service = TranslatorService(
    device=settings.device,
    cache_dir=settings.hf_cache_dir,
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Loading translator model on %s...", settings.device)
    translator_service.load()
    logger.info("Model loaded successfully.")
    yield


app = FastAPI(
    title="LSTM Translator API",
    description="EN→ES translation using a custom LSTM seq2seq model",
    version="0.1.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_methods=["POST", "GET"],
    allow_headers=["*"],
)


def get_translator() -> TranslatorService:
    if not translator_service.is_loaded:
        raise HTTPException(503, "Model not loaded yet")
    return translator_service


@app.post("/api/translate", response_model=TranslateResponse)
def translate(
    request: TranslateRequest,
    service: TranslatorService = Depends(get_translator),
):
    translation = service.translate(
        text=request.text,
        method=request.method,
        beam_width=request.beam_width,
    )
    return TranslateResponse(translation=translation, method=request.method)


@app.get("/api/health", response_model=HealthResponse)
def health():
    return HealthResponse(
        status="ok",
        device=settings.device,
        model_loaded=translator_service.is_loaded,
    )
