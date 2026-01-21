from __future__ import annotations


def validate_seat_numbers(seats: list[int], total_seats: int) -> list[int]:
    if total_seats <= 0:
        raise ValueError("total_seats must be positive.")
    if not seats:
        raise ValueError("seats must be non-empty.")
    if any(seat <= 0 for seat in seats):
        raise ValueError("seats must be positive integers.")
    if len(set(seats)) != len(seats):
        raise ValueError("seats must be unique.")
    if any(seat > total_seats for seat in seats):
        raise ValueError("seats must be within event capacity.")
    return seats
