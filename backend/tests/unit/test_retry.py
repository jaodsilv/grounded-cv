"""Unit tests for retry utilities with exponential backoff."""

import logging
from unittest.mock import MagicMock

import pytest

from app.utils.retry import (
    RetryConfig,
    retry_async_generator,
    retry_on_transient_error,
)


class TestRetryConfig:
    """Tests for RetryConfig dataclass."""

    def test_default_values(self):
        """Test RetryConfig initializes with sensible defaults."""
        config = RetryConfig()

        assert config.max_attempts == 3
        assert config.base_delay == 1.0
        assert config.max_delay == 30.0
        assert config.exponential_base == 2.0
        assert config.jitter is True

    def test_custom_values(self):
        """Test RetryConfig accepts custom values."""
        config = RetryConfig(
            max_attempts=5,
            base_delay=0.5,
            max_delay=60.0,
            exponential_base=3.0,
            jitter=False,
        )

        assert config.max_attempts == 5
        assert config.base_delay == 0.5
        assert config.max_delay == 60.0
        assert config.exponential_base == 3.0
        assert config.jitter is False

    def test_calculate_delay_exponential(self):
        """Test delay calculation follows exponential backoff."""
        config = RetryConfig(
            base_delay=1.0,
            exponential_base=2.0,
            max_delay=100.0,
            jitter=False,
        )

        # attempt 0: 1.0 * 2^0 = 1.0
        assert config.calculate_delay(0) == 1.0
        # attempt 1: 1.0 * 2^1 = 2.0
        assert config.calculate_delay(1) == 2.0
        # attempt 2: 1.0 * 2^2 = 4.0
        assert config.calculate_delay(2) == 4.0
        # attempt 3: 1.0 * 2^3 = 8.0
        assert config.calculate_delay(3) == 8.0

    def test_calculate_delay_respects_max(self):
        """Test delay is capped at max_delay."""
        config = RetryConfig(
            base_delay=1.0,
            exponential_base=2.0,
            max_delay=5.0,
            jitter=False,
        )

        # attempt 0: min(1.0, 5.0) = 1.0
        assert config.calculate_delay(0) == 1.0
        # attempt 1: min(2.0, 5.0) = 2.0
        assert config.calculate_delay(1) == 2.0
        # attempt 2: min(4.0, 5.0) = 4.0
        assert config.calculate_delay(2) == 4.0
        # attempt 3: min(8.0, 5.0) = 5.0 (capped)
        assert config.calculate_delay(3) == 5.0
        # attempt 10: min(1024.0, 5.0) = 5.0 (capped)
        assert config.calculate_delay(10) == 5.0

    def test_calculate_delay_with_jitter(self):
        """Test jitter adds randomization within expected range."""
        config = RetryConfig(
            base_delay=10.0,
            exponential_base=1.0,  # Keep base constant for easier testing
            max_delay=100.0,
            jitter=True,
        )

        # Run multiple times to verify jitter range
        delays = [config.calculate_delay(0) for _ in range(100)]

        # All delays should be within jitter range: 5.0 to 15.0 (0.5x to 1.5x)
        for delay in delays:
            assert 5.0 <= delay <= 15.0

        # Delays should not all be the same (randomness)
        unique_delays = set(delays)
        assert len(unique_delays) > 1


class TestRetryOnTransientError:
    """Tests for the retry_on_transient_error decorator."""

    @pytest.mark.asyncio
    async def test_no_retry_on_success(self):
        """Test successful call returns immediately without retry."""
        call_count = 0

        @retry_on_transient_error(
            retryable_exceptions=(ConnectionError,),
            config=RetryConfig(max_attempts=3),
        )
        async def successful_fn():
            nonlocal call_count
            call_count += 1
            return "success"

        result = await successful_fn()

        assert result == "success"
        assert call_count == 1

    @pytest.mark.asyncio
    async def test_retry_on_transient_failure_then_success(self):
        """Test retry succeeds after transient failure."""
        call_count = 0

        @retry_on_transient_error(
            retryable_exceptions=(ConnectionError,),
            config=RetryConfig(max_attempts=3, base_delay=0.01, jitter=False),
        )
        async def fails_then_succeeds():
            nonlocal call_count
            call_count += 1
            if call_count < 2:
                raise ConnectionError("Temporary failure")
            return "success"

        result = await fails_then_succeeds()

        assert result == "success"
        assert call_count == 2

    @pytest.mark.asyncio
    async def test_retry_exhausts_attempts(self):
        """Test raises after exhausting all retry attempts."""
        call_count = 0

        @retry_on_transient_error(
            retryable_exceptions=(ConnectionError,),
            config=RetryConfig(max_attempts=3, base_delay=0.01, jitter=False),
        )
        async def always_fails():
            nonlocal call_count
            call_count += 1
            raise ConnectionError("Persistent failure")

        with pytest.raises(ConnectionError, match="Persistent failure"):
            await always_fails()

        assert call_count == 3

    @pytest.mark.asyncio
    async def test_no_retry_on_non_retryable_exception(self):
        """Test non-retryable exceptions are raised immediately."""
        call_count = 0

        @retry_on_transient_error(
            retryable_exceptions=(ConnectionError,),
            config=RetryConfig(max_attempts=3, base_delay=0.01),
        )
        async def raises_value_error():
            nonlocal call_count
            call_count += 1
            raise ValueError("Not retryable")

        with pytest.raises(ValueError, match="Not retryable"):
            await raises_value_error()

        assert call_count == 1  # No retries

    @pytest.mark.asyncio
    async def test_multiple_retryable_exceptions(self):
        """Test retry works with multiple exception types."""
        call_count = 0

        @retry_on_transient_error(
            retryable_exceptions=(ConnectionError, TimeoutError, OSError),
            config=RetryConfig(max_attempts=4, base_delay=0.01, jitter=False),
        )
        async def raises_different_errors():
            nonlocal call_count
            call_count += 1
            if call_count == 1:
                raise ConnectionError("Connection failed")
            if call_count == 2:
                raise TimeoutError("Timed out")
            if call_count == 3:
                raise OSError("OS error")
            return "success"

        result = await raises_different_errors()

        assert result == "success"
        assert call_count == 4

    @pytest.mark.asyncio
    async def test_retry_logs_attempts(self, caplog):
        """Test retry attempts are logged."""
        call_count = 0

        @retry_on_transient_error(
            retryable_exceptions=(ConnectionError,),
            config=RetryConfig(max_attempts=3, base_delay=0.01, jitter=False),
        )
        async def fails_twice():
            nonlocal call_count
            call_count += 1
            if call_count < 3:
                raise ConnectionError("Temporary failure")
            return "success"

        with caplog.at_level(logging.WARNING):
            await fails_twice()

        # Should have logged 2 retry attempts
        retry_logs = [r for r in caplog.records if "Retry" in r.message]
        assert len(retry_logs) == 2

    @pytest.mark.asyncio
    async def test_retry_with_custom_logger(self):
        """Test retry uses custom logger when provided."""
        custom_logger = MagicMock(spec=logging.Logger)
        call_count = 0

        @retry_on_transient_error(
            retryable_exceptions=(ConnectionError,),
            config=RetryConfig(max_attempts=2, base_delay=0.01, jitter=False),
            logger=custom_logger,
        )
        async def fails_once():
            nonlocal call_count
            call_count += 1
            if call_count == 1:
                raise ConnectionError("Temp failure")
            return "success"

        await fails_once()

        # Should have logged the retry attempt
        custom_logger.warning.assert_called()

    @pytest.mark.asyncio
    async def test_retry_preserves_function_metadata(self):
        """Test decorated function preserves name and docstring."""

        @retry_on_transient_error(
            retryable_exceptions=(ConnectionError,),
            config=RetryConfig(),
        )
        async def my_documented_function():
            """This is my docstring."""
            return "result"

        assert my_documented_function.__name__ == "my_documented_function"
        assert my_documented_function.__doc__ == "This is my docstring."

    @pytest.mark.asyncio
    async def test_retry_uses_default_config_when_none(self):
        """Test decorator uses default config when none provided."""
        call_count = 0

        @retry_on_transient_error(retryable_exceptions=(ConnectionError,))
        async def my_fn():
            nonlocal call_count
            call_count += 1
            if call_count == 1:
                raise ConnectionError("Temp")
            return "ok"

        # Should still retry with default config
        result = await my_fn()
        assert result == "ok"
        assert call_count == 2


class TestRetryAsyncGenerator:
    """Tests for the retry_async_generator wrapper."""

    @pytest.mark.asyncio
    async def test_generator_no_retry_on_success(self):
        """Test successful generator yields without retry."""
        call_count = 0

        async def successful_generator():
            nonlocal call_count
            call_count += 1
            yield "chunk1"
            yield "chunk2"
            yield "chunk3"

        results = []
        async for chunk in retry_async_generator(
            generator_factory=successful_generator,
            retryable_exceptions=(ConnectionError,),
            config=RetryConfig(max_attempts=3, base_delay=0.01),
        ):
            results.append(chunk)

        assert results == ["chunk1", "chunk2", "chunk3"]
        assert call_count == 1

    @pytest.mark.asyncio
    async def test_generator_retry_on_initial_failure(self):
        """Test generator retries if fails before first yield."""
        call_count = 0

        async def fails_initially_then_succeeds():
            nonlocal call_count
            call_count += 1
            if call_count == 1:
                raise ConnectionError("Initial connection failed")
            yield "chunk1"
            yield "chunk2"

        results = []
        async for chunk in retry_async_generator(
            generator_factory=fails_initially_then_succeeds,
            retryable_exceptions=(ConnectionError,),
            config=RetryConfig(max_attempts=3, base_delay=0.01, jitter=False),
        ):
            results.append(chunk)

        assert results == ["chunk1", "chunk2"]
        assert call_count == 2

    @pytest.mark.asyncio
    async def test_generator_no_retry_after_first_yield(self):
        """Test generator does NOT retry failures after first yield."""
        call_count = 0
        yielded_chunks = []

        async def fails_mid_stream():
            nonlocal call_count
            call_count += 1
            yield "chunk1"
            yielded_chunks.append("chunk1")
            raise ConnectionError("Mid-stream failure")

        results = []
        with pytest.raises(ConnectionError, match="Mid-stream failure"):
            async for chunk in retry_async_generator(
                generator_factory=fails_mid_stream,
                retryable_exceptions=(ConnectionError,),
                config=RetryConfig(max_attempts=3, base_delay=0.01),
            ):
                results.append(chunk)

        assert results == ["chunk1"]
        assert call_count == 1  # No retry after first yield

    @pytest.mark.asyncio
    async def test_generator_exhausts_retries(self):
        """Test generator raises after exhausting retries."""
        call_count = 0

        async def always_fails_initially():
            nonlocal call_count
            call_count += 1
            raise ConnectionError("Always fails")
            yield "never reached"

        with pytest.raises(ConnectionError, match="Always fails"):
            async for _ in retry_async_generator(
                generator_factory=always_fails_initially,
                retryable_exceptions=(ConnectionError,),
                config=RetryConfig(max_attempts=3, base_delay=0.01, jitter=False),
            ):
                pass

        assert call_count == 3

    @pytest.mark.asyncio
    async def test_generator_no_retry_on_non_retryable(self):
        """Test generator doesn't retry non-retryable exceptions."""
        call_count = 0

        async def raises_value_error():
            nonlocal call_count
            call_count += 1
            raise ValueError("Not retryable")
            yield "never"

        with pytest.raises(ValueError, match="Not retryable"):
            async for _ in retry_async_generator(
                generator_factory=raises_value_error,
                retryable_exceptions=(ConnectionError,),
                config=RetryConfig(max_attempts=3, base_delay=0.01),
            ):
                pass

        assert call_count == 1

    @pytest.mark.asyncio
    async def test_generator_handles_generator_exit(self):
        """Test generator handles GeneratorExit gracefully."""
        cleanup_called = False

        async def generator_with_cleanup():
            nonlocal cleanup_called
            try:
                yield "chunk1"
                yield "chunk2"
            except GeneratorExit:
                cleanup_called = True
                raise

        gen = retry_async_generator(
            generator_factory=generator_with_cleanup,
            retryable_exceptions=(ConnectionError,),
            config=RetryConfig(max_attempts=3),
        )

        # Get first chunk then close
        async for chunk in gen:
            assert chunk == "chunk1"
            break

        # GeneratorExit should be handled gracefully
        await gen.aclose()
        assert cleanup_called

    @pytest.mark.asyncio
    async def test_generator_logs_retries(self, caplog):
        """Test generator logs retry attempts."""
        call_count = 0

        async def fails_initially():
            nonlocal call_count
            call_count += 1
            if call_count == 1:
                raise ConnectionError("Initial failure")
            yield "success"

        with caplog.at_level(logging.WARNING):
            results = []
            async for chunk in retry_async_generator(
                generator_factory=fails_initially,
                retryable_exceptions=(ConnectionError,),
                config=RetryConfig(max_attempts=3, base_delay=0.01, jitter=False),
            ):
                results.append(chunk)

        assert results == ["success"]
        retry_logs = [r for r in caplog.records if "Retry" in r.message]
        assert len(retry_logs) == 1
