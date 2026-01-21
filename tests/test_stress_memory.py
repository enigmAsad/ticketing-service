from datetime import datetime, timedelta, timezone

from fastapi.testclient import TestClient

from ticketing_service import main
from ticketing_service.repositories import BookingRepository, EventRepository


def reset_repositories() -> None:
    main.event_repository = EventRepository()
    main.booking_repository = BookingRepository()


def test_large_event_is_rejected() -> None:
    reset_repositories()
    client = TestClient(main.app)

    response = client.post(
        "/events",
        json={
            "name": "Huge Event",
            "starts_at": (datetime.now(timezone.utc) + timedelta(days=1)).isoformat(),
            "venue": "Mega Stadium",
            "total_seats": 150_000,
        },
    )
    assert response.status_code == 422
