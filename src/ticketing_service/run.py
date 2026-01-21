from __future__ import annotations

import uvicorn

from ticketing_service.config import settings


def main() -> None:
    uvicorn.run(
        "ticketing_service.main:app",
        host=settings.host,
        port=settings.port,
        reload=True,
    )


if __name__ == "__main__":
    main()
