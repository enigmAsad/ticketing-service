from datetime import datetime, timedelta, timezone
from uuid import uuid4

import pytest

from ticketing_service.models import Booking, BookingStatus, Event


def test_event_requires_timezone_aware_start() -> None:
    with pytest.raises(ValueError):
        Event(
            id=uuid4(),
            name="Show",
            starts_at=datetime.now(),
            venue="Main Hall",
            total_seats=100,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
        )


def test_event_requires_positive_seats() -> None:
    with pytest.raises(ValueError):
        Event(
            id=uuid4(),
            name="Show",
            starts_at=datetime.now(timezone.utc) + timedelta(days=1),
            venue="Main Hall",
            total_seats=0,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
        )


def test_booking_requires_unique_positive_seats() -> None:
    with pytest.raises(ValueError):
        Booking(
            id=uuid4(),
            event_id=uuid4(),
            seats=(1, 1),
            status=BookingStatus.CONFIRMED,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
        )

    with pytest.raises(ValueError):
        Booking(
            id=uuid4(),
            event_id=uuid4(),
            seats=(0, 2),
            status=BookingStatus.CONFIRMED,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
        )
