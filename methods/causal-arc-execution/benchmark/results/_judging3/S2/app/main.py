"""URL shortener FastAPI app."""
from __future__ import annotations

import logging
import os
from pathlib import Path
from typing import Optional

from fastapi import Depends, FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field, HttpUrl, ValidationError

from .db import Database
from .shortener import generate_code

logging.basicConfig(
    level=os.environ.get("LOG_LEVEL", "INFO"),
    format="%(asctime)s %(levelname)s %(name)s %(message)s",
)
log = logging.getLogger("shortener")

BASE_DIR = Path(__file__).resolve().parent.parent
STATIC_DIR = BASE_DIR / "static"
DB_PATH = os.environ.get("SHORTENER_DB", str(BASE_DIR / "data" / "shortener.db"))
BASE_URL = os.environ.get("BASE_URL", "")  # e.g. http://localhost:8000; falls back to request URL


def _ensure_db_dir(path: str) -> None:
    p = Path(path)
    if p.parent and not p.parent.exists():
        p.parent.mkdir(parents=True, exist_ok=True)


# ---- schemas ----
class ShortenRequest(BaseModel):
    url: HttpUrl = Field(..., description="The URL to shorten")


class ShortenResponse(BaseModel):
    code: str
    short_url: str
    url: str


class StatsResponse(BaseModel):
    code: str
    url: str
    clicks: int
    created_at: str


class ErrorBody(BaseModel):
    code: str
    message: str
    details: Optional[dict] = None


def err(status: int, code: str, message: str, details: Optional[dict] = None) -> JSONResponse:
    return JSONResponse(
        status_code=status,
        content={"error": {"code": code, "message": message, "details": details}},
    )


def create_app(db_path: Optional[str] = None) -> FastAPI:
    path = db_path or DB_PATH
    _ensure_db_dir(path)
    db = Database(path)
    log.info("database initialized at %s", path)

    app = FastAPI(
        title="URL Shortener",
        version="1.0.0",
        description="A small but production-quality URL shortener service.",
    )
    app.state.db = db

    # ---- exception handlers (consistent error shape) ----
    @app.exception_handler(HTTPException)
    async def _http_exc(_req: Request, exc: HTTPException):
        code_map = {400: "bad_request", 404: "not_found", 409: "conflict", 422: "validation_error"}
        return err(exc.status_code, code_map.get(exc.status_code, "error"), str(exc.detail))

    @app.exception_handler(ValidationError)
    async def _pyd_exc(_req: Request, exc: ValidationError):
        return err(422, "validation_error", "Request validation failed", {"errors": exc.errors()})

    # Override FastAPI's default 422 to keep the shape consistent
    from fastapi.exceptions import RequestValidationError

    @app.exception_handler(RequestValidationError)
    async def _req_val_exc(_req: Request, exc: RequestValidationError):
        return err(422, "validation_error", "Request validation failed", {"errors": exc.errors()})

    # ---- routes ----
    @app.get("/", response_class=HTMLResponse)
    async def index() -> HTMLResponse:
        index_path = STATIC_DIR / "index.html"
        return HTMLResponse(index_path.read_text(encoding="utf-8"))

    if STATIC_DIR.exists():
        app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")

    def _short_url(request: Request, code: str) -> str:
        if BASE_URL:
            return f"{BASE_URL.rstrip('/')}/{code}"
        return str(request.url_for("redirect_code", code=code))

    @app.post("/shorten", response_model=ShortenResponse, status_code=201)
    async def shorten(payload: ShortenRequest, request: Request) -> ShortenResponse:
        url = str(payload.url)
        existing = db.get_by_url(url)
        if existing is not None:
            log.info("reusing existing code=%s for url=%s", existing["code"], url)
            return ShortenResponse(
                code=existing["code"],
                short_url=_short_url(request, existing["code"]),
                url=url,
            )
        # collision-resistant insert; retry a small number of times
        for _ in range(8):
            code = generate_code()
            if db.get_by_code(code) is None:
                try:
                    db.insert(code, url)
                except Exception as e:  # uniqueness race
                    log.warning("insert collision retry: %s", e)
                    continue
                log.info("shortened url=%s -> code=%s", url, code)
                return ShortenResponse(code=code, short_url=_short_url(request, code), url=url)
        raise HTTPException(status_code=500, detail="Could not allocate a unique code")

    @app.get("/api/stats/{code}", response_model=StatsResponse)
    async def stats(code: str) -> StatsResponse:
        row = db.get_by_code(code)
        if row is None:
            log.info("stats miss code=%s", code)
            raise HTTPException(status_code=404, detail=f"Unknown code: {code}")
        return StatsResponse(
            code=row["code"],
            url=row["url"],
            clicks=row["clicks"],
            created_at=row["created_at"],
        )

    @app.get("/{code}", name="redirect_code")
    async def redirect_code(code: str):
        # Reserved names - let other routes win; this catches anything else.
        if code in {"shorten", "api", "static", "docs", "openapi.json", "redoc", "favicon.ico"}:
            raise HTTPException(status_code=404, detail=f"Unknown code: {code}")
        row = db.get_by_code(code)
        if row is None:
            log.info("redirect miss code=%s", code)
            raise HTTPException(status_code=404, detail=f"Unknown code: {code}")
        db.increment_clicks(code)
        log.info("redirect code=%s -> %s", code, row["url"])
        return RedirectResponse(url=row["url"], status_code=302)

    return app


app = create_app()
