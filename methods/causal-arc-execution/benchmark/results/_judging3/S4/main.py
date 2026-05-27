"""URL Shortener Service — FastAPI backend with SQLite persistence."""

import hashlib
import logging
import os
import time
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse
from pydantic import BaseModel, HttpUrl, field_validator

from db import Database

# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger("shortener")

# ---------------------------------------------------------------------------
# Database singleton
# ---------------------------------------------------------------------------
DB_PATH = Path(os.environ.get("DB_PATH", "urls.db"))
db: Database


@asynccontextmanager
async def lifespan(app: FastAPI):
    global db
    logger.info("Starting URL shortener service")
    db = Database(DB_PATH)
    db.initialize()
    logger.info("Database ready at %s", DB_PATH)
    yield
    logger.info("Shutting down URL shortener service")


# ---------------------------------------------------------------------------
# App
# ---------------------------------------------------------------------------
app = FastAPI(
    title="URL Shortener",
    description="A simple, production-quality URL shortener",
    version="1.0.0",
    lifespan=lifespan,
)


# ---------------------------------------------------------------------------
# Schemas
# ---------------------------------------------------------------------------
class ShortenRequest(BaseModel):
    url: HttpUrl

    @field_validator("url")
    @classmethod
    def url_must_be_http_or_https(cls, v: HttpUrl) -> HttpUrl:
        if v.scheme not in ("http", "https"):
            raise ValueError("URL must use http or https scheme")
        return v


class ShortenResponse(BaseModel):
    code: str
    short_url: str
    original_url: str


class StatsResponse(BaseModel):
    code: str
    original_url: str
    click_count: int


class ErrorResponse(BaseModel):
    error: str
    detail: str | None = None


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
def _make_code(url: str) -> str:
    """Generate a 7-character URL-safe code from the URL + current nanoseconds."""
    raw = f"{url}{time.time_ns()}"
    digest = hashlib.sha256(raw.encode()).hexdigest()
    return digest[:7]


def _base_url(request: Request) -> str:
    return str(request.base_url).rstrip("/")


# ---------------------------------------------------------------------------
# Error handler — consistent shape for all HTTP exceptions
# ---------------------------------------------------------------------------
@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": exc.detail, "detail": None},
    )


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------
@app.get("/", response_class=HTMLResponse)
async def index():
    """Serve the HTML frontend."""
    html_path = Path(__file__).parent / "static" / "index.html"
    return HTMLResponse(content=html_path.read_text(), status_code=200)


@app.post("/shorten", response_model=ShortenResponse, status_code=201)
async def shorten(body: ShortenRequest, request: Request):
    """Accept a URL and return a short code + full short URL."""
    original = str(body.url)
    logger.info("Shortening URL: %s", original)

    # Check for an existing mapping to keep things idempotent-ish
    existing = db.get_by_original_url(original)
    if existing:
        code = existing["code"]
        logger.info("Reusing existing code %s for URL", code)
    else:
        code = _make_code(original)
        # Retry on the unlikely collision
        while db.get_by_code(code) is not None:
            code = _make_code(original)
        db.insert(code, original)
        logger.info("Created new short code %s", code)

    short_url = f"{_base_url(request)}/{code}"
    return ShortenResponse(code=code, short_url=short_url, original_url=original)


@app.get("/api/stats/{code}", response_model=StatsResponse)
async def stats(code: str):
    """Return click count and original URL for a code."""
    row = db.get_by_code(code)
    if row is None:
        logger.warning("Stats requested for unknown code: %s", code)
        raise HTTPException(status_code=404, detail=f"Code '{code}' not found")
    return StatsResponse(
        code=code,
        original_url=row["original_url"],
        click_count=row["click_count"],
    )


@app.get("/{code}")
async def redirect(code: str):
    """Redirect to the original URL, incrementing the click count."""
    row = db.get_by_code(code)
    if row is None:
        logger.warning("Redirect requested for unknown code: %s", code)
        raise HTTPException(status_code=404, detail=f"Code '{code}' not found")
    db.increment_clicks(code)
    logger.info("Redirecting code %s -> %s", code, row["original_url"])
    return RedirectResponse(url=row["original_url"], status_code=302)
