from __future__ import annotations

from datetime import datetime
from threading import Lock
from uuid import UUID, uuid4

from ticketing_service.models import Booking, BookingStatus, Event, utc_now


class EventRepository:
    def __init__(self) -> None:
        self._events: dict[UUID, Event] = {}
        self._lock = Lock()

    def create(self, name: str, starts_at: datetime, venue: str, total_seats: int) -> Event:
        now = utc_now()
        event = Event(
            id=uuid4(),
            name=name,
            starts_at=starts_at,
            venue=venue,
            total_seats=total_seats,
            created_at=now,
            updated_at=now,
        )
        # Lock to keep writes consistent under concurrency.
        with self._lock:
            self._events[event.id] = event
        return event

    def get(self, event_id: UUID) -> Event | None:
        return self._events.get(event_id)

    def list(self) -> list[Event]:
        return list(self._events.values())


class BookingRepository:
    def __init__(self) -> None:
        self._bookings: dict[UUID, Booking] = {}
        self._lock = Lock()

    def create(
        self,
        event_id: UUID,
        seats: list[int] | tuple[int, ...],
        status: BookingStatus = BookingStatus.CONFIRMED,
    ) -> Booking:
        now = utc_now()
        booking = Booking(
            id=uuid4(),
            event_id=event_id,
            seats=tuple(seats),
            status=status,
            created_at=now,
            updated_at=now,
        )
        # Lock to keep writes consistent under concurrency.
        with self._lock:
            self._bookings[booking.id] = booking
        return booking

    def get(self, booking_id: UUID) -> Booking | None:
        return self._bookings.get(booking_id)

    def list_by_event(self, event_id: UUID) -> list[Booking]:
        return [booking for booking in self._bookings.values() if booking.event_id == event_id]
