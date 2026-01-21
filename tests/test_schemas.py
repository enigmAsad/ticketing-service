from datetime import datetime, timedelta, timezone

import pytest
from pydantic import ValidationError

from ticketing_service.api.schemas import BookingCreateRequest, EventCreateRequest
from ticketing_service.api.validation import validate_seat_numbers


def test_event_create_requires_future_aware_datetime() -> None:
    with pytest.raises(ValidationError):
        EventCreateRequest(
            name="Show",
            starts_at=datetime.now(),
            venue="Main Hall",
            total_seats=100,
        )

    with pytest.raises(ValidationError):
        EventCreateRequest(
            name="Show",
            starts_at=datetime.now(timezone.utc) - timedelta(minutes=5),
            venue="Main Hall",
            total_seats=100,
        )


def test_booking_create_validates_seats() -> None:
    with pytest.raises(ValidationError):
        BookingCreateRequest(event_id="9ce9b3b4-fd2e-4b69-8b5b-2e53e10b7d13", seats=[])

    with pytest.raises(ValidationError):
        BookingCreateRequest(event_id="9ce9b3b4-fd2e-4b69-8b5b-2e53e10b7d13", seats=[1, 1])


def test_validate_seat_numbers_enforces_capacity() -> None:
    with pytest.raises(ValueError):
        validate_seat_numbers([1, 2, 10], total_seats=5)

    assert validate_seat_numbers([1, 2, 3], total_seats=3) == [1, 2, 3]
