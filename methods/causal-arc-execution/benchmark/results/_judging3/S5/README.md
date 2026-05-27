# URL Shortener

A small, production-quality URL shortener built with **FastAPI** and **SQLite**.

## Features

- `POST /shorten` — accepts JSON `{"url": "..."}`, returns short code + short URL
- `GET /{code}` — 302 redirect to the original URL, increments click counter
- `GET /api/stats/{code}` — JSON with `{code, url, clicks}`
- HTML frontend at `/` with shorten + stats forms
- SQLite persistence (URL mapping + click counts)
- Consistent JSON error responses: `{"error": "...", "detail": "..."}`
- URL validation via `pydantic.HttpUrl` (only `http`/`https`)
- Structured logging at all interesting events
- Dockerfile + docker-compose for local dev
- Comprehensive pytest suite (endpoints, validation, 404s, persistence-across-restart)

## Project layout

```
app/
  main.py        FastAPI app + routes
  db.py          SQLite wrapper
  shortcode.py   Random short-code generator
  config.py      Settings (env-driven)
static/          Frontend (index.html, style.css, app.js)
tests/           pytest suite
Dockerfile
docker-compose.yml
requirements.txt
```

## Quick start (local)

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements-dev.txt
uvicorn app.main:app --reload
```

Then open <http://localhost:8000/>.

## Run the tests

```bash
pip install -r requirements-dev.txt
pytest
```

## Quick start (Docker)

```bash
docker compose up --build
```

The service listens on port 8000 and persists the SQLite database in the named
volume `shortener_data` (mounted at `/data` inside the container).

## API

### `POST /shorten`

```bash
curl -X POST http://localhost:8000/shorten \
  -H 'Content-Type: application/json' \
  -d '{"url": "https://example.com/very/long/path"}'
```

```json
{
  "code": "aB3xZ9q",
  "short_url": "http://localhost:8000/aB3xZ9q",
  "url": "https://example.com/very/long/path"
}
```

Shortening the same URL twice returns the same code (idempotent).

### `GET /{code}`

Returns `302 Found` with `Location: <original_url>` and increments the click
counter. Unknown codes return `404`.

### `GET /api/stats/{code}`

```bash
curl http://localhost:8000/api/stats/aB3xZ9q
```

```json
{ "code": "aB3xZ9q", "url": "https://example.com/very/long/path", "clicks": 7 }
```

### Error shape

All non-redirect error responses use the same shape:

```json
{ "error": "validation_error", "detail": "..." }
```

with `error` one of `validation_error`, `not_found`, `bad_request`,
`internal_error`.

## Configuration (env vars)

| Variable | Default | Purpose |
|---|---|---|
| `SHORTENER_DB_PATH` | `data/shortener.db` | SQLite file path |
| `SHORTENER_BASE_URL` | `http://localhost:8000` | Base URL used to build `short_url` |
| `SHORTENER_CODE_LENGTH` | `7` | Length of generated short codes |
