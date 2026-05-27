"""FastAPI URL shortener application."""
from __future__ import annotations

import logging
import os
from pathlib import Path
from typing import Optional

from fastapi import Depends, FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, HttpUrl, ValidationError

from .db import Database
from .shortener import generate_code

logging.basicConfig(
    level=os.environ.get("LOG_LEVEL", "INFO"),
    format="%(asctime)s %(levelname)s %(name)s %(message)s",
)
logger = logging.getLogger("shortener")

STATIC_DIR = Path(__file__).resolve().parent.parent / "static"

MAX_INSERT_ATTEMPTS = 8


def _error(code: str, message: str, status: int) -> JSONResponse:
    """Consistent error response shape."""
    return JSONResponse(
        status_code=status,
        content={"error": {"code": code, "message": message}},
    )


class ShortenRequest(BaseModel):
    url: HttpUrl


class ShortenResponse(BaseModel):
    code: str
    short_url: str
    original_url: str


class StatsResponse(BaseModel):
    code: str
    original_url: str
    clicks: int
    created_at: str


def create_app(db: Optional[Database] = None) -> FastAPI:
    app = FastAPI(title="URL Shortener", version="1.0.0")

    # Dependency-injectable DB; tests override this.
    state_db = db if db is not None else Database()
    app.state.db = state_db

    def get_db() -> Database:
        return app.state.db

    if STATIC_DIR.exists():
        app.mount(
            "/static", StaticFiles(directory=str(STATIC_DIR)), name="static"
        )

    @app.exception_handler(ValidationError)
    async def _validation_handler(_: Request, exc: ValidationError):  # noqa: ANN001
        return _error("validation_error", str(exc), 422)

    @app.exception_handler(RequestValidationError)
    async def _req_validation_handler(_: Request, exc: RequestValidationError):  # noqa: ANN001
        return JSONResponse(
            status_code=422,
            content={
                "error": {
                    "code": "validation_error",
                    "message": "request validation failed",
                    "details": exc.errors(),
                }
            },
        )

    @app.exception_handler(HTTPException)
    async def _http_handler(_: Request, exc: HTTPException):  # noqa: ANN001
        # Don't override redirects.
        if 300 <= exc.status_code < 400:
            raise exc
        code = {
            400: "bad_request",
            404: "not_found",
            422: "validation_error",
            500: "internal_error",
        }.get(exc.status_code, "error")
        return _error(code, str(exc.detail), exc.status_code)

    @app.get("/", response_class=HTMLResponse)
    async def index() -> HTMLResponse:
        index_path = STATIC_DIR / "index.html"
        if not index_path.exists():
            return HTMLResponse("<h1>URL Shortener</h1>")
        return HTMLResponse(index_path.read_text(encoding="utf-8"))

    @app.get("/healthz")
    async def healthz() -> dict:
        return {"status": "ok"}

    @app.post("/shorten", response_model=ShortenResponse)
    async def shorten(
        payload: ShortenRequest,
        request: Request,
        database: Database = Depends(get_db),
    ) -> ShortenResponse:
        url = str(payload.url)
        # Try a few times to avoid the (extremely unlikely) collision.
        for attempt in range(MAX_INSERT_ATTEMPTS):
            code = generate_code()
            try:
                database.insert(code, url)
                break
            except Exception as exc:  # sqlite3.IntegrityError on collision
                if "UNIQUE" in str(exc) and attempt < MAX_INSERT_ATTEMPTS - 1:
                    logger.warning("code collision on %s, retrying", code)
                    continue
                logger.exception("failed to insert shortened URL")
                raise HTTPException(status_code=500, detail="failed to store URL")
        else:  # pragma: no cover
            raise HTTPException(status_code=500, detail="failed to allocate code")

        base = str(request.base_url).rstrip("/")
        short_url = f"{base}/{code}"
        logger.info("shortened url=%s code=%s", url, code)
        return ShortenResponse(code=code, short_url=short_url, original_url=url)

    @app.get("/api/stats/{code}", response_model=StatsResponse)
    async def stats(code: str, database: Database = Depends(get_db)) -> StatsResponse:
        row = database.get(code)
        if row is None:
            logger.info("stats miss code=%s", code)
            raise HTTPException(status_code=404, detail=f"code '{code}' not found")
        return StatsResponse(
            code=row["code"],
            original_url=row["url"],
            clicks=row["clicks"],
            created_at=row["created_at"],
        )

    @app.get("/{code}")
    async def redirect(code: str, database: Database = Depends(get_db)):
        # Avoid clashing with known top-level paths.
        if code in {"shorten", "healthz", "static", "api", "docs", "openapi.json", "redoc"}:
            raise HTTPException(status_code=404, detail="not found")
        row = database.get(code)
        if row is None:
            logger.info("redirect miss code=%s", code)
            raise HTTPException(status_code=404, detail=f"code '{code}' not found")
        database.increment_clicks(code)
        logger.info("redirect hit code=%s -> %s", code, row["url"])
        return RedirectResponse(url=row["url"], status_code=302)

    return app


app = create_app()
