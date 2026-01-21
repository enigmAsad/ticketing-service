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
        self._event_bookings: dict[UUID, list[Booking]] = {}
        self._occupied_seats: dict[UUID, set[int]] = {}
        self._lock = Lock()

    def reserve(
        self,
        event_id: UUID,
        seats: list[int] | tuple[int, ...],
        status: BookingStatus = BookingStatus.CONFIRMED,
    ) -> Booking:
        now = utc_now()
        requested_seats = tuple(seats)
        booking = Booking(
            id=uuid4(),
            event_id=event_id,
            seats=requested_seats,
            status=status,
            created_at=now,
            updated_at=now,
        )

        with self._lock:
            if event_id not in self._occupied_seats:
                self._occupied_seats[event_id] = set()

            current_occupied = self._occupied_seats[event_id]
            if any(seat in current_occupied for seat in requested_seats):
                raise ValueError("One or more seats are already booked.")

            self._bookings[booking.id] = booking

            if event_id not in self._event_bookings:
                self._event_bookings[event_id] = []
            self._event_bookings[event_id].append(booking)

            current_occupied.update(requested_seats)

        return booking

    def get(self, booking_id: UUID) -> Booking | None:
        return self._bookings.get(booking_id)

    def list_by_event(self, event_id: UUID) -> list[Booking]:
        return list(self._event_bookings.get(event_id, []))

