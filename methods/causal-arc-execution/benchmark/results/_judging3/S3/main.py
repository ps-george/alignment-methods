"""URL Shortener Service - FastAPI backend."""

import logging
import random
import string
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from pydantic import BaseModel, HttpUrl, field_validator

from database import Database

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

db = Database()


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting URL Shortener Service")
    db.init()
    yield
    logger.info("Shutting down URL Shortener Service")


app = FastAPI(
    title="URL Shortener",
    description="A simple URL shortening service",
    version="1.0.0",
    lifespan=lifespan,
)


# --- Models ---

class ShortenRequest(BaseModel):
    url: HttpUrl

    @field_validator("url")
    @classmethod
    def validate_url(cls, v):
        url_str = str(v)
        if not url_str.startswith(("http://", "https://")):
            raise ValueError("URL must start with http:// or https://")
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


# --- Helpers ---

def generate_code(length: int = 6) -> str:
    """Generate a random alphanumeric short code."""
    chars = string.ascii_letters + string.digits
    return "".join(random.choices(chars, k=length))


def make_short_url(request: Request, code: str) -> str:
    base = str(request.base_url).rstrip("/")
    return f"{base}/{code}"


# --- Endpoints ---

@app.get("/", response_class=HTMLResponse)
async def index():
    """Serve the HTML frontend."""
    html_path = Path(__file__).parent / "static" / "index.html"
    return HTMLResponse(content=html_path.read_text())


@app.post(
    "/shorten",
    response_model=ShortenResponse,
    responses={422: {"model": ErrorResponse}},
)
async def shorten_url(body: ShortenRequest, request: Request):
    """Accept a URL and return a short code + full short URL."""
    original_url = str(body.url)
    logger.info("Shortening URL: %s", original_url)

    # Check if URL already exists
    existing = db.get_code_by_url(original_url)
    if existing:
        logger.info("URL already shortened, returning existing code: %s", existing)
        return ShortenResponse(
            code=existing,
            short_url=make_short_url(request, existing),
            original_url=original_url,
        )

    # Generate a unique code
    for _ in range(10):
        code = generate_code()
        if not db.get_url_by_code(code):
            break
    else:
        logger.error("Failed to generate a unique code after 10 attempts")
        raise HTTPException(status_code=500, detail="Could not generate unique code")

    db.create_mapping(code, original_url)
    logger.info("Created short code %s for URL %s", code, original_url)

    return ShortenResponse(
        code=code,
        short_url=make_short_url(request, code),
        original_url=original_url,
    )


@app.get(
    "/api/stats/{code}",
    response_model=StatsResponse,
    responses={404: {"model": ErrorResponse}},
)
async def get_stats(code: str):
    """Return JSON with click count and original URL for a given code."""
    logger.info("Fetching stats for code: %s", code)
    row = db.get_stats(code)
    if not row:
        logger.warning("Stats requested for unknown code: %s", code)
        raise HTTPException(
            status_code=404,
            detail=f"Short code '{code}' not found",
        )
    return StatsResponse(
        code=code,
        original_url=row["original_url"],
        click_count=row["click_count"],
    )


@app.get(
    "/{code}",
    responses={
        302: {"description": "Redirect to original URL"},
        404: {"model": ErrorResponse},
    },
)
async def redirect_to_url(code: str):
    """Redirect to the original URL for the given short code."""
    logger.info("Redirect request for code: %s", code)
    original_url = db.get_url_by_code(code)
    if not original_url:
        logger.warning("Redirect attempted for unknown code: %s", code)
        raise HTTPException(
            status_code=404,
            detail=f"Short code '{code}' not found",
        )
    db.increment_click(code)
    logger.info("Redirecting code %s to %s", code, original_url)
    return RedirectResponse(url=original_url, status_code=302)
