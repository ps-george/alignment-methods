# URL Shortener

A production-quality URL shortening service built with FastAPI, SQLite, and a clean HTML frontend.

## Features

- Shorten any valid HTTP/HTTPS URL to a 6-character alphanumeric code
- 302 redirect via short code
- Per-code click tracking
- SQLite persistence (survives restarts)
- Clean HTML frontend served at `/`
- Consistent JSON error responses
- Structured logging throughout

---

## Quick Start

### Option 1: Local Python

```bash
# Install dependencies
pip install -r requirements.txt

# Run the server
uvicorn main:app --reload --port 8000
```

Open http://localhost:8000 in your browser.

### Option 2: Docker Compose

```bash
docker-compose up --build
```

The service will be available at http://localhost:8000. Data persists in the `shortener_data` Docker volume.

### Option 3: Docker (manual)

```bash
docker build -t url-shortener .
docker run -p 8000:8000 -v $(pwd)/data:/data url-shortener
```

---

## API Reference

### `POST /shorten`

Shorten a URL.

**Request body:**
```json
{ "url": "https://example.com/very/long/path" }
```

**Response (200):**
```json
{
  "code": "aB3xYz",
  "short_url": "http://localhost:8000/aB3xYz",
  "original_url": "https://example.com/very/long/path"
}
```

**Errors:**
- `422 Unprocessable Entity` — URL is missing, empty, or not a valid http/https URL.

---

### `GET /{code}`

Redirects (302) to the original URL. Also increments the click counter.

**Errors:**
- `404 Not Found` — code does not exist.

---

### `GET /api/stats/{code}`

Returns click statistics for a short code.

**Response (200):**
```json
{
  "code": "aB3xYz",
  "original_url": "https://example.com/very/long/path",
  "click_count": 42
}
```

**Errors:**
- `404 Not Found` — code does not exist.

---

## Running Tests

```bash
pytest tests/ -v
```

All tests use isolated temporary SQLite databases — no shared state between test runs.

---

## Configuration

| Environment Variable | Default | Description |
|---|---|---|
| `DB_PATH` | `shortener.db` | Path to the SQLite database file |

---

## Project Structure

```
.
├── main.py              # FastAPI application and endpoints
├── database.py          # SQLite database layer
├── static/
│   └── index.html       # HTML frontend
├── tests/
│   └── test_api.py      # pytest test suite
├── requirements.txt
├── Dockerfile
├── docker-compose.yml
└── README.md
```
