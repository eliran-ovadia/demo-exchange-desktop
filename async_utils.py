from __future__ import annotations

import asyncio
import logging

_log = logging.getLogger(__name__)


def schedule(coro) -> asyncio.Task:
    task = asyncio.ensure_future(coro)
    task.add_done_callback(_log_exc)
    return task


def _log_exc(task: asyncio.Task) -> None:
    if task.cancelled():
        return
    exc = task.exception()
    if exc is not None:
        _log.error("Unhandled exception in scheduled task", exc_info=exc)
