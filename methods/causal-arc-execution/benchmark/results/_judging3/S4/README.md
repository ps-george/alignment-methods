# URL Shortener

A production-quality URL shortener built with FastAPI, SQLite, and a vanilla-JS frontend.

---

## Features

- Shorten any `http://` or `https://` URL to a 7-character code
- 302 redirect via `/{code}`
- Per-code click-count stats at `/api/stats/{code}`
- HTML frontend served at `/`
- SQLite persistence with WAL mode
- Idempotent: the same long URL always returns the same short code
- Consistent JSON error shape for all 4xx responses

---

## Local development (without Docker)

### Prerequisites

- Python 3.12+

### Setup

```bash
# 1. Create and activate a virtual environment
python -m venv .venv
source .venv/bin/activate       # Windows: .venv\Scripts\activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Run the server
uvicorn main:app --reload
```

The service is now running at http://localhost:8000.

### Environment variables

| Variable  | Default    | Description                   |
|-----------|------------|-------------------------------|
| `DB_PATH` | `urls.db`  | Path to the SQLite database   |

---

## Docker

### Build and run with Docker

```bash
docker build -t url-shortener .
docker run -p 8000:8000 -v shortener_data:/data url-shortener
```

### docker-compose (recommended for local dev)

```bash
docker compose up --build
```

This starts the service on port 8000 with a named volume for persistent storage.

---

## API Reference

### `POST /shorten`

Accepts a JSON body with a `url` field and returns a short code.

**Request**
```json
{ "url": "https://example.com/very/long/path" }
```

**Response `201`**
```json
{
  "code": "a3f9b12",
  "short_url": "http://localhost:8000/a3f9b12",
  "original_url": "https://example.com/very/long/path"
}
```

**Error `422`** — URL is missing, empty, or not a valid http/https URL.

---

### `GET /{code}`

Redirects (302) to the original URL and increments the click counter.

**Error `404`** — code not found.

---

### `GET /api/stats/{code}`

Returns click statistics for the given code.

**Response `200`**
```json
{
  "code": "a3f9b12",
  "original_url": "https://example.com/very/long/path",
  "click_count": 42
}
```

**Error `404`** — code not found.

---

### Error shape

All error responses share a consistent JSON structure:

```json
{ "error": "Human-readable message", "detail": null }
```

---

## Running tests

```bash
# With virtual environment active
pytest -v
```

The test suite covers:

- `POST /shorten`: success, idempotency, 7-char codes, URL validation (missing body, empty string, non-URL, ftp:// scheme, http:// and https:// acceptance, wrong field name)
- `GET /{code}`: 302 redirect, click-count increment, 404 on unknown code, error shape
- `GET /api/stats/{code}`: stats at zero, stats after redirects, 404 on unknown code, error shape
- Persistence: data survives a simulated restart (two separate Database instances, same file)
- Frontend: `GET /` returns HTML
