from __future__ import annotations

import time
from typing import Callable, TypeVar

T = TypeVar("T")


def timed_call(fn: Callable[[], T], repeat: int = 1) -> tuple[T, float]:
    last_result: T | None = None
    start = time.perf_counter()
    for _ in range(max(1, repeat)):
        last_result = fn()
    elapsed_ms = (time.perf_counter() - start) * 1000.0
    # Average per run to keep numbers interpretable.
    return last_result, elapsed_ms / max(1, repeat)
