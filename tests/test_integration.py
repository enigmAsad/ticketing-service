from datetime import datetime, timedelta, timezone

from fastapi.testclient import TestClient

from ticketing_service import main
from ticketing_service.repositories import BookingRepository, EventRepository


def reset_repositories() -> None:
    main.event_repository = EventRepository()
    main.booking_repository = BookingRepository()


def test_event_and_booking_flow_end_to_end() -> None:
    reset_repositories()
    client = TestClient(main.app)

    event_payload = {
        "name": "City Lights Live",
        "starts_at": (datetime.now(timezone.utc) + timedelta(days=1)).isoformat(),
        "venue": "Downtown Arena",
        "total_seats": 5,
    }
    create_event = client.post("/events", json=event_payload)
    assert create_event.status_code == 201
    event_id = create_event.json()["id"]

    list_events = client.get("/events")
    assert list_events.status_code == 200
    assert list_events.json()["total"] == 1

    fetch_event = client.get(f"/events/{event_id}")
    assert fetch_event.status_code == 200
    assert fetch_event.json()["id"] == event_id

    seat_check = client.get(f"/events/{event_id}/seats?detail=list")
    assert seat_check.status_code == 200
    assert seat_check.json()["available_seats"] == [1, 2, 3, 4, 5]
    assert seat_check.json()["available_count"] == 5

    booking_payload = {"event_id": event_id, "seats": [1, 2]}
    create_booking = client.post("/bookings", json=booking_payload)
    assert create_booking.status_code == 201
    booking_id = create_booking.json()["id"]

    seat_check_after = client.get(f"/events/{event_id}/seats")
    assert seat_check_after.status_code == 200
    assert seat_check_after.json()["booked_count"] == 2

    fetch_booking = client.get(f"/bookings/{booking_id}")
    assert fetch_booking.status_code == 200
    assert fetch_booking.json()["id"] == booking_id

    list_bookings = client.get(f"/events/{event_id}/bookings")
    assert list_bookings.status_code == 200
    assert list_bookings.json()["total"] == 1


def test_double_booking_is_rejected() -> None:
    reset_repositories()
    client = TestClient(main.app)

    event_payload = {
        "name": "Test Event",
        "starts_at": (datetime.now(timezone.utc) + timedelta(days=1)).isoformat(),
        "venue": "Main Hall",
        "total_seats": 3,
    }
    event_id = client.post("/events", json=event_payload).json()["id"]

    booking_payload = {"event_id": event_id, "seats": [1]}
    assert client.post("/bookings", json=booking_payload).status_code == 201

    conflict = client.post("/bookings", json=booking_payload)
    assert conflict.status_code == 409


def test_invalid_event_start_date_is_rejected() -> None:
    reset_repositories()
    client = TestClient(main.app)

    event_payload = {
        "name": "Past Event",
        "starts_at": (datetime.now(timezone.utc) - timedelta(hours=1)).isoformat(),
        "venue": "Main Hall",
        "total_seats": 10,
    }
    response = client.post("/events", json=event_payload)
    assert response.status_code == 422
