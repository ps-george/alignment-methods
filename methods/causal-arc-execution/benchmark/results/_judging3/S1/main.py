"""URL Shortener Service - FastAPI Backend"""

import hashlib
import logging
import os
import time
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse
from pydantic import BaseModel, HttpUrl, field_validator

from database import Database

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# Database instance
db = Database()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage application lifespan - initialize DB on startup."""
    logger.info("Starting URL Shortener service")
    db.init_db()
    logger.info("Database initialized")
    yield
    logger.info("Shutting down URL Shortener service")


app = FastAPI(
    title="URL Shortener",
    description="A simple URL shortening service",
    version="1.0.0",
    lifespan=lifespan,
)


# --- Pydantic Models ---

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
    short_code: str
    short_url: str
    original_url: str


class StatsResponse(BaseModel):
    short_code: str
    original_url: str
    click_count: int


class ErrorResponse(BaseModel):
    error: str
    detail: str | None = None


# --- Helper ---

def generate_short_code(url: str) -> str:
    """Generate a short code from a URL using a hash."""
    timestamp = str(time.time())
    data = f"{url}{timestamp}"
    return hashlib.md5(data.encode()).hexdigest()[:7]


def get_base_url(request: Request) -> str:
    """Get the base URL from the request."""
    return str(request.base_url).rstrip("/")


# --- Endpoints ---

@app.post(
    "/shorten",
    response_model=ShortenResponse,
    status_code=201,
    responses={
        422: {"model": ErrorResponse, "description": "Validation error"},
        500: {"model": ErrorResponse, "description": "Internal server error"},
    },
)
async def shorten_url(body: ShortenRequest, request: Request):
    """Accept a URL and return a short code + full short URL."""
    original_url = str(body.url)
    logger.info("Shortening URL: %s", original_url)

    # Generate a unique short code
    max_attempts = 5
    for attempt in range(max_attempts):
        short_code = generate_short_code(original_url)
        if not db.get_url(short_code):
            break
        logger.debug("Collision on attempt %d, retrying", attempt + 1)
    else:
        logger.error("Failed to generate unique short code after %d attempts", max_attempts)
        raise HTTPException(status_code=500, detail="Could not generate unique short code")

    db.create_url(short_code, original_url)
    logger.info("Created short code %s for URL %s", short_code, original_url)

    base_url = get_base_url(request)
    short_url = f"{base_url}/{short_code}"

    return ShortenResponse(
        short_code=short_code,
        short_url=short_url,
        original_url=original_url,
    )


@app.get(
    "/api/stats/{code}",
    response_model=StatsResponse,
    responses={
        404: {"model": ErrorResponse, "description": "Short code not found"},
    },
)
async def get_stats(code: str):
    """Return JSON with click count and original URL for a short code."""
    logger.info("Stats requested for code: %s", code)
    row = db.get_url(code)
    if not row:
        logger.warning("Stats requested for unknown code: %s", code)
        raise HTTPException(status_code=404, detail=f"Short code '{code}' not found")

    return StatsResponse(
        short_code=code,
        original_url=row["original_url"],
        click_count=row["click_count"],
    )


@app.get(
    "/",
    response_class=HTMLResponse,
    include_in_schema=False,
)
async def index():
    """Serve the HTML frontend."""
    html_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "static", "index.html")
    with open(html_path, "r") as f:
        content = f.read()
    return HTMLResponse(content=content)


@app.get(
    "/{code}",
    responses={
        302: {"description": "Redirect to original URL"},
        404: {"model": ErrorResponse, "description": "Short code not found"},
    },
)
async def redirect_to_url(code: str):
    """Redirect to the original URL for a given short code."""
    logger.info("Redirect requested for code: %s", code)
    row = db.get_url(code)
    if not row:
        logger.warning("Redirect requested for unknown code: %s", code)
        raise HTTPException(status_code=404, detail=f"Short code '{code}' not found")

    db.increment_click(code)
    logger.info("Redirecting code %s to %s", code, row["original_url"])
    return RedirectResponse(url=row["original_url"], status_code=302)


# --- Custom exception handler for consistent error shape ---

@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    logger.error("HTTP error %d: %s", exc.status_code, exc.detail)
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": str(exc.detail), "detail": None},
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    logger.warning("Validation error: %s", str(exc))
    return JSONResponse(
        status_code=422,
        content={"error": "Validation error", "detail": str(exc)},
    )
