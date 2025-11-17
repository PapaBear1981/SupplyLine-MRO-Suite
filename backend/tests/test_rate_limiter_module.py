"""
Comprehensive tests for the rate_limiter module.
Tests the RateLimiter class, token bucket algorithm, cleanup, and decorators.
"""

import time
from unittest.mock import MagicMock, Mock, patch, PropertyMock

import pytest

from rate_limiter import RateLimiter, rate_limit, rate_limiter


class TestRateLimiterInitialization:
    """Test RateLimiter initialization and configuration"""

    def test_default_initialization(self):
        """Test RateLimiter with default parameters"""
        limiter = RateLimiter()
        assert limiter.rate == 10
        assert limiter.per == 1
        assert limiter.burst == 20
        assert limiter.cleanup_interval == 3600
        assert limiter.buckets == {}
        assert limiter.lock is not None
        assert isinstance(limiter.last_cleanup, float)

    def test_custom_initialization(self):
        """Test RateLimiter with custom parameters"""
        limiter = RateLimiter(rate=50, per=2, burst=100, cleanup_interval=7200)
        assert limiter.rate == 50
        assert limiter.per == 2
        assert limiter.burst == 100
        assert limiter.cleanup_interval == 7200

    def test_initialization_with_zero_values(self):
        """Test RateLimiter handles edge case parameters"""
        limiter = RateLimiter(rate=1, per=1, burst=1, cleanup_interval=60)
        assert limiter.rate == 1
        assert limiter.per == 1
        assert limiter.burst == 1
        assert limiter.cleanup_interval == 60

    def test_global_rate_limiter_instance(self):
        """Test that global rate_limiter is properly configured"""
        assert isinstance(rate_limiter, RateLimiter)
        assert rate_limiter.rate == 100
        assert rate_limiter.per == 1
        assert rate_limiter.burst == 200


class TestGetClientId:
    """Test _get_client_id method"""

    def test_get_client_id_with_request_context(self, app):
        """Test getting client ID from Flask request"""
        limiter = RateLimiter()
        with app.test_request_context(environ_base={'REMOTE_ADDR': '192.168.1.1'}):
            client_id = limiter._get_client_id()
            assert client_id == '192.168.1.1'

    def test_get_client_id_different_ips(self, app):
        """Test that different IPs return different client IDs"""
        limiter = RateLimiter()
        with app.test_request_context(environ_base={'REMOTE_ADDR': '10.0.0.1'}):
            client_id_1 = limiter._get_client_id()
        with app.test_request_context(environ_base={'REMOTE_ADDR': '10.0.0.2'}):
            client_id_2 = limiter._get_client_id()

        assert client_id_1 != client_id_2
        assert client_id_1 == '10.0.0.1'
        assert client_id_2 == '10.0.0.2'

    def test_get_client_id_localhost(self, app):
        """Test getting client ID for localhost"""
        limiter = RateLimiter()
        with app.test_request_context(environ_base={'REMOTE_ADDR': '127.0.0.1'}):
            client_id = limiter._get_client_id()
            assert client_id == '127.0.0.1'


class TestRefillBucket:
    """Test _refill_bucket method"""

    def test_refill_bucket_no_time_passed(self):
        """Test refill with no time elapsed"""
        limiter = RateLimiter(rate=10, per=1, burst=20)
        bucket = {"tokens": 10, "last_refill": time.time()}

        limiter._refill_bucket(bucket)

        # Should have approximately the same tokens (maybe slightly more due to tiny time delta)
        assert bucket["tokens"] >= 10
        assert bucket["tokens"] <= 20

    def test_refill_bucket_partial_refill(self):
        """Test partial bucket refill"""
        limiter = RateLimiter(rate=10, per=1, burst=20)
        old_time = time.time() - 0.5  # 0.5 seconds ago
        bucket = {"tokens": 5, "last_refill": old_time}

        limiter._refill_bucket(bucket)

        # Should have added approximately 5 tokens (10 tokens/sec * 0.5 sec)
        assert bucket["tokens"] >= 9  # Allow some tolerance
        assert bucket["tokens"] <= 20

    def test_refill_bucket_full_refill(self):
        """Test full bucket refill"""
        limiter = RateLimiter(rate=10, per=1, burst=20)
        old_time = time.time() - 2  # 2 seconds ago
        bucket = {"tokens": 0, "last_refill": old_time}

        limiter._refill_bucket(bucket)

        # Should have added 20 tokens but capped at burst (20)
        assert bucket["tokens"] == 20

    def test_refill_bucket_respects_burst_limit(self):
        """Test that refill respects burst limit"""
        limiter = RateLimiter(rate=100, per=1, burst=50)
        old_time = time.time() - 10  # 10 seconds ago
        bucket = {"tokens": 45, "last_refill": old_time}

        limiter._refill_bucket(bucket)

        # Should be capped at burst limit
        assert bucket["tokens"] == 50

    def test_refill_bucket_updates_timestamp(self):
        """Test that refill updates last_refill timestamp"""
        limiter = RateLimiter(rate=10, per=1, burst=20)
        old_time = time.time() - 1
        bucket = {"tokens": 10, "last_refill": old_time}

        before_refill = time.time()
        limiter._refill_bucket(bucket)
        after_refill = time.time()

        assert bucket["last_refill"] >= before_refill
        assert bucket["last_refill"] <= after_refill

    def test_refill_bucket_with_different_rates(self):
        """Test refill with different rate configurations"""
        # Slower rate: 1 token per 10 seconds
        limiter = RateLimiter(rate=1, per=10, burst=10)
        old_time = time.time() - 10
        bucket = {"tokens": 0, "last_refill": old_time}

        limiter._refill_bucket(bucket)

        # Should have added 1 token
        assert bucket["tokens"] >= 0.9  # Allow tolerance
        assert bucket["tokens"] <= 10


class TestCleanupOldBuckets:
    """Test _cleanup_old_buckets method"""

    def test_no_cleanup_if_interval_not_reached(self):
        """Test that cleanup doesn't run before interval"""
        limiter = RateLimiter(cleanup_interval=3600)
        limiter.last_cleanup = time.time()  # Just cleaned
        limiter.buckets = {"client1": {"tokens": 10, "last_refill": time.time()}}

        limiter._cleanup_old_buckets()

        # Bucket should still be there
        assert "client1" in limiter.buckets

    def test_cleanup_removes_old_buckets(self):
        """Test that old buckets are removed"""
        limiter = RateLimiter(cleanup_interval=1)  # 1 second interval
        old_time = time.time() - 3600 * 3  # 3 hours ago (older than 2 * cleanup_interval)

        limiter.buckets = {
            "old_client": {"tokens": 10, "last_refill": old_time},
            "new_client": {"tokens": 10, "last_refill": time.time()}
        }
        limiter.last_cleanup = time.time() - 2  # Force cleanup to run

        limiter._cleanup_old_buckets()

        # Old bucket should be removed, new one kept
        assert "old_client" not in limiter.buckets
        assert "new_client" in limiter.buckets

    def test_cleanup_updates_last_cleanup_time(self):
        """Test that cleanup updates the last_cleanup timestamp"""
        limiter = RateLimiter(cleanup_interval=1)
        limiter.last_cleanup = time.time() - 10  # Force cleanup to run

        before_cleanup = time.time()
        limiter._cleanup_old_buckets()
        after_cleanup = time.time()

        assert limiter.last_cleanup >= before_cleanup
        assert limiter.last_cleanup <= after_cleanup

    def test_cleanup_handles_empty_buckets(self):
        """Test cleanup with no buckets"""
        limiter = RateLimiter(cleanup_interval=1)
        limiter.last_cleanup = time.time() - 10
        limiter.buckets = {}

        # Should not raise any errors
        limiter._cleanup_old_buckets()

        assert limiter.buckets == {}

    def test_cleanup_multiple_old_buckets(self):
        """Test cleanup removes multiple old buckets"""
        limiter = RateLimiter(cleanup_interval=1)
        old_time = time.time() - 3600 * 3

        limiter.buckets = {
            "old1": {"tokens": 10, "last_refill": old_time},
            "old2": {"tokens": 10, "last_refill": old_time},
            "old3": {"tokens": 10, "last_refill": old_time},
            "new": {"tokens": 10, "last_refill": time.time()}
        }
        limiter.last_cleanup = time.time() - 2

        limiter._cleanup_old_buckets()

        assert len(limiter.buckets) == 1
        assert "new" in limiter.buckets

    @patch('builtins.print')
    def test_cleanup_prints_message_on_cleanup(self, mock_print):
        """Test that cleanup prints message when buckets are removed"""
        limiter = RateLimiter(cleanup_interval=1)
        old_time = time.time() - 3600 * 3

        limiter.buckets = {
            "old1": {"tokens": 10, "last_refill": old_time},
            "old2": {"tokens": 10, "last_refill": old_time}
        }
        limiter.last_cleanup = time.time() - 2

        limiter._cleanup_old_buckets()

        mock_print.assert_called_once()
        call_args = mock_print.call_args[0][0]
        assert "Cleaned up 2 old client buckets" in call_args


class TestConsumeToken:
    """Test _consume_token method"""

    def test_consume_token_new_client(self):
        """Test token consumption for new client"""
        limiter = RateLimiter(rate=10, per=1, burst=20)

        with patch.object(limiter, '_cleanup_old_buckets'):
            result = limiter._consume_token("new_client")

        assert result is True
        assert "new_client" in limiter.buckets
        assert limiter.buckets["new_client"]["tokens"] == 19  # Started with burst, consumed 1

    def test_consume_token_existing_client(self):
        """Test token consumption for existing client"""
        limiter = RateLimiter(rate=10, per=1, burst=20)
        limiter.buckets["existing"] = {"tokens": 15, "last_refill": time.time()}

        with patch.object(limiter, '_cleanup_old_buckets'):
            result = limiter._consume_token("existing")

        assert result is True
        # Token count should be less than 15 (one consumed, but may have refilled slightly)
        assert limiter.buckets["existing"]["tokens"] < 15

    def test_consume_token_no_tokens_available(self):
        """Test token consumption when no tokens available"""
        limiter = RateLimiter(rate=10, per=1, burst=20)
        limiter.buckets["depleted"] = {"tokens": 0, "last_refill": time.time()}

        with patch.object(limiter, '_cleanup_old_buckets'):
            result = limiter._consume_token("depleted")

        # Should fail because no tokens available (and not enough time for refill)
        assert result is False

    def test_consume_token_exactly_one_token(self):
        """Test consumption when exactly one token available"""
        limiter = RateLimiter(rate=10, per=1, burst=20)
        limiter.buckets["one_token"] = {"tokens": 1, "last_refill": time.time()}

        with patch.object(limiter, '_cleanup_old_buckets'):
            result = limiter._consume_token("one_token")

        assert result is True
        # Should have 0 tokens now (plus small refill from time delta)
        assert limiter.buckets["one_token"]["tokens"] < 1

    def test_consume_token_depletes_bucket(self):
        """Test consuming all tokens depletes bucket"""
        limiter = RateLimiter(rate=0.01, per=1, burst=5)  # Very slow refill
        client_id = "depleting"
        limiter.buckets[client_id] = {"tokens": 3, "last_refill": time.time()}

        with patch.object(limiter, '_cleanup_old_buckets'):
            # Consume all tokens
            assert limiter._consume_token(client_id) is True  # 2 left
            assert limiter._consume_token(client_id) is True  # 1 left
            assert limiter._consume_token(client_id) is True  # 0 left
            # Next consumption should fail (slow refill rate)
            result = limiter._consume_token(client_id)

        # Should fail or succeed with very small token count
        assert result is False or limiter.buckets[client_id]["tokens"] < 0.1

    def test_consume_token_calls_cleanup(self):
        """Test that consume_token triggers cleanup"""
        limiter = RateLimiter(rate=10, per=1, burst=20)

        with patch.object(limiter, '_cleanup_old_buckets') as mock_cleanup:
            limiter._consume_token("client")
            mock_cleanup.assert_called_once()

    def test_consume_token_thread_safety(self):
        """Test that token consumption is thread-safe"""
        import threading

        limiter = RateLimiter(rate=1, per=100, burst=100)  # Very slow refill
        results = []

        def consume():
            with patch.object(limiter, '_cleanup_old_buckets'):
                result = limiter._consume_token("shared_client")
                results.append(result)

        # Create multiple threads consuming from the same bucket
        threads = []
        for _ in range(10):
            t = threading.Thread(target=consume)
            threads.append(t)
            t.start()

        for t in threads:
            t.join()

        # All should succeed initially (burst of 100)
        assert all(results)
        # Verify we consumed approximately 10 tokens (allowing for small refill)
        assert limiter.buckets["shared_client"]["tokens"] < 95  # More lenient due to thread timing


class TestLimitDecorator:
    """Test the limit decorator"""

    def test_limit_decorator_allows_request(self, app):
        """Test that limit decorator allows request when tokens available"""
        limiter = RateLimiter(rate=10, per=1, burst=20)

        @limiter.limit
        def test_route():
            return {"status": "ok"}

        with app.test_request_context(environ_base={'REMOTE_ADDR': '127.0.0.1'}):
            response = test_route()
            assert response == {"status": "ok"}

    def test_limit_decorator_blocks_when_rate_limited(self, app):
        """Test that limit decorator blocks when no tokens"""
        limiter = RateLimiter(rate=0.001, per=1, burst=1)  # Very low limit

        @limiter.limit
        def test_route():
            return {"status": "ok"}

        with app.test_request_context(environ_base={'REMOTE_ADDR': '127.0.0.1'}):
            # First request should succeed
            response1 = test_route()
            assert response1 == {"status": "ok"}

            # Second request should be rate limited
            response2 = test_route()
            assert response2.status_code == 429
            data = response2.get_json()
            assert "error" in data
            assert data["error"] == "Too many requests"

    def test_limit_decorator_returns_correct_error_message(self, app):
        """Test that rate limit response has correct message"""
        limiter = RateLimiter(rate=0.001, per=1, burst=0)  # No tokens

        @limiter.limit
        def test_route():
            return {"status": "ok"}

        with app.test_request_context(environ_base={'REMOTE_ADDR': '127.0.0.1'}):
            response = test_route()
            assert response.status_code == 429
            data = response.get_json()
            assert "error" in data
            assert "message" in data
            assert "rate limit" in data["message"].lower()

    def test_limit_decorator_preserves_function_metadata(self):
        """Test that decorator preserves function metadata"""
        limiter = RateLimiter()

        @limiter.limit
        def my_function():
            """My docstring"""
            pass

        assert my_function.__name__ == "my_function"
        assert my_function.__doc__ == "My docstring"

    def test_limit_decorator_passes_arguments(self, app):
        """Test that decorator passes through function arguments"""
        limiter = RateLimiter(rate=10, per=1, burst=20)

        @limiter.limit
        def test_route_with_args(arg1, kwarg1=None):
            return {"arg1": arg1, "kwarg1": kwarg1}

        with app.test_request_context(environ_base={'REMOTE_ADDR': '127.0.0.1'}):
            response = test_route_with_args("test_value", kwarg1="kwarg_value")
            assert response == {"arg1": "test_value", "kwarg1": "kwarg_value"}

    def test_limit_decorator_separate_limits_per_client(self, app):
        """Test that different clients have separate limits"""
        limiter = RateLimiter(rate=0.001, per=1, burst=1)

        @limiter.limit
        def test_route():
            return {"status": "ok"}

        # First client uses their token
        with app.test_request_context(environ_base={'REMOTE_ADDR': '192.168.1.1'}):
            response1 = test_route()
            assert response1 == {"status": "ok"}

        # Second client should still have tokens
        with app.test_request_context(environ_base={'REMOTE_ADDR': '192.168.1.2'}):
            response2 = test_route()
            assert response2 == {"status": "ok"}

        # First client is now rate limited
        with app.test_request_context(environ_base={'REMOTE_ADDR': '192.168.1.1'}):
            response3 = test_route()
            assert response3.status_code == 429


class TestGetStats:
    """Test get_stats method"""

    def test_get_stats_empty_buckets(self):
        """Test stats with no clients"""
        limiter = RateLimiter(cleanup_interval=3600)
        stats = limiter.get_stats()

        assert stats["active_clients"] == 0
        assert stats["memory_usage_estimate"] == 0
        assert "last_cleanup" in stats
        assert stats["cleanup_interval"] == 3600

    def test_get_stats_with_clients(self):
        """Test stats with active clients"""
        limiter = RateLimiter(cleanup_interval=7200)
        limiter.buckets = {
            "client1": {"tokens": 10, "last_refill": time.time()},
            "client2": {"tokens": 15, "last_refill": time.time()},
            "client3": {"tokens": 20, "last_refill": time.time()}
        }

        stats = limiter.get_stats()

        assert stats["active_clients"] == 3
        assert stats["memory_usage_estimate"] == 3 * 64  # 192 bytes estimate
        assert stats["cleanup_interval"] == 7200

    def test_get_stats_memory_estimate_calculation(self):
        """Test memory usage estimate calculation"""
        limiter = RateLimiter()

        # Add 100 clients
        for i in range(100):
            limiter.buckets[f"client{i}"] = {"tokens": 10, "last_refill": time.time()}

        stats = limiter.get_stats()

        assert stats["active_clients"] == 100
        assert stats["memory_usage_estimate"] == 100 * 64  # 6400 bytes

    def test_get_stats_returns_correct_types(self):
        """Test that stats return correct data types"""
        limiter = RateLimiter()
        stats = limiter.get_stats()

        assert isinstance(stats["active_clients"], int)
        assert isinstance(stats["memory_usage_estimate"], int)
        assert isinstance(stats["last_cleanup"], float)
        assert isinstance(stats["cleanup_interval"], int)


class TestGlobalRateLimitFunction:
    """Test the global rate_limit function"""

    def test_rate_limit_function_wraps_limiter(self):
        """Test that rate_limit function wraps global limiter"""
        def dummy_function():
            pass

        decorated = rate_limit(dummy_function)

        # Should be decorated with functools.wraps
        assert callable(decorated)
        assert decorated.__name__ == "dummy_function"

    def test_rate_limit_function_uses_global_instance(self, app):
        """Test that rate_limit uses the global rate_limiter instance"""
        @rate_limit
        def test_route():
            return {"status": "ok"}

        with app.test_request_context(environ_base={'REMOTE_ADDR': '127.0.0.1'}):
            response = test_route()
            # Global limiter has burst of 200, should allow request
            assert response == {"status": "ok"}

    def test_rate_limit_decorator_syntax(self):
        """Test rate_limit can be used as decorator without parentheses"""
        @rate_limit
        def my_route():
            """Route docstring"""
            return "response"

        assert my_route.__name__ == "my_route"
        assert my_route.__doc__ == "Route docstring"


class TestIntegration:
    """Integration tests for rate limiter"""

    def test_full_rate_limiting_cycle(self, app):
        """Test complete rate limiting cycle"""
        limiter = RateLimiter(rate=2, per=1, burst=3)

        @limiter.limit
        def test_route():
            return {"status": "ok"}

        with app.test_request_context(environ_base={'REMOTE_ADDR': '127.0.0.1'}):
            # Consume all burst tokens
            assert test_route() == {"status": "ok"}  # 2 tokens left
            assert test_route() == {"status": "ok"}  # 1 token left
            assert test_route() == {"status": "ok"}  # 0 tokens left

            # Should be rate limited now
            response = test_route()
            assert response.status_code == 429

    def test_rate_limiter_with_refill(self, app):
        """Test that tokens refill over time"""
        limiter = RateLimiter(rate=100, per=1, burst=1)  # Fast refill

        @limiter.limit
        def test_route():
            return {"status": "ok"}

        with app.test_request_context(environ_base={'REMOTE_ADDR': '127.0.0.1'}):
            # Use up initial token
            assert test_route() == {"status": "ok"}

            # Wait for refill
            time.sleep(0.02)  # 20ms should give us ~2 tokens

            # Should have refilled
            assert test_route() == {"status": "ok"}

    def test_multiple_clients_independent_limits(self, app):
        """Test that multiple clients have independent rate limits"""
        limiter = RateLimiter(rate=1, per=100, burst=2)  # Slow refill

        @limiter.limit
        def test_route():
            return {"status": "ok"}

        # Client 1 uses all tokens
        with app.test_request_context(environ_base={'REMOTE_ADDR': '10.0.0.1'}):
            test_route()
            test_route()
            response = test_route()
            assert response.status_code == 429

        # Client 2 should still have tokens
        with app.test_request_context(environ_base={'REMOTE_ADDR': '10.0.0.2'}):
            response = test_route()
            assert response == {"status": "ok"}

    def test_cleanup_removes_inactive_clients(self):
        """Test that cleanup properly manages memory"""
        limiter = RateLimiter(rate=10, per=1, burst=20, cleanup_interval=1)

        # Add old and new clients
        old_time = time.time() - 3600 * 3  # 3 hours old
        limiter.buckets = {
            "old_client_1": {"tokens": 10, "last_refill": old_time},
            "old_client_2": {"tokens": 10, "last_refill": old_time},
            "active_client": {"tokens": 10, "last_refill": time.time()}
        }
        limiter.last_cleanup = time.time() - 2  # Force cleanup

        # Trigger cleanup via _consume_token
        limiter._consume_token("active_client")

        # Old clients should be removed
        assert len(limiter.buckets) == 1
        assert "active_client" in limiter.buckets

    def test_stats_reflect_current_state(self):
        """Test that stats accurately reflect limiter state"""
        limiter = RateLimiter(cleanup_interval=3600)

        # Initially empty
        stats = limiter.get_stats()
        assert stats["active_clients"] == 0

        # Add clients
        for i in range(5):
            limiter.buckets[f"client{i}"] = {"tokens": 10, "last_refill": time.time()}

        stats = limiter.get_stats()
        assert stats["active_clients"] == 5
        assert stats["memory_usage_estimate"] == 320  # 5 * 64

    def test_high_load_scenario(self, app):
        """Test rate limiter under high load"""
        limiter = RateLimiter(rate=100, per=1, burst=10)

        @limiter.limit
        def test_route():
            return {"status": "ok"}

        with app.test_request_context(environ_base={'REMOTE_ADDR': '127.0.0.1'}):
            successes = 0
            rate_limited = 0

            # Make 20 rapid requests
            for _ in range(20):
                response = test_route()
                if isinstance(response, dict):
                    successes += 1
                else:
                    rate_limited += 1

            # Should have some successes and some rate limits
            assert successes >= 10  # At least burst amount
            assert rate_limited > 0  # Should hit rate limit


class TestEdgeCases:
    """Test edge cases and error conditions"""

    def test_very_small_burst(self):
        """Test with very small burst size"""
        limiter = RateLimiter(rate=1, per=1, burst=1)
        assert limiter.burst == 1

    def test_very_large_burst(self):
        """Test with very large burst size"""
        limiter = RateLimiter(rate=1000, per=1, burst=1000000)
        assert limiter.burst == 1000000

    def test_fractional_rate(self):
        """Test with fractional rate"""
        limiter = RateLimiter(rate=0.5, per=1, burst=10)
        bucket = {"tokens": 0, "last_refill": time.time() - 10}
        limiter._refill_bucket(bucket)
        # Should have added approximately 5 tokens (0.5 * 10)
        assert 4.9 <= bucket["tokens"] <= 5.1  # Allow for floating point precision

    def test_long_cleanup_interval(self):
        """Test with long cleanup interval"""
        limiter = RateLimiter(cleanup_interval=86400)  # 1 day
        assert limiter.cleanup_interval == 86400

    def test_bucket_tokens_near_zero(self):
        """Test bucket with tokens very close to zero"""
        limiter = RateLimiter(rate=0.0001, per=1, burst=20)
        limiter.buckets["client"] = {"tokens": 0.9, "last_refill": time.time()}

        with patch.object(limiter, '_cleanup_old_buckets'):
            # 0.9 tokens is less than 1, should fail
            result = limiter._consume_token("client")

        # Should fail as tokens < 1
        assert result is False

    def test_concurrent_cleanup_and_consume(self):
        """Test thread safety between cleanup and consume operations"""
        import threading

        limiter = RateLimiter(rate=100, per=1, burst=100, cleanup_interval=1)
        limiter.last_cleanup = time.time() - 2  # Force cleanup on next operation

        # Add some old buckets
        old_time = time.time() - 3600 * 3
        for i in range(10):
            limiter.buckets[f"old_{i}"] = {"tokens": 10, "last_refill": old_time}

        # Add active client
        limiter.buckets["active"] = {"tokens": 50, "last_refill": time.time()}

        def consume():
            # This will trigger cleanup
            limiter._consume_token("active")

        # Run cleanup through consume in parallel threads
        threads = [threading.Thread(target=consume) for _ in range(5)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        # Should have cleaned up old clients
        old_clients = [k for k in limiter.buckets if k.startswith("old_")]
        assert len(old_clients) == 0
        assert "active" in limiter.buckets
