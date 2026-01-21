from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import StrEnum
from uuid import UUID


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


class BookingStatus(StrEnum):
    PENDING = "PENDING"
    CONFIRMED = "CONFIRMED"
    CANCELLED = "CANCELLED"


@dataclass(frozen=True, slots=True)
class Event:
    id: UUID
    name: str
    starts_at: datetime
    venue: str
    total_seats: int
    created_at: datetime
    updated_at: datetime

    def __post_init__(self) -> None:
        if not self.name.strip():
            raise ValueError("Event name must be non-empty.")
        if not self.venue.strip():
            raise ValueError("Event venue must be non-empty.")
        if self.total_seats <= 0:
            raise ValueError("Event total_seats must be positive.")
        if self.starts_at.tzinfo is None or self.starts_at.tzinfo.utcoffset(self.starts_at) is None:
            raise ValueError("Event starts_at must be timezone-aware.")


@dataclass(frozen=True, slots=True)
class Booking:
    id: UUID
    event_id: UUID
    seats: tuple[int, ...]
    status: BookingStatus
    created_at: datetime
    updated_at: datetime

    def __post_init__(self) -> None:
        if not self.seats:
            raise ValueError("Booking seats must be non-empty.")
        if any(seat <= 0 for seat in self.seats):
            raise ValueError("Booking seats must be positive integers.")
        if len(set(self.seats)) != len(self.seats):
            raise ValueError("Booking seats must be unique.")
