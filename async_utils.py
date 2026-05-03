"""
Async scheduling helpers for Qt views.

  schedule_replacing(coro, self._task) -> asyncio.Task
      Cancels the previous task if still running, then fires the new one.
      Use when the same operation can be triggered repeatedly and only the
      latest result matters (refresh timer, reload on activation).
      Always assign the return value back:
          self._task = schedule_replacing(coro, self._task)

  Debouncer(delay_ms).schedule(lambda: coro_factory())
      Waits delay_ms before running; resets the timer on each new call.
      Use for rapid repeated triggers where only the final one matters
      (e.g. clicking through a list quickly).
      Pass a lambda — not the coroutine directly — so a fresh coroutine is
      created after the delay.

Unhandled exceptions from both are caught by the global handler in main.py.
"""

from __future__ import annotations

import asyncio
from typing import Callable


def schedule_replacing(coro, prev: asyncio.Task | None) -> asyncio.Task:
    """Cancel prev if still running, then schedule coro."""
    if prev and not prev.done():
        prev.cancel()
    return asyncio.ensure_future(coro)


class Debouncer:
    """Delays a call by delay_ms and resets the timer on each new call.

    Usage:
        self._debouncer = Debouncer(150)          # in __init__
        self._debouncer.schedule(lambda: coro())  # in signal handler
    """

    def __init__(self, delay_ms: int) -> None:
        self._delay = delay_ms / 1000
        self._task: asyncio.Task | None = None

    def schedule(self, coro_factory: Callable) -> None:
        if self._task and not self._task.done():
            self._task.cancel()

        async def _run() -> None:
            await asyncio.sleep(self._delay)
            await coro_factory()

        self._task = asyncio.ensure_future(_run())
