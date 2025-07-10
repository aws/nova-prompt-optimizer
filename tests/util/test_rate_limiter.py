import threading
import unittest
from unittest.mock import patch

import time

from amzn_nova_prompt_optimizer.util.rate_limiter import RateLimiter


class TestRateLimiter(unittest.TestCase):
    def setUp(self):
        self.rate_limiter = RateLimiter(rate_limit=5)

    @patch('time.time')
    @patch('time.sleep')
    def test_rate_limit_disabled(self, mock_sleep, mock_time):
        """Test rate limiting disabled when rate_limit <=0 """
        # Arrange
        mock_time.return_value = 100.0
        self.rate_limiter.rate_limit = -1

        # Act
        self.rate_limiter.apply_rate_limiting()

        # Assert
        mock_sleep.assert_not_called()
        self.assertEqual(len(self.rate_limiter.request_timestamps), 0)  # No request timestamps recorded
        self.assertEqual(self.rate_limiter.waiting_requests_count, 0)

    @patch('time.time')
    @patch('time.sleep')
    def test_apply_rate_limiting_no_limit_reached(self, mock_sleep, mock_time):
        """Test rate limiting when limit is not reached"""
        # Arrange
        mock_time.return_value = 100.0
        self.rate_limiter.rate_limit = 5

        # Add some timestamps that are within rate limit
        self.rate_limiter.request_timestamps = [99.5, 99.7, 99.9]  # 3 requests in last second

        # Act
        self.rate_limiter.apply_rate_limiting()

        # Assert
        mock_sleep.assert_not_called()
        self.assertEqual(len(self.rate_limiter.request_timestamps), 4)  # Original 3 + 1 new
        self.assertEqual(self.rate_limiter.waiting_requests_count, 0)

    @patch('time.time')
    @patch('time.sleep')
    @patch('random.uniform')
    def test_apply_rate_limiting_limit_reached(self, mock_random, mock_sleep, mock_time):
        """Test rate limiting when limit is reached"""
        # Arrange
        mock_time.side_effect = [100.0, 100.0, 100.1]  # Current time calls
        mock_random.return_value = 0.9
        self.rate_limiter.rate_limit = 3

        # Fill up to rate limit
        self.rate_limiter.request_timestamps = [99.5, 99.7, 99.9]  # 3 requests in last second

        # Act
        self.rate_limiter.apply_rate_limiting()

        # Assert
        mock_sleep.assert_called_once()
        # Verify sleep time is positive (exact value depends on random component)
        sleep_args = mock_sleep.call_args[0]
        self.assertGreater(sleep_args[0], 0)

    @patch('time.time')
    @patch('time.sleep')
    def test_apply_rate_limiting_old_timestamps_removed(self, mock_sleep, mock_time):
        """Test that old timestamps are properly removed"""
        # Arrange
        mock_time.return_value = 100.0
        self.rate_limiter.rate_limit = 5

        # Add timestamps - some old (>1 second) and some recent
        self.rate_limiter.request_timestamps = [98.5, 98.8, 99.2, 99.5, 99.8]  # Mix of old and recent

        # Act
        self.rate_limiter.apply_rate_limiting()

        # Assert
        # Only timestamps from last second should remain (99.2, 99.5, 99.8) + new one
        self.assertEqual(len(self.rate_limiter.request_timestamps), 4)
        for timestamp in self.rate_limiter.request_timestamps[:-1]:  # Exclude the newly added one
            self.assertGreaterEqual(timestamp, 99.0)  # All should be within last second

    @patch('time.time')
    @patch('time.sleep')
    @patch('random.uniform')
    def test_apply_rate_limiting_sleep_calculation(self, mock_random, mock_sleep, mock_time):
        """Test sleep time calculation with predictable random value"""
        # Arrange
        mock_time.side_effect = [100.0, 100.0, 100.1]
        mock_random.return_value = 0.5  # Fixed random value for predictable testing
        self.rate_limiter.rate_limit = 2

        # Set up scenario where rate limit is reached
        self.rate_limiter.request_timestamps = [99.5, 99.8]  # 2 requests, rate limit is 2
        self.rate_limiter.waiting_requests_count = 0

        # Act
        self.rate_limiter.apply_rate_limiting()

        # Assert
        mock_sleep.assert_called_once()
        # Verify the sleep calculation: ((waiting_requests_count/rate_limit) * 1.0) - (current_time - oldest_timestamp) + random
        # Expected: ((1/2) * 1.0) - (100.0 - 99.5) + 0.5 = 0.5 - 0.5 + 0.5 = 0.5
        expected_sleep_time = 0.5
        actual_sleep_time = mock_sleep.call_args[0][0]
        self.assertAlmostEqual(actual_sleep_time, expected_sleep_time, places=2)

    @patch('time.time')
    @patch('time.sleep')
    def test_apply_rate_limiting_waiting_requests_count_management(self, mock_sleep, mock_time):
        """Test waiting_requests_count is properly managed"""
        # Arrange
        mock_time.side_effect = [100.0, 100.0, 100.1]
        self.rate_limiter.rate_limit = 2

        # Set up scenario where rate limit is reached
        self.rate_limiter.request_timestamps = [99.5, 99.8]
        self.rate_limiter.waiting_requests_count = 0

        # Act
        self.rate_limiter.apply_rate_limiting()

        # Assert
        self.assertEqual(self.rate_limiter.waiting_requests_count, 0)  # Should be decremented back to 0

    @patch('time.time')
    @patch('time.sleep')
    def test_apply_rate_limiting_negative_sleep_time(self, mock_sleep, mock_time):
        """Test that negative sleep times don't cause sleep"""
        # Arrange
        mock_time.side_effect = [100.0, 100.0, 100.1]
        self.rate_limiter.rate_limit = 2

        # Set up scenario where calculated sleep time would be negative
        self.rate_limiter.request_timestamps = [98.0, 98.5]  # Old timestamps
        self.rate_limiter.waiting_requests_count = 0

        # Act
        self.rate_limiter.apply_rate_limiting()

        # Assert
        mock_sleep.assert_not_called()

    def test_apply_rate_limiting_initialization_values(self):
        """Test that rate limiting attributes are properly initialized"""
        # Act
        self.rate_limiter.rate_limit = 5

        # Assert
        self.assertEqual(self.rate_limiter.rate_limit, 5)
        self.assertEqual(self.rate_limiter.request_timestamps, [])
        self.assertEqual(self.rate_limiter.waiting_requests_count, 0)

    @patch('time.time')
    @patch('time.sleep')
    @patch('random.uniform')
    def test_apply_rate_limiting_multiple_waiting_requests(self,mock_random, mock_sleep, mock_time):
        """Test behavior with multiple waiting requests"""
        # Arrange
        mock_time.side_effect = [100.0, 100.0, 100.1]
        mock_random.return_value = 0.9
        self.rate_limiter.rate_limit = 2

        # Set up scenario with multiple waiting requests
        self.rate_limiter.request_timestamps = [99.5, 99.8]
        self.rate_limiter.waiting_requests_count = 2  # Simulate multiple waiting requests

        # Act
        self.rate_limiter.apply_rate_limiting()

        # Assert
        mock_sleep.assert_called_once()
        self.assertEqual(self.rate_limiter.waiting_requests_count, 2)

    @patch('time.time')
    @patch('time.sleep')
    @patch('random.uniform')
    def test_apply_rate_limiting_waiting_requests_count_floor(self,mock_random, mock_sleep, mock_time):
        """Test that waiting_requests_count doesn't go below 0"""
        # Arrange
        mock_time.return_value = 100.0
        mock_random.return_value = 0.9
        self.rate_limiter.rate_limit = 5

        # Set up scenario where waiting_requests_count would go negative
        self.rate_limiter.request_timestamps = []
        self.rate_limiter.waiting_requests_count = -1  # Start with negative value

        # Act
        self.rate_limiter.apply_rate_limiting()

        # Assert
        self.assertEqual(self.rate_limiter.waiting_requests_count, 0)  # Should be reset to 0

    @patch('time.time')
    @patch('time.sleep')
    @patch('random.uniform')
    def test_apply_rate_limiting_waiting_requests_negative_sleep(self, mock_random, mock_sleep, mock_time):
        """Test behavior with multiple waiting requests"""
        # Arrange
        mock_time.side_effect = [100.0, 100.0, 100.1]
        mock_random.return_value = 0.01 # low random value for testing negative sleep
        self.rate_limiter.rate_limit = 2

        # Set up scenario with multiple waiting requests
        self.rate_limiter.request_timestamps = [99.1, 99.8]
        self.rate_limiter.waiting_requests_count = 0

        # Act
        self.rate_limiter.apply_rate_limiting()

        # Assert
        mock_sleep.assert_not_called()
        self.assertEqual(self.rate_limiter.waiting_requests_count, 0)

    def test_thread_safety_concurrent_access(self):
        """Test that RateLimiter is thread-safe with concurrent access"""
        # Arrange
        self.rate_limiter.rate_limit = 2
        num_threads = 5
        requests_per_thread = 2
        results = []
        
        def make_requests():
            """Function to be run by each thread"""
            thread_results = []
            for _ in range(requests_per_thread):
                start_time = time.time()
                self.rate_limiter.apply_rate_limiting()
                end_time = time.time()
                thread_results.append(end_time - start_time)
            results.extend(thread_results)
        
        # Act
        threads = []
        for _ in range(num_threads):
            thread = threading.Thread(target=make_requests)
            threads.append(thread)
            thread.start()
        
        for thread in threads:
            thread.join()
        
        # Assert
        self.assertEqual(len(results), num_threads * requests_per_thread)

        # Verify waiting count is non-negative
        self.assertGreaterEqual(self.rate_limiter.waiting_requests_count, 0)
        # Verify all timestamps are valid
        for timestamp in self.rate_limiter.request_timestamps:
            self.assertIsInstance(timestamp, float)
            self.assertGreater(timestamp, 0)

    def test_thread_safety_lock_acquisition(self):
        """Test that the lock is properly acquired and released"""
        # Arrange
        self.rate_limiter.rate_limit = 1
        lock_acquired_count = 0
        
        # Mock the lock to count acquisitions
        original_lock = self.rate_limiter._lock
        
        class CountingLock:
            def __init__(self, original_lock):
                self.original_lock = original_lock
                self.acquire_count = 0
            
            def __enter__(self):
                nonlocal lock_acquired_count
                lock_acquired_count += 1
                return self.original_lock.__enter__()
            
            def __exit__(self, *args):
                return self.original_lock.__exit__(*args)

        self.rate_limiter._lock = CountingLock(original_lock)
        
        def make_request():
            self.rate_limiter.apply_rate_limiting()
        
        # Act
        threads = []
        for _ in range(3):
            thread = threading.Thread(target=make_request)
            threads.append(thread)
            thread.start()
        
        for thread in threads:
            thread.join()
        
        # Assert
        self.assertEqual(lock_acquired_count, 3)  # Each thread should acquire lock once

    def test_thread_safety_no_race_conditions(self):
        """Test that no race conditions occur in timestamp list operations"""
        # Arrange
        self.rate_limiter.rate_limit = 50  # High limit to avoid rate limiting
        num_threads = 25
        
        def add_timestamp():
            """Function to add timestamp (simulates apply_rate_limiting)"""
            self.rate_limiter.apply_rate_limiting()
        
        # Act
        threads = []
        for _ in range(num_threads):
            thread = threading.Thread(target=add_timestamp)
            threads.append(thread)
            thread.start()
        
        for thread in threads:
            thread.join()
        
        # Assert
        # All timestamps should be added without corruption
        self.assertEqual(len(self.rate_limiter.request_timestamps), num_threads)
        
        # All timestamps should be valid floats
        for timestamp in self.rate_limiter.request_timestamps:
            self.assertIsInstance(timestamp, float)
            self.assertGreater(timestamp, 0)