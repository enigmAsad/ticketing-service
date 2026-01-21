from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import os


def _load_env_file(path: Path) -> None:
    if not path.exists():
        return
    for line in path.read_text(encoding="utf-8").splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#") or "=" not in stripped:
            continue
        key, value = stripped.split("=", 1)
        key = key.strip()
        value = value.strip().strip('"').strip("'")
        if key and key not in os.environ:
            os.environ[key] = value


_load_env_file(Path(".env"))


@dataclass(frozen=True)
class Settings:
    host: str = os.getenv("HOST", "127.0.0.1")
    port: int = int(os.getenv("PORT", "8000"))
    rate_limit_max_requests: int = int(os.getenv("RATE_LIMIT_MAX_REQUESTS", "100"))
    rate_limit_window_seconds: int = int(os.getenv("RATE_LIMIT_WINDOW_SECONDS", "60"))
    max_body_bytes: int = int(os.getenv("MAX_BODY_BYTES", "1000000"))
    log_level: str = os.getenv("LOG_LEVEL", "INFO").upper()


settings = Settings()
