from datetime import datetime, timedelta, timezone

from ticketing_service.models import BookingStatus
from ticketing_service.repositories import BookingRepository, EventRepository


def test_event_repository_create_and_get() -> None:
    repo = EventRepository()
    event = repo.create(
        name="City Lights",
        starts_at=datetime.now(timezone.utc) + timedelta(days=1),
        venue="Downtown Arena",
        total_seats=250,
    )

    fetched = repo.get(event.id)
    assert fetched is not None
    assert fetched.id == event.id
    assert fetched.created_at == fetched.updated_at


def test_booking_repository_create_and_filter() -> None:
    repo = BookingRepository()
    event_id = EventRepository().create(
        name="City Lights",
        starts_at=datetime.now(timezone.utc) + timedelta(days=1),
        venue="Downtown Arena",
        total_seats=250,
    ).id

    booking = repo.reserve(event_id=event_id, seats=[1, 2, 3], status=BookingStatus.CONFIRMED)
    assert repo.get(booking.id) is not None
    assert repo.list_by_event(event_id) == [booking]
