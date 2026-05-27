# URL Shortener

A small, production-shaped URL shortener: FastAPI + SQLite + an HTML frontend, with Docker packaging and a pytest suite.

## Features

- `POST /shorten` — accepts `{"url": "..."}`, returns `{code, short_url, original_url}`
- `GET /{code}` — 302 redirect to the original URL, increments a click counter
- `GET /api/stats/{code}` — JSON with the code, original URL, click count, and creation time
- `GET /` — HTML page with two forms (shorten + look up stats)
- `GET /healthz` — liveness probe
- SQLite persistence (mapping + click counts) in WAL mode
- Consistent error shape: `{"error": {"code": "...", "message": "..."}}`
- URL validation via Pydantic `HttpUrl`
- Structured logging at INFO

## Layout

```
app/
  main.py        # FastAPI app factory + routes
  db.py          # SQLite wrapper
  shortener.py   # short-code generator
static/
  index.html     # frontend served at /
tests/
  test_api.py    # endpoint + persistence tests
Dockerfile
docker-compose.yml
requirements.txt
```

## Local development

Requires Python 3.11+.

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# Run the server
uvicorn app.main:app --reload --port 8000
```

Open <http://localhost:8000/> for the frontend, or hit the API directly:

```bash
curl -X POST http://localhost:8000/shorten \
     -H 'Content-Type: application/json' \
     -d '{"url":"https://example.com/some/long/path"}'
# -> {"code":"abc1234","short_url":"http://localhost:8000/abc1234","original_url":"..."}

curl -i http://localhost:8000/abc1234
# -> HTTP/1.1 302 Found ... location: https://example.com/...

curl http://localhost:8000/api/stats/abc1234
# -> {"code":"abc1234","original_url":"...","clicks":1,"created_at":"..."}
```

## Configuration

Environment variables:

| Variable             | Default          | Description                       |
|----------------------|------------------|-----------------------------------|
| `SHORTENER_DB_PATH`  | `shortener.db`   | Path to the SQLite database file. |
| `LOG_LEVEL`          | `INFO`           | Python logging level.             |

## Tests

```bash
pip install -r requirements.txt
pytest
```

The suite covers:
- success path for `/shorten`, `/{code}`, `/api/stats/{code}`
- input validation (invalid URL, missing field)
- 404 for unknown codes (both redirect and stats)
- click-count increment across multiple hits
- persistence across an app/database restart (same SQLite file, new `Database` + app instance)
- HTML index served at `/`
- health endpoint

## Docker

Build and run the image directly:

```bash
docker build -t shortener:local .
docker run --rm -p 8000:8000 -v shortener-data:/data shortener:local
```

Or use compose for local dev:

```bash
docker compose up --build
```

The SQLite database lives in the `shortener-data` named volume at `/data/shortener.db`, so click counts and mappings survive container restarts.

## Error shape

All error responses use the same envelope:

```json
{ "error": { "code": "not_found", "message": "code 'xyz' not found" } }
```

Codes: `validation_error` (422), `not_found` (404), `bad_request` (400), `internal_error` (500).
