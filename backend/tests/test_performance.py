"""Unit tests for performance monitoring utilities.

Tests the PerformanceTimer and async_perf_timer utilities.
"""

import asyncio
import logging
import time

import pytest

from app.utils.performance import PerformanceTimer, async_perf_timer


class TestPerformanceTimer:
    """Tests for PerformanceTimer class."""

    def test_timer_basic_usage(self, caplog):
        """Test basic timer usage."""
        with caplog.at_level(logging.DEBUG):
            timer = PerformanceTimer("test_operation")
            timer.start()
            time.sleep(0.01)  # 10ms
            timer.stop()

            assert timer.elapsed_ms >= 10  # Should be at least 10ms
            assert "[PERF] test_operation - " in caplog.text
            assert "ms" in caplog.text

    def test_timer_logs_at_specified_level(self, caplog):
        """Test that timer logs at the specified level."""
        # Test INFO level
        with caplog.at_level(logging.INFO):
            timer = PerformanceTimer("info_test", logging.INFO)
            timer.start()
            timer.stop()

            assert "[PERF] info_test - " in caplog.text

        caplog.clear()

        # Test DEBUG level (should not appear in INFO logs)
        with caplog.at_level(logging.INFO):
            timer = PerformanceTimer("debug_test", logging.DEBUG)
            timer.start()
            timer.stop()

            assert "debug_test" not in caplog.text

    def test_timer_elapsed_before_stop(self):
        """Test that elapsed_ms returns 0 before stop() is called."""
        timer = PerformanceTimer("test")
        timer.start()

        # elapsed_ms should return current elapsed time
        time.sleep(0.01)
        elapsed = timer.elapsed_ms

        assert elapsed >= 10  # Should be at least 10ms

    def test_timer_without_start(self, caplog):
        """Test timer.stop() without start() doesn't crash."""
        with caplog.at_level(logging.DEBUG):
            timer = PerformanceTimer("test")
            timer.stop()  # Should not crash

            # Should still log, elapsed will be 0
            assert "[PERF] test - " in caplog.text

    def test_timer_accuracy(self):
        """Test timer accuracy for known sleep duration."""
        timer = PerformanceTimer("accuracy_test")
        timer.start()
        time.sleep(0.05)  # 50ms
        timer.stop()

        # Should be close to 50ms (allow 10ms tolerance for system overhead)
        assert 40 <= timer.elapsed_ms <= 70

    def test_timer_name_in_log(self, caplog):
        """Test that timer name appears in log output."""
        with caplog.at_level(logging.DEBUG):
            timer = PerformanceTimer("my_custom_operation")
            timer.start()
            timer.stop()

            assert "my_custom_operation" in caplog.text

    def test_timer_multiple_operations(self, caplog):
        """Test multiple timers with different names."""
        with caplog.at_level(logging.DEBUG):
            timer1 = PerformanceTimer("operation_1")
            timer1.start()
            time.sleep(0.01)
            timer1.stop()

            timer2 = PerformanceTimer("operation_2")
            timer2.start()
            time.sleep(0.01)
            timer2.stop()

            assert "operation_1" in caplog.text
            assert "operation_2" in caplog.text


class TestAsyncPerfTimer:
    """Tests for async_perf_timer context manager."""

    @pytest.mark.asyncio
    async def test_async_timer_basic_usage(self, caplog):
        """Test async timer basic usage."""
        with caplog.at_level(logging.DEBUG):
            async with async_perf_timer("async_test"):
                await asyncio.sleep(0.02)  # 20ms

            assert "[PERF] async_test - " in caplog.text
            # Should show at least 20ms
            assert any(
                float(part.replace("ms", "")) >= 20 for part in caplog.text.split() if "ms" in part
            )

    @pytest.mark.asyncio
    async def test_async_timer_logs_at_specified_level(self, caplog):
        """Test async timer logs at specified level."""
        with caplog.at_level(logging.INFO):
            async with async_perf_timer("info_async", logging.INFO):
                await asyncio.sleep(0.01)

            assert "[PERF] info_async - " in caplog.text

        caplog.clear()

        # DEBUG level should not appear in INFO logs
        with caplog.at_level(logging.INFO):
            async with async_perf_timer("debug_async", logging.DEBUG):
                await asyncio.sleep(0.01)

            assert "debug_async" not in caplog.text

    @pytest.mark.asyncio
    async def test_async_timer_with_exception(self, caplog):
        """Test that async timer still logs when exception is raised."""
        with caplog.at_level(logging.DEBUG):
            with pytest.raises(ValueError):
                async with async_perf_timer("failing_operation"):
                    await asyncio.sleep(0.01)
                    raise ValueError("Test error")

            # Should still log the timing despite the exception
            assert "[PERF] failing_operation - " in caplog.text

    @pytest.mark.asyncio
    async def test_async_timer_yields_timer_instance(self):
        """Test that async_perf_timer yields a timer instance."""
        async with async_perf_timer("test") as timer:
            assert isinstance(timer, PerformanceTimer)
            assert timer.name == "test"

    @pytest.mark.asyncio
    async def test_async_timer_accuracy(self):
        """Test async timer accuracy."""
        async with async_perf_timer("accuracy") as timer:
            await asyncio.sleep(0.05)  # 50ms

        # Should be close to 50ms (allow 15ms tolerance for async overhead)
        assert 40 <= timer.elapsed_ms <= 75

    @pytest.mark.asyncio
    async def test_async_timer_nested(self, caplog):
        """Test nested async timers."""
        with caplog.at_level(logging.DEBUG):
            async with async_perf_timer("outer"):
                await asyncio.sleep(0.01)
                async with async_perf_timer("inner"):
                    await asyncio.sleep(0.01)
                await asyncio.sleep(0.01)

            assert "[PERF] outer - " in caplog.text
            assert "[PERF] inner - " in caplog.text

    @pytest.mark.asyncio
    async def test_async_timer_concurrent_operations(self, caplog):
        """Test multiple concurrent async timers."""
        with caplog.at_level(logging.DEBUG):

            async def timed_operation(name: str, duration: float):
                async with async_perf_timer(name):
                    await asyncio.sleep(duration)

            # Run concurrent operations
            await asyncio.gather(
                timed_operation("op1", 0.02),
                timed_operation("op2", 0.03),
                timed_operation("op3", 0.01),
            )

            assert "[PERF] op1 - " in caplog.text
            assert "[PERF] op2 - " in caplog.text
            assert "[PERF] op3 - " in caplog.text

    @pytest.mark.asyncio
    async def test_async_timer_formatting(self, caplog):
        """Test that timer output is properly formatted."""
        with caplog.at_level(logging.DEBUG):
            async with async_perf_timer("format_test"):
                await asyncio.sleep(0.01)

            # Check format: "[PERF] format_test - XX.XXms"
            assert "[PERF] format_test - " in caplog.text
            assert "ms" in caplog.text
            # Should have decimal point
            assert "." in caplog.text


class TestPerformanceIntegration:
    """Integration tests for performance monitoring in realistic scenarios."""

    @pytest.mark.asyncio
    async def test_simulated_api_endpoint_timing(self, caplog):
        """Test timing a simulated API endpoint."""
        with caplog.at_level(logging.INFO):

            async def simulated_endpoint():
                async with async_perf_timer("api.request", logging.INFO):
                    # Simulate database query
                    async with async_perf_timer("api.database_query", logging.DEBUG):
                        await asyncio.sleep(0.02)

                    # Simulate LLM call
                    async with async_perf_timer("api.llm_call", logging.INFO):
                        await asyncio.sleep(0.05)

                    # Simulate response serialization
                    async with async_perf_timer("api.serialize", logging.DEBUG):
                        await asyncio.sleep(0.01)

            await simulated_endpoint()

            # INFO level logs should appear
            assert "[PERF] api.request - " in caplog.text
            assert "[PERF] api.llm_call - " in caplog.text

            # DEBUG level logs should not appear in INFO
            assert "api.database_query" not in caplog.text
            assert "api.serialize" not in caplog.text

    @pytest.mark.asyncio
    async def test_timer_overhead(self):
        """Test that timer overhead is minimal."""
        # Measure without timer
        start = time.perf_counter()
        await asyncio.sleep(0.01)
        no_timer_duration = time.perf_counter() - start

        # Measure with timer
        async with async_perf_timer("overhead_test") as timer:
            await asyncio.sleep(0.01)

        # Timer overhead should be less than 5ms
        overhead = timer.elapsed_ms - (no_timer_duration * 1000)
        assert overhead < 5

    def test_synchronous_timer_in_sync_context(self, caplog):
        """Test that PerformanceTimer works in synchronous context."""
        with caplog.at_level(logging.DEBUG):
            timer = PerformanceTimer("sync_operation")
            timer.start()

            # Simulate work
            total = 0
            for i in range(10000):
                total += i

            timer.stop()

            assert "[PERF] sync_operation - " in caplog.text
            assert timer.elapsed_ms > 0
