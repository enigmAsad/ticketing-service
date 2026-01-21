from datetime import datetime, timedelta, timezone

from fastapi.testclient import TestClient

from ticketing_service import main
from ticketing_service.repositories import BookingRepository, EventRepository


def reset_repositories() -> None:
    main.event_repository = EventRepository()
    main.booking_repository = BookingRepository()
    main.rate_limiter._max_requests = 10_000
    main.rate_limiter._buckets.clear()


def create_event(client: TestClient, total_seats: int) -> str:
    response = client.post(
        "/events",
        json={
            "name": "Stress Event",
            "starts_at": (datetime.now(timezone.utc) + timedelta(days=1)).isoformat(),
            "venue": "Void",
            "total_seats": total_seats,
        },
    )
    response.raise_for_status()
    return response.json()["id"]


def test_scalability_stress() -> None:
    reset_repositories()
    client = TestClient(main.app)

    noise_event_id = create_event(client, total_seats=10_000)
    target_event_id = create_event(client, total_seats=10)

    assert client.post("/bookings", json={"event_id": target_event_id, "seats": [1]}).status_code == 201

    for seat_number in range(1, 5_001):
        response = client.post("/bookings", json={"event_id": noise_event_id, "seats": [seat_number]})
        assert response.status_code == 201

    assert client.post("/bookings", json={"event_id": target_event_id, "seats": [2]}).status_code == 201
