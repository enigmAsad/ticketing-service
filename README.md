# Ticketing Service

## API Overview
The service exposes a simple REST API for events and bookings. OpenAPI docs are
available at `/docs` and `/openapi.json` when the service is running.

### Example Payloads

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