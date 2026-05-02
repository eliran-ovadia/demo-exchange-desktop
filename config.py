from __future__ import annotations
import os
import logging

DEV = os.getenv("APP_ENV", "prod") == "dev"

BASE_URL = "http://localhost:8000" if DEV else "https://demoexchanges.com"

logging.basicConfig(
    level=logging.DEBUG if DEV else logging.WARNING,
    format="%(levelname)s [%(name)s] %(message)s",
)
