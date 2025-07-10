import unittest
from unittest.mock import Mock, patch

import dspy  # type: ignore

from amzn_nova_prompt_optimizer.core.optimizers.miprov2.custom_lm.rate_limited_lm import RateLimitedLM


class TestRateLimitedLM(unittest.TestCase):
    def setUp(self):
        self.mock_lm = Mock()
        self.rate_limited_lm = RateLimitedLM(self.mock_lm, rate_limit=2)

    def test_initialization(self):
        """Test RateLimitedLM initialization"""
        self.assertIsInstance(self.rate_limited_lm, dspy.LM)
        self.assertEqual(self.rate_limited_lm.wrapped_model, self.mock_lm)
        self.assertEqual(self.rate_limited_lm.rate_limiter.rate_limit, 2)

    def test_custom_rate_limit(self):
        """Test initialization with custom rate limit"""
        # Act
        custom_lm = RateLimitedLM(self.mock_lm, rate_limit=5)

        # Assert
        self.assertEqual(custom_lm.rate_limiter.rate_limit, 5)

    @patch('amzn_nova_prompt_optimizer.util.rate_limiter.RateLimiter.apply_rate_limiting')
    def test_call_applies_rate_limiting(self, mock_rate_limiting):
        """Test that calling RateLimitedLM applies rate limiting"""
        # Arrange
        expected_result = "test response"
        self.mock_lm.return_value = expected_result
        
        # Act
        result = self.rate_limited_lm("test prompt")
        
        # Assert
        mock_rate_limiting.assert_called_once()
        self.mock_lm.assert_called_once_with("test prompt")
        self.assertEqual(result, expected_result)

    @patch('amzn_nova_prompt_optimizer.util.rate_limiter.RateLimiter.apply_rate_limiting')
    def test_call_with_kwargs(self, mock_rate_limiting):
        """Test calling with keyword arguments"""
        # Arrange
        expected_result = "test response"
        self.mock_lm.return_value = expected_result
        
        # Act
        result = self.rate_limited_lm("test prompt", temperature=0.7, max_tokens=100)
        
        # Assert
        mock_rate_limiting.assert_called_once()
        self.mock_lm.assert_called_once_with("test prompt", temperature=0.7, max_tokens=100)
        self.assertEqual(result, expected_result)

    def test_getattr_delegates_to_wrapped_model(self):
        """Test that attribute access is delegated to base_model"""
        # Arrange
        self.mock_lm.some_attribute = "test_value"
        
        # Act & Assert
        self.assertEqual(self.rate_limited_lm.some_attribute, "test_value")

    @patch('time.time')
    @patch('time.sleep')
    def test_apply_rate_limiting_no_limit_reached(self, mock_sleep, mock_time):
        """Test rate limiting with multiple calls in quick succession"""
        # Mock time to simulate calls within 1 second
        mock_time.return_value = 100.0
        self.rate_limited_lm.rate_limiter.rate_limit = 5

        # Add some timestamps that are within rate limit
        self.rate_limited_lm.rate_limiter.request_timestamps = [99.5, 99.7, 99.9]  # 3 requests in last second

        # Act
        self.rate_limited_lm.__call__()

        # Assert
        mock_sleep.assert_not_called()
        self.assertEqual(len(self.rate_limited_lm.rate_limiter.request_timestamps), 4)  # Original 3 + 1 new
        self.assertEqual(self.rate_limited_lm.rate_limiter.waiting_requests_count, 0)

    @patch('time.time')
    @patch('time.sleep')
    @patch('random.uniform')
    def test_apply_rate_limiting_limit_reached(self, mock_random, mock_sleep, mock_time):
        """Test rate limiting when limit is reached"""
        # Arrange
        mock_time.side_effect = [100.0, 100.0, 100.1]  # Current time calls
        mock_random.return_value = 0.9
        self.rate_limited_lm.rate_limiter.rate_limit = 3

        # Fill up to rate limit
        self.rate_limited_lm.rate_limiter.request_timestamps = [99.5, 99.7, 99.9]  # 3 requests in last second

        # Act
        self.rate_limited_lm.__call__()

        # Assert
        mock_sleep.assert_called_once()
        # Verify sleep time is positive (exact value depends on random component)
        sleep_args = mock_sleep.call_args[0]
        self.assertGreater(sleep_args[0], 0)
