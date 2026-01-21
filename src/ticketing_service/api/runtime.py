from __future__ import annotations

import logging
from collections import defaultdict, deque
from time import time
from threading import Lock
from typing import Callable
from uuid import uuid4

from fastapi import Request
from fastapi.responses import JSONResponse, Response
from starlette.middleware.base import RequestResponseEndpoint

from ticketing_service.api.schemas import ErrorResponse


class RateLimiter:
    def __init__(self, max_requests: int, window_seconds: int) -> None:
        self._max_requests = max_requests
        self._window_seconds = window_seconds
        self._buckets: dict[str, deque[float]] = defaultdict(deque)
        self._lock = Lock()
        self._last_cleanup = time()

    def _cleanup_stale_buckets(self, now: float) -> None:
        keys_to_delete = []
        for key, bucket in self._buckets.items():
            if bucket and (now - bucket[-1] > self._window_seconds):
                keys_to_delete.append(key)

        for key in keys_to_delete:
            del self._buckets[key]

        self._last_cleanup = now

    def allow(self, key: str) -> bool:
        now = time()
        with self._lock:
            if now - self._last_cleanup > 60:
                self._cleanup_stale_buckets(now)

            bucket = self._buckets[key]
            while bucket and now - bucket[0] > self._window_seconds:
                bucket.popleft()

            if len(bucket) >= self._max_requests:
                return False

            bucket.append(now)
        return True


def configure_logging() -> logging.Logger:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s [%(message)s]",
    )
    return logging.getLogger("ticketing_service")


def create_request_middleware(
    rate_limiter: RateLimiter,
    max_body_bytes: int,
    logger: logging.Logger,
) -> Callable[[Request, RequestResponseEndpoint], Response]:
    async def middleware(request: Request, call_next: RequestResponseEndpoint) -> Response:
        request_id = request.headers.get("x-request-id") or str(uuid4())
        request.state.request_id = request_id
        client_host = request.client.host if request.client else "unknown"

        if not rate_limiter.allow(client_host):
            response = ErrorResponse(error="Too Many Requests", detail="Rate limit exceeded.")
            return JSONResponse(status_code=429, content=response.model_dump())

        content_length = request.headers.get("content-length")
        if content_length and int(content_length) > max_body_bytes:
            response = ErrorResponse(error="Payload Too Large", detail="Request body exceeds size limit.")
            return JSONResponse(status_code=413, content=response.model_dump())

        response = await call_next(request)
        response.headers["X-Request-Id"] = request_id
        logger.info("%s %s %s", request.method, request.url.path, response.status_code)
        return response

    return middleware
