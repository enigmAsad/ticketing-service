from uuid import UUID

from fastapi import FastAPI, HTTPException, Query, status

from ticketing_service.api.schemas import (
    ErrorResponse,
    EventCreateRequest,
    EventListResponse,
    EventResponse,
)
from ticketing_service.repositories import EventRepository

app = FastAPI(title="Ticketing Service")
event_repository = EventRepository()


@app.get("/health")
def health_check() -> dict[str, str]:
    return {"status": "ok"}


@app.post(
    "/events",
    response_model=EventResponse,
    status_code=status.HTTP_201_CREATED,
    responses={400: {"model": ErrorResponse}},
)
def create_event(payload: EventCreateRequest) -> EventResponse:
    try:
        event = event_repository.create(
            name=payload.name,
            starts_at=payload.starts_at,
            venue=payload.venue,
            total_seats=payload.total_seats,
        )
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc

    return EventResponse(
        id=event.id,
        name=event.name,
        starts_at=event.starts_at,
        venue=event.venue,
        total_seats=event.total_seats,
        created_at=event.created_at,
        updated_at=event.updated_at,
    )


@app.get("/events", response_model=EventListResponse)
def list_events(
    offset: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
) -> EventListResponse:
    events = event_repository.list()
    paged = events[offset : offset + limit]
    return EventListResponse(
        items=[
            EventResponse(
                id=event.id,
                name=event.name,
                starts_at=event.starts_at,
                venue=event.venue,
                total_seats=event.total_seats,
                created_at=event.created_at,
                updated_at=event.updated_at,
            )
            for event in paged
        ],
        total=len(events),
    )


@app.get(
    "/events/{event_id}",
    response_model=EventResponse,
    responses={404: {"model": ErrorResponse}},
)
def get_event(event_id: UUID) -> EventResponse:
    event = event_repository.get(event_id)
    if event is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Event not found.")

    return EventResponse(
        id=event.id,
        name=event.name,
        starts_at=event.starts_at,
        venue=event.venue,
        total_seats=event.total_seats,
        created_at=event.created_at,
        updated_at=event.updated_at,
    )
