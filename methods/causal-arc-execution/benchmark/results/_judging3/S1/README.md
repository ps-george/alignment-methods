# URL Shortener

A production-quality URL shortening service built with FastAPI and SQLite.

## Features

- Shorten any valid HTTP/HTTPS URL to a 7-character code
- Automatic 302 redirect via short code
- Per-URL click tracking
- HTML frontend (no build step required)
- SQLite persistence with volume mount for Docker
- Consistent JSON error responses

## Quick Start

### With Docker Compose (recommended)

```bash
docker compose up --build
```

The service will be available at http://localhost:8000.

### Local Development

**Requirements:** Python 3.11+

```bash
# Create and activate a virtual environment
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run the server
uvicorn main:app --reload
```

The service will be available at http://localhost:8000.

## API Reference

### POST /shorten

Accepts a URL and returns a short code plus the full short URL.

**Request body (JSON):**
```json
{ "url": "https://example.com/very/long/path" }
```

**Response (201):**
```json
{
  "short_code": "a1b2c3d",
  "short_url": "http://localhost:8000/a1b2c3d",
  "original_url": "https://example.com/very/long/path"
}
```

**Validation errors (422):**
```json
{ "error": "Validation error", "detail": "..." }
```

### GET /{code}

Redirects (302) to the original URL. Increments the click counter.

**404 response:**
```json
{ "error": "Short code 'xyz' not found", "detail": null }
```

### GET /api/stats/{code}

Returns click statistics for a short code.

**Response (200):**
```json
{
  "short_code": "a1b2c3d",
  "original_url": "https://example.com/very/long/path",
  "click_count": 42
}
```

**404 response:**
```json
{ "error": "Short code 'xyz' not found", "detail": null }
```

## Running Tests

```bash
# From the project root with the virtualenv active
pytest tests/ -v
```

Expected output:

```
tests/test_api.py::TestShortenEndpoint::test_shorten_valid_url PASSED
tests/test_api.py::TestShortenEndpoint::test_shorten_returns_full_short_url PASSED
...
```

## Configuration

| Environment Variable | Default    | Description                       |
|----------------------|------------|-----------------------------------|
| `DB_PATH`            | `urls.db`  | Path to the SQLite database file  |

## Project Structure

```
.
├── main.py            # FastAPI app, routes, request/response models
├── database.py        # SQLite wrapper
├── static/
│   └── index.html     # HTML frontend
├── tests/
│   └── test_api.py    # pytest test suite
├── requirements.txt
├── Dockerfile
├── docker-compose.yml
└── README.md
```

## Architecture Notes

- **Short code generation:** MD5 hash of `url + timestamp`, truncated to 7 characters. Collision retry loop ensures uniqueness.
- **Click tracking:** Atomic `UPDATE` on redirect; count stored in the `urls` table.
- **Persistence:** SQLite file path is configurable via `DB_PATH`. Docker Compose mounts a named volume at `/data` so data survives container restarts.
- **Error shape:** All error responses share `{ "error": "...", "detail": null | "..." }`.
