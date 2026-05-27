"""FastAPI application for the URL shortener service."""
from __future__ import annotations

import logging
import sqlite3
from pathlib import Path

from fastapi import FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field, HttpUrl

from . import shortcode
from .config import Settings, get_settings
from .db import Database

logger = logging.getLogger("shortener")
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s %(message)s",
)

STATIC_DIR = Path(__file__).resolve().parent.parent / "static"


# ---- schemas ---------------------------------------------------------------

class ShortenRequest(BaseModel):
    url: HttpUrl = Field(..., description="The URL to shorten.")


class ShortenResponse(BaseModel):
    code: str
    short_url: str
    url: str


class StatsResponse(BaseModel):
    code: str
    url: str
    clicks: int


class ErrorResponse(BaseModel):
    error: str
    detail: str | None = None


def _error(status: int, error: str, detail: str | None = None) -> JSONResponse:
    return JSONResponse(
        status_code=status,
        content={"error": error, "detail": detail},
    )


# ---- app factory -----------------------------------------------------------

def create_app(settings: Settings | None = None, db: Database | None = None) -> FastAPI:
    settings = settings or get_settings()
    db = db or Database(settings.db_path)

    app = FastAPI(
        title="URL Shortener",
        version="1.0.0",
        description="A small, production-quality URL shortener.",
    )
    app.state.settings = settings
    app.state.db = db

    # Static assets (CSS/JS) served from /static.
    if STATIC_DIR.exists():
        app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")

    # ---- error handlers --------------------------------------------------
    @app.exception_handler(RequestValidationError)
    async def _validation_handler(request: Request, exc: RequestValidationError):
        logger.info("validation error path=%s errors=%s", request.url.path, exc.errors())
        return _error(422, "validation_error", str(exc.errors()))

    @app.exception_handler(HTTPException)
    async def _http_handler(request: Request, exc: HTTPException):
        # Preserve redirects untouched (no body for 3xx from this path).
        return _error(exc.status_code, _slug(exc.status_code), str(exc.detail))

    # ---- routes ----------------------------------------------------------
    @app.get("/", response_class=HTMLResponse, include_in_schema=False)
    async def index() -> HTMLResponse:
        index_file = STATIC_DIR / "index.html"
        if not index_file.exists():
            return HTMLResponse("<h1>URL Shortener</h1>", status_code=200)
        return HTMLResponse(index_file.read_text(encoding="utf-8"))

    @app.get("/healthz", include_in_schema=False)
    async def healthz() -> dict:
        return {"status": "ok"}

    @app.post(
        "/shorten",
        response_model=ShortenResponse,
        responses={422: {"model": ErrorResponse}, 500: {"model": ErrorResponse}},
    )
    async def shorten(payload: ShortenRequest) -> ShortenResponse:
        url = str(payload.url)
        # De-duplicate: same URL gets same code.
        existing = db.get_by_url(url)
        if existing:
            logger.info("shorten reuse code=%s url=%s", existing, url)
            return ShortenResponse(
                code=existing,
                short_url=f"{settings.base_url.rstrip('/')}/{existing}",
                url=url,
            )

        last_error: Exception | None = None
        for _ in range(settings.max_collisions):
            code = shortcode.generate(settings.code_length)
            try:
                db.insert(code, url)
                logger.info("shorten created code=%s url=%s", code, url)
                return ShortenResponse(
                    code=code,
                    short_url=f"{settings.base_url.rstrip('/')}/{code}",
                    url=url,
                )
            except sqlite3.IntegrityError as exc:
                last_error = exc
                logger.warning("shorten collision code=%s; retrying", code)
                continue

        logger.error("shorten exhausted attempts: %s", last_error)
        raise HTTPException(status_code=500, detail="Could not allocate a unique code.")

    @app.get("/api/stats/{code}", response_model=StatsResponse,
             responses={404: {"model": ErrorResponse}})
    async def stats(code: str) -> StatsResponse:
        if not _valid_code(code):
            raise HTTPException(status_code=404, detail="code not found")
        result = db.get(code)
        if result is None:
            logger.info("stats miss code=%s", code)
            raise HTTPException(status_code=404, detail="code not found")
        url, clicks = result
        return StatsResponse(code=code, url=url, clicks=clicks)

    @app.get("/{code}", include_in_schema=False)
    async def redirect(code: str):
        if not _valid_code(code):
            raise HTTPException(status_code=404, detail="code not found")
        result = db.get(code)
        if result is None:
            logger.info("redirect miss code=%s", code)
            raise HTTPException(status_code=404, detail="code not found")
        url, _ = result
        db.increment_clicks(code)
        logger.info("redirect hit code=%s -> %s", code, url)
        return RedirectResponse(url=url, status_code=302)

    return app


def _valid_code(code: str) -> bool:
    if not code or len(code) > 64:
        return False
    return all(c.isalnum() for c in code)


def _slug(status: int) -> str:
    return {
        400: "bad_request",
        404: "not_found",
        422: "validation_error",
        500: "internal_error",
    }.get(status, "error")


# Module-level ASGI app for `uvicorn app.main:app`.
app = create_app()
