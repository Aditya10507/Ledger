"""Structured (JSON-line) logging setup.

The architecture doc (Section 10) calls for structured request/error logs —
this was previously just default uvicorn output with no structure. Kept simple
on purpose: writes JSON lines to stdout, which is what most hosting platforms
(Render/Railway) already collect and index without extra configuration.
"""

import json
import logging
import sys
import time
from typing import Callable

from fastapi import Request, Response


class JsonFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        payload = {
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }
        if hasattr(record, "extra_fields"):
            payload.update(record.extra_fields)
        return json.dumps(payload)


def configure_logging() -> None:
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(JsonFormatter())

    root = logging.getLogger()
    root.handlers = [handler]
    root.setLevel(logging.INFO)


logger = logging.getLogger("ledger")


async def request_logging_middleware(request: Request, call_next: Callable) -> Response:
    """Logs method, path, status, and latency for every request.
    Deliberately does NOT log request bodies (may contain file contents / tokens — SEC-4).
    """
    start = time.time()
    response = await call_next(request)
    duration_ms = round((time.time() - start) * 1000, 1)

    logger.info(
        "request",
        extra={
            "extra_fields": {
                "method": request.method,
                "path": request.url.path,
                "status_code": response.status_code,
                "duration_ms": duration_ms,
            }
        },
    )
    return response
