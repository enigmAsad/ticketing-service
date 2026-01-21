from http import HTTPStatus
from uuid import UUID

from fastapi import FastAPI, HTTPException, Query, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from ticketing_service.api.runtime import RateLimiter, configure_logging, create_request_middleware
from ticketing_service.api.schemas import (
    BookingCreateRequest,
    BookingListResponse,
    BookingResponse,
    ErrorResponse,
    EventCreateRequest,
    EventListResponse,
    EventResponse,
    SeatAvailabilityResponse,
)
from ticketing_service.api.validation import validate_seat_numbers
from ticketing_service.repositories import BookingRepository, EventRepository

app = FastAPI(title="Ticketing Service")
event_repository = EventRepository()
booking_repository = BookingRepository()
logger = configure_logging()
rate_limiter = RateLimiter(max_requests=100, window_seconds=60)
app.middleware("http")(create_request_middleware(rate_limiter, max_body_bytes=1_000_000, logger=logger))


@app.get("/health")
def health_check() -> dict[str, str]:
    return {"status": "ok"}


@app.exception_handler(HTTPException)
def http_exception_handler(request: Request, exc: HTTPException) -> JSONResponse:
    try:
        error_name = HTTPStatus(exc.status_code).phrase
    except ValueError:
        error_name = "Error"
    detail = exc.detail if isinstance(exc.detail, str) else "Request failed."
    response = ErrorResponse(error=error_name, detail=detail)
    return JSONResponse(status_code=exc.status_code, content=response.model_dump())


@app.exception_handler(RequestValidationError)
def validation_exception_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
    response = ErrorResponse(error="Validation Error", detail="Request validation failed.")
    return JSONResponse(status_code=status.HTTP_422_UNPROCESSABLE_CONTENT, content=response.model_dump())


@app.exception_handler(Exception)
def unhandled_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    logger.exception("Unhandled error for request %s", request.url.path)
    response = ErrorResponse(error="Internal Server Error", detail="Unexpected server error.")
    return JSONResponse(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, content=response.model_dump())


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


@app.get(
    "/events/{event_id}/seats",
    response_model=SeatAvailabilityResponse,
    responses={404: {"model": ErrorResponse}},
)
def get_seat_availability(event_id: UUID) -> SeatAvailabilityResponse:
    event = event_repository.get(event_id)
    if event is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Event not found.")

    bookings = booking_repository.list_by_event(event_id)
    booked_seats = sorted({seat for booking in bookings for seat in booking.seats})
    booked_set = set(booked_seats)
    available_seats = [seat for seat in range(1, event.total_seats + 1) if seat not in booked_set]

    return SeatAvailabilityResponse(
        available_seats=available_seats,
        booked_seats=booked_seats,
        capacity=event.total_seats,
    )


@app.post(
    "/bookings",
    response_model=BookingResponse,
    status_code=status.HTTP_201_CREATED,
    responses={400: {"model": ErrorResponse}, 404: {"model": ErrorResponse}, 409: {"model": ErrorResponse}},
)
def create_booking(payload: BookingCreateRequest) -> BookingResponse:
    event = event_repository.get(payload.event_id)
    if event is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Event not found.")

    try:
        validate_seat_numbers(payload.seats, event.total_seats)
        booking = booking_repository.reserve(event_id=event.id, seats=payload.seats)
    except ValueError as exc:
        detail = str(exc)
        status_code = (
            status.HTTP_409_CONFLICT if "already booked" in detail.lower() else status.HTTP_400_BAD_REQUEST
        )
        raise HTTPException(status_code=status_code, detail=detail) from exc

    return BookingResponse(
        id=booking.id,
        event_id=booking.event_id,
        seats=list(booking.seats),
        status=booking.status,
        created_at=booking.created_at,
        updated_at=booking.updated_at,
    )


@app.get(
    "/bookings/{booking_id}",
    response_model=BookingResponse,
    responses={404: {"model": ErrorResponse}},
)
def get_booking(booking_id: UUID) -> BookingResponse:
    booking = booking_repository.get(booking_id)
    if booking is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Booking not found.")

    return BookingResponse(
        id=booking.id,
        event_id=booking.event_id,
        seats=list(booking.seats),
        status=booking.status,
        created_at=booking.created_at,
        updated_at=booking.updated_at,
    )


@app.get(
    "/events/{event_id}/bookings",
    response_model=BookingListResponse,
    responses={404: {"model": ErrorResponse}},
)
def list_event_bookings(
    event_id: UUID,
    offset: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
) -> BookingListResponse:
    event = event_repository.get(event_id)
    if event is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Event not found.")

    bookings = booking_repository.list_by_event(event_id)
    paged = bookings[offset : offset + limit]
    return BookingListResponse(
        items=[
            BookingResponse(
                id=booking.id,
                event_id=booking.event_id,
                seats=list(booking.seats),
                status=booking.status,
                created_at=booking.created_at,
                updated_at=booking.updated_at,
            )
            for booking in paged
        ],
        total=len(bookings),
    )
