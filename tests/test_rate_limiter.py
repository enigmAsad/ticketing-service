from ticketing_service.api.runtime import RateLimiter


def test_rate_limiter_blocks_after_limit() -> None:
    limiter = RateLimiter(max_requests=2, window_seconds=60)
    assert limiter.allow("client") is True
    assert limiter.allow("client") is True
    assert limiter.allow("client") is False
