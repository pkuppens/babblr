"""Performance monitoring utilities for debugging bottlenecks.

Provides timing decorators and context managers with millisecond precision.
"""

import functools
import logging
import time
from contextlib import asynccontextmanager, contextmanager
from typing import Any, Callable

logger = logging.getLogger(__name__)


class PerformanceTimer:
    """High-precision timer for performance monitoring."""

    def __init__(self, name: str, log_level: int = logging.DEBUG):
        self.name = name
        self.log_level = log_level
        self.start_time: float | None = None
        self.end_time: float | None = None

    def start(self) -> None:
        """Start the timer."""
        self.start_time = time.perf_counter()
        logger.log(self.log_level, f"[PERF] {self.name} - START")

    def stop(self) -> float:
        """Stop the timer and return elapsed time in milliseconds."""
        if self.start_time is None:
            logger.warning(f"[PERF] {self.name} - Timer never started")
            return 0.0

        self.end_time = time.perf_counter()
        elapsed_ms = (self.end_time - self.start_time) * 1000
        logger.log(self.log_level, f"[PERF] {self.name} - DONE in {elapsed_ms:.2f}ms")
        return elapsed_ms

    @property
    def elapsed_ms(self) -> float:
        """Get elapsed time in milliseconds.

        Returns current elapsed time if timer is still running,
        or final elapsed time if timer has stopped.
        """
        if self.start_time is None:
            return 0.0

        end = self.end_time if self.end_time is not None else time.perf_counter()
        return (end - self.start_time) * 1000


@contextmanager
def perf_timer(name: str, log_level: int = logging.DEBUG):
    """Context manager for timing code blocks.

    Usage:
        with perf_timer("database_query"):
            result = db.query(...)
    """
    timer = PerformanceTimer(name, log_level)
    timer.start()
    try:
        yield timer
    finally:
        timer.stop()


@asynccontextmanager
async def async_perf_timer(name: str, log_level: int = logging.DEBUG):
    """Async context manager for timing async code blocks.

    Usage:
        async with async_perf_timer("llm_generation"):
            result = await llm.generate(...)
    """
    timer = PerformanceTimer(name, log_level)
    timer.start()
    try:
        yield timer
    finally:
        timer.stop()


def time_function(log_level: int = logging.DEBUG):
    """Decorator for timing function execution.

    Usage:
        @time_function(logging.INFO)
        def my_function():
            ...
    """

    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            func_name = f"{func.__module__}.{func.__qualname__}"
            with perf_timer(func_name, log_level):
                return func(*args, **kwargs)

        return wrapper

    return decorator


def time_async_function(log_level: int = logging.DEBUG):
    """Decorator for timing async function execution.

    Usage:
        @time_async_function(logging.INFO)
        async def my_async_function():
            ...
    """

    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        async def wrapper(*args: Any, **kwargs: Any) -> Any:
            func_name = f"{func.__module__}.{func.__qualname__}"
            async with async_perf_timer(func_name, log_level):
                return await func(*args, **kwargs)

        return wrapper

    return decorator
