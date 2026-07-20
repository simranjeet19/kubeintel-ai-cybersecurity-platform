import time
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse

from app.logging_config import logger
from app.models import SummarizeRequest, SummarizeResponse
from app.summarizer import summarize_content


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("summarizer-api starting up")
    yield
    logger.info("summarizer-api shutting down")


app = FastAPI(
    title="KubeIntel Summarizer API",
    description="LLM-backed summarization for AI and cybersecurity research digests",
    version="1.0.0",
    lifespan=lifespan,
)


@app.middleware("http")
async def log_requests(request: Request, call_next):
    start = time.perf_counter()
    response = await call_next(request)
    duration_ms = round((time.perf_counter() - start) * 1000, 2)
    logger.info(
        "request",
        extra={
            "method": request.method,
            "path": request.url.path,
            "status": response.status_code,
            "duration_ms": duration_ms,
        },
    )
    return response


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/ready")
def ready():
    return {"status": "ready"}


@app.post("/summarize", response_model=SummarizeResponse)
async def summarize(request: SummarizeRequest):
    try:
        return await summarize_content(
            title=request.title,
            content=request.content,
            category=request.category,
        )
    except ValueError as e:
        logger.error("summarization parse error", extra={"error": str(e)})
        raise HTTPException(status_code=502, detail="Failed to parse LLM response")
    except Exception as e:
        logger.error("summarization failed", extra={"error": str(e)})
        raise HTTPException(status_code=500, detail="Internal summarization error")


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error("unhandled exception", extra={"error": str(exc), "path": request.url.path})
    return JSONResponse(status_code=500, content={"detail": "Internal server error"})
