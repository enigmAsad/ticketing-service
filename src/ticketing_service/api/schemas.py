from __future__ import annotations

from datetime import datetime, timezone
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, field_validator

from ticketing_service.models import BookingStatus


class ApiBaseModel(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True, extra="forbid")


class EventCreateRequest(ApiBaseModel):
    name: str = Field(min_length=1, max_length=200)
    starts_at: datetime
    venue: str = Field(min_length=1, max_length=200)
    total_seats: int = Field(gt=0)

    @field_validator("starts_at")
    @classmethod
    def validate_starts_at(cls, value: datetime) -> datetime:
        if value.tzinfo is None or value.tzinfo.utcoffset(value) is None:
            raise ValueError("starts_at must be timezone-aware.")
        if value <= datetime.now(timezone.utc):
            raise ValueError("starts_at must be in the future.")
        return value


class EventResponse(ApiBaseModel):
    id: UUID
    name: str
    starts_at: datetime
    venue: str
    total_seats: int
    created_at: datetime
    updated_at: datetime


class EventListResponse(ApiBaseModel):
    items: list[EventResponse]
    total: int

    @field_validator("total")
    @classmethod
    def validate_total(cls, value: int) -> int:
        if value < 0:
            raise ValueError("total must be non-negative.")
        return value


class BookingCreateRequest(ApiBaseModel):
    event_id: UUID
    seats: list[int] = Field(min_length=1)

    @field_validator("seats")
    @classmethod
    def validate_seats(cls, value: list[int]) -> list[int]:
        if any(seat <= 0 for seat in value):
            raise ValueError("seats must be positive integers.")
        if len(set(value)) != len(value):
            raise ValueError("seats must be unique.")
        return value


class BookingResponse(ApiBaseModel):
    id: UUID
    event_id: UUID
    seats: list[int]
    status: BookingStatus
    created_at: datetime
    updated_at: datetime


class BookingListResponse(ApiBaseModel):
    items: list[BookingResponse]
    total: int

    @field_validator("total")
    @classmethod
    def validate_total(cls, value: int) -> int:
        if value < 0:
            raise ValueError("total must be non-negative.")
        return value


class SeatAvailabilityResponse(ApiBaseModel):
    available_seats: list[int]
    booked_seats: list[int]
    capacity: int = Field(gt=0)


class ErrorResponse(ApiBaseModel):
    error: str
    detail: str | None = None
