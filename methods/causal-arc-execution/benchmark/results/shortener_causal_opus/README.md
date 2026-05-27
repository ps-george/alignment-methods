# URL Shortener

A small but production-quality URL shortener: FastAPI + SQLite, HTML frontend,
Docker, and a thorough pytest suite.

## Features

- `POST /shorten` — accepts a JSON `{ "url": "..." }`, returns the short code and full short URL. Idempotent per input URL.
- `GET /{code}` — 302 redirect to the original URL; increments the click counter.
- `GET /api/stats/{code}` — JSON with `code`, `url`, `clicks`, `created_at`.
- `GET /` — HTML frontend with forms to shorten URLs and look up stats.
- SQLite persistence (WAL mode), survives restarts.
- Strict URL validation via Pydantic `HttpUrl`.
- Consistent error envelope: `{ "error": { "code", "message", "details" } }`.
- Structured logging at the request edges and the DB writes.

## Layout

```
shortener_causal_opus/
  app/
    main.py        # FastAPI app, routes, error handlers
    db.py          # SQLite wrapper
    shortener.py   # short-code generator
  static/
    index.html     # frontend
  tests/
    test_api.py    # full pytest suite
  Dockerfile
  docker-compose.yml
  requirements.txt
  requirements-dev.txt
  pytest.ini
```

## Quickstart (local Python)

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements-dev.txt
uvicorn app.main:app --reload
```

Open <http://localhost:8000>.

## Tests

```bash
pip install -r requirements-dev.txt
pytest
```

The suite covers: happy-path shorten + redirect + stats, click tracking,
invalid-URL 422, missing-field 422, unknown-code 404 on both `/{code}` and
`/api/stats/{code}`, frontend HTML served from `/`, idempotency of `/shorten`,
the consistent error envelope, and **persistence across restart** (an entire
fresh app instance against the same SQLite file sees prior codes and click
counts).

## Docker

Build and run:

```bash
docker compose up --build
```

The compose file mounts a named volume at `/data` so the SQLite database
persists across container restarts.

## Configuration

| Env var          | Default                | Meaning                                                |
|------------------|------------------------|--------------------------------------------------------|
| `SHORTENER_DB`   | `./data/shortener.db`  | Path to the SQLite file.                               |
| `BASE_URL`       | (derived from request) | Public base URL used when constructing `short_url`.    |
| `LOG_LEVEL`      | `INFO`                 | Standard logging level.                                |

## API examples

```bash
# Shorten
curl -s -X POST http://localhost:8000/shorten \
  -H 'Content-Type: application/json' \
  -d '{"url":"https://example.com/some/long/path"}'
# -> {"code":"aB3xY9z","short_url":"http://localhost:8000/aB3xY9z","url":"..."}

# Redirect (note: -L to follow)
curl -I http://localhost:8000/aB3xY9z

# Stats
curl -s http://localhost:8000/api/stats/aB3xY9z
# -> {"code":"aB3xY9z","url":"...","clicks":1,"created_at":"..."}
```

## Error shape

All non-2xx responses use:

```json
{ "error": { "code": "not_found", "message": "Unknown code: xyz", "details": null } }
```

`code` is one of: `bad_request`, `not_found`, `conflict`, `validation_error`, `error`.

## Notes & decisions

- **Code generation:** 7-char base62 (~3.5 trillion codes). Insert retries on collision; effectively never triggers at realistic scale.
- **Idempotency:** Re-shortening the same URL returns the existing code. This avoids unbounded growth from duplicates and is the behavior most users expect.
- **Reserved paths:** `shorten`, `api`, `static`, `docs`, `openapi.json`, `redoc`, `favicon.ico` are reserved and won't be issued as codes (the generator is random alphanumeric, but the redirect route also refuses them defensively).
- **Concurrency:** SQLite is opened with WAL and `BEGIN IMMEDIATE` for writes; sufficient for single-node deployments. For scale-out, swap `db.py` for a Postgres backend behind the same interface.
