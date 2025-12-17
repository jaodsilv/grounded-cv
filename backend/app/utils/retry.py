"""Retry utilities with exponential backoff for async operations."""

import asyncio
import functools
import logging
import random
from collections.abc import AsyncIterator, Awaitable, Callable
from dataclasses import dataclass
from typing import ParamSpec, TypeVar

P = ParamSpec("P")
T = TypeVar("T")

# Module logger for retry operations
_logger = logging.getLogger(__name__)


@dataclass
class RetryConfig:
    """Configuration for retry behavior.

    Attributes:
        max_attempts: Maximum number of attempts (including initial try)
        base_delay: Base delay in seconds between retries
        max_delay: Maximum delay in seconds (caps exponential growth, after jitter)
        exponential_base: Base for exponential backoff calculation
        jitter: Whether to add randomization to delays (applied before max_delay cap)
    """

    max_attempts: int = 3
    base_delay: float = 1.0
    max_delay: float = 30.0
    exponential_base: float = 2.0
    jitter: bool = True

    def __post_init__(self) -> None:
        """Validate configuration values."""
        if self.max_attempts < 1:
            raise ValueError("max_attempts must be >= 1")
        if self.base_delay < 0:
            raise ValueError("base_delay must be >= 0")
        if self.max_delay < 0:
            raise ValueError("max_delay must be >= 0")
        if self.exponential_base < 1:
            raise ValueError("exponential_base must be >= 1")

    def calculate_delay(self, attempt: int) -> float:
        """Calculate delay for a given attempt number (0-indexed).

        Args:
            attempt: The attempt number (0 for first retry)

        Returns:
            Delay in seconds before next retry
        """
        delay = self.base_delay * (self.exponential_base**attempt)
        if self.jitter:
            # Add jitter: 0.5x to 1.5x of calculated delay (applied before cap)
            delay = delay * (0.5 + random.random())
        # Cap at max_delay after jitter to ensure predictable maximum
        delay = min(delay, self.max_delay)
        return delay


def retry_on_transient_error(
    retryable_exceptions: tuple[type[Exception], ...],
    config: RetryConfig | None = None,
    logger: logging.Logger | None = None,
) -> Callable[[Callable[P, Awaitable[T]]], Callable[P, Awaitable[T]]]:
    """Decorator for retrying async functions on transient errors.

    Args:
        retryable_exceptions: Tuple of exception types to retry on
        config: RetryConfig instance (uses defaults if None)
        logger: Logger for retry messages (uses module logger if None)

    Returns:
        Decorated function with retry logic

    Example:
        @retry_on_transient_error(
            retryable_exceptions=(ConnectionError, TimeoutError),
            config=RetryConfig(max_attempts=3, base_delay=1.0),
        )
        async def call_external_api():
            ...
    """
    if config is None:
        config = RetryConfig()

    log = logger or _logger

    def decorator(func: Callable[P, Awaitable[T]]) -> Callable[P, Awaitable[T]]:
        @functools.wraps(func)
        async def wrapper(*args: P.args, **kwargs: P.kwargs) -> T:
            last_exception: Exception | None = None

            for attempt in range(config.max_attempts):
                try:
                    return await func(*args, **kwargs)
                except retryable_exceptions as e:
                    last_exception = e
                    if attempt < config.max_attempts - 1:
                        delay = config.calculate_delay(attempt)
                        log.warning(
                            f"Attempt {attempt + 1}/{config.max_attempts} failed: "
                            f"{type(e).__name__}: {e}. Retrying in {delay:.2f}s"
                        )
                        await asyncio.sleep(delay)
                    # If this was the last attempt, fall through to raise

            # All retries exhausted
            if last_exception is not None:
                raise last_exception

            # Should never reach here, but satisfy type checker
            raise RuntimeError("Unexpected state in retry logic")

        return wrapper

    return decorator


async def retry_async_generator(
    generator_factory: Callable[[], AsyncIterator[T]],
    retryable_exceptions: tuple[type[Exception], ...],
    config: RetryConfig | None = None,
    logger: logging.Logger | None = None,
) -> AsyncIterator[T]:
    """Retry wrapper for async generators.

    Only retries on initial connection/setup failures. Once streaming has
    started successfully (first yield), failures are NOT retried to avoid
    duplicate data.

    Args:
        generator_factory: Callable that creates a new async iterator
        retryable_exceptions: Tuple of exception types to retry on
        config: RetryConfig instance (uses defaults if None)
        logger: Logger for retry messages (uses module logger if None)

    Yields:
        Items from the underlying generator

    Raises:
        The last exception after all retries are exhausted, or any
        non-retryable exception immediately

    Example:
        async for chunk in retry_async_generator(
            generator_factory=lambda: stream_data(),
            retryable_exceptions=(ConnectionError,),
            config=RetryConfig(max_attempts=3),
        ):
            process(chunk)
    """
    if config is None:
        config = RetryConfig()

    log = logger or _logger
    last_exception: Exception | None = None

    for attempt in range(config.max_attempts):
        gen: AsyncIterator[T] | None = None
        first_yielded = False
        try:
            gen = generator_factory()

            async for item in gen:
                first_yielded = True
                yield item

            # Successfully completed
            return

        except retryable_exceptions as e:
            # Only retry if we haven't yielded anything yet
            if first_yielded:
                # Mid-stream failure - do not retry to avoid duplicates
                raise

            last_exception = e
            if attempt < config.max_attempts - 1:
                delay = config.calculate_delay(attempt)
                log.warning(
                    f"Attempt {attempt + 1}/{config.max_attempts} failed: "
                    f"{type(e).__name__}: {e}. Retrying in {delay:.2f}s"
                )
                await asyncio.sleep(delay)
            # If this was the last attempt, fall through to raise
        finally:
            # Ensure inner generator is properly closed
            if gen is not None and hasattr(gen, "aclose"):
                try:
                    await gen.aclose()
                except (GeneratorExit, StopAsyncIteration, RuntimeError):
                    pass  # Expected during cleanup
                except Exception as cleanup_error:
                    log.warning(f"Unexpected error during generator cleanup: {cleanup_error}")

    # All retries exhausted
    if last_exception is not None:
        raise last_exception
