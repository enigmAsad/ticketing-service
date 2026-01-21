# Ticketing Service

FastAPI service for an in-memory concert ticketing system. It supports event
creation, seat availability queries, and seat bookings with concurrency-safe
reservation logic.

## Features
- Create and list events
- Check seat availability by event
- Reserve one or more seats per booking
- In-memory storage (no external database)
- Rate limiting, request-size guard, and structured error responses

## Tech Stack
- Python 3.12
- FastAPI
- Uvicorn
- Pytest

## Requirements
- Python 3.12 (see `.python-version`)
- `uv` package manager (recommended)

## Install
```bash
cd "ticketing-service"
uv sync
```

## Run
```bash
cd "ticketing-service"
uv run uvicorn ticketing_service.main:app --reload
```

The API will be available at `http://127.0.0.1:8000`.

## API Documentation
OpenAPI and Swagger UI are available at:
- `http://127.0.0.1:8000/docs`
- `http://127.0.0.1:8000/openapi.json`

Seat availability defaults to counts only. Use:
- `?detail=list&offset=0&limit=1000` for a page of available seats
- `?detail=range` for compact ranges

## Example Requests

Create an event:
```json
{
  "name": "City Lights Live",
  "starts_at": "2026-02-01T19:30:00Z",
  "venue": "Downtown Arena",
  "total_seats": 100
}
```

Create a booking:
```json
{
  "event_id": "c6d0bd52-6b79-4a7b-9b02-8c1c7a9dfb47",
  "seats": [1, 2, 3]
}
```

## Testing
```bash
cd "ticketing-service"
uv sync --extra test
uv run pytest
```

## Project Structure
- `src/ticketing_service` - application code
- `tests` - unit and integration tests
- `docs` - implementation notes and setup guide

## License
MIT. See `LICENSE`.