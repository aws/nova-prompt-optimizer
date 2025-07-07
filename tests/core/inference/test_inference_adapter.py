import unittest
import time

from amzn_nova_prompt_optimizer.core.inference.adapter import BedrockInferenceAdapter
from amzn_nova_prompt_optimizer.core.inference.bedrock_converse import BedrockConverseHandler

from unittest.mock import Mock, patch
from botocore.config import Config
from botocore.exceptions import ProfileNotFound, ParamValidationError, ClientError


class TestBedrockInferenceAdapter(unittest.TestCase):
    def setUp(self):
        """Set up test fixtures"""
        # Common test data
        self.test_region = "us-west-2"
        self.test_access_key = "test_access_key"
        self.test_secret_key = "test_secret_key"
        self.test_session_token = "test_session_token"
        self.test_profile = "test_profile"
        self.test_max_retries = 5

        # Create patcher for boto3.Session
        self.session_patcher = patch('amzn_nova_prompt_optimizer.core.inference.adapter.boto3.Session')
        self.mock_session_class = self.session_patcher.start()

        # Setup mock session and client
        self.mock_session = Mock()
        self.mock_bedrock_client = Mock()
        self.mock_bedrock_client.converse.return_value = {
            "output": {"message": {"content": [{"text": "model response"}]}}
        }
        self.mock_session.client.return_value = self.mock_bedrock_client
        self.mock_session_class.return_value = self.mock_session

        # Mock BedrockConverseHandler
        self.mock_converse_handler = BedrockConverseHandler(self.mock_bedrock_client)

    def tearDown(self):
        self.session_patcher.stop()

    def test_init_with_profile(self):
        """Test initialization with AWS profile"""
        # Act
        adapter = BedrockInferenceAdapter(
            region_name=self.test_region,
            profile_name=self.test_profile
        )

        # Assert
        self.mock_session_class.assert_called_once_with(profile_name=self.test_profile)
        self.mock_session.client.assert_called_once()

    def test_init_with_default_credentials(self):
        """Test initialization with default credentials"""
        # Act
        adapter = BedrockInferenceAdapter(region_name=self.test_region)

        # Assert
        self.mock_session_class.assert_called_once_with()
        self.mock_session.client.assert_called_once()

    def test_call_model(self):
        """Test call_model method with successful response"""
        # Arrange
        adapter = BedrockInferenceAdapter(region_name=self.test_region)
        test_model_id = "test_model"
        test_system_prompt = "system prompt"
        test_message = [{"user": "user prompt"}]
        test_inf_config = {"maxTokens": 100}

        expected_response = "model response"
        self.mock_bedrock_client.invoke_model.return_value = {
            "body": expected_response
        }

        # Mock the converse_client's call_model method
        adapter.converse_client.call_model = Mock(return_value=expected_response)

        # Act
        response = adapter.call_model(
            test_model_id,
            test_system_prompt,
            test_message,
            test_inf_config
        )

        # Assert
        adapter.converse_client.call_model.assert_called_once_with(
            test_model_id,
            test_system_prompt,
            test_message,
            test_inf_config
        )
        self.assertEqual(response, expected_response)

    def test_profile_not_found(self):
        """Test handling of non-existent profile"""
        # Arrange
        self.mock_session_class.side_effect = ProfileNotFound(profile='test_profile')

        # Act/Assert
        with self.assertRaises(ProfileNotFound):
            BedrockInferenceAdapter(
                region_name=self.test_region,
                profile_name='test_profile'
            )

    @patch('time.time')
    @patch('time.sleep')
    def test_apply_rate_limiting_no_limit_reached(self, mock_sleep, mock_time):
        """Test rate limiting when limit is not reached"""
        # Arrange
        mock_time.return_value = 100.0
        adapter = BedrockInferenceAdapter(region_name=self.test_region, rate_limit=5)
        
        # Add some timestamps that are within rate limit
        adapter.request_timestamps = [99.5, 99.7, 99.9]  # 3 requests in last second
        
        # Act
        adapter._apply_rate_limiting()
        
        # Assert
        mock_sleep.assert_not_called()
        self.assertEqual(len(adapter.request_timestamps), 4)  # Original 3 + 1 new
        self.assertEqual(adapter.waiting_requests_count, 0)

    @patch('time.time')
    @patch('time.sleep')
    @patch('random.uniform')
    def test_apply_rate_limiting_limit_reached(self, mock_random, mock_sleep, mock_time):
        """Test rate limiting when limit is reached"""
        # Arrange
        mock_time.side_effect = [100.0, 100.0, 100.1]  # Current time calls
        mock_random.return_value = 0.9
        adapter = BedrockInferenceAdapter(region_name=self.test_region, rate_limit=3)
        
        # Fill up to rate limit
        adapter.request_timestamps = [99.5, 99.7, 99.9]  # 3 requests in last second
        
        # Act
        adapter._apply_rate_limiting()
        
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
        adapter = BedrockInferenceAdapter(region_name=self.test_region, rate_limit=5)
        
        # Add timestamps - some old (>1 second) and some recent
        adapter.request_timestamps = [98.5, 98.8, 99.2, 99.5, 99.8]  # Mix of old and recent
        
        # Act
        adapter._apply_rate_limiting()
        
        # Assert
        # Only timestamps from last second should remain (99.2, 99.5, 99.8) + new one
        self.assertEqual(len(adapter.request_timestamps), 4)
        for timestamp in adapter.request_timestamps[:-1]:  # Exclude the newly added one
            self.assertGreaterEqual(timestamp, 99.0)  # All should be within last second

    @patch('time.time')
    @patch('time.sleep')
    @patch('random.uniform')
    def test_apply_rate_limiting_sleep_calculation(self, mock_random, mock_sleep, mock_time):
        """Test sleep time calculation with predictable random value"""
        # Arrange
        mock_time.side_effect = [100.0, 100.0, 100.1]
        mock_random.return_value = 0.5  # Fixed random value for predictable testing
        adapter = BedrockInferenceAdapter(region_name=self.test_region, rate_limit=2)
        
        # Set up scenario where rate limit is reached
        adapter.request_timestamps = [99.5, 99.8]  # 2 requests, rate limit is 2
        adapter.waiting_requests_count = 0
        
        # Act
        adapter._apply_rate_limiting()
        
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
        adapter = BedrockInferenceAdapter(region_name=self.test_region, rate_limit=2)
        
        # Set up scenario where rate limit is reached
        adapter.request_timestamps = [99.5, 99.8]
        adapter.waiting_requests_count = 0
        
        # Act
        adapter._apply_rate_limiting()
        
        # Assert
        self.assertEqual(adapter.waiting_requests_count, 0)  # Should be decremented back to 0

    @patch('time.time')
    @patch('time.sleep')
    def test_apply_rate_limiting_negative_sleep_time(self, mock_sleep, mock_time):
        """Test that negative sleep times don't cause sleep"""
        # Arrange
        mock_time.side_effect = [100.0, 100.0, 100.1]
        adapter = BedrockInferenceAdapter(region_name=self.test_region, rate_limit=2)
        
        # Set up scenario where calculated sleep time would be negative
        adapter.request_timestamps = [98.0, 98.5]  # Old timestamps
        adapter.waiting_requests_count = 0
        
        # Act
        adapter._apply_rate_limiting()
        
        # Assert
        mock_sleep.assert_not_called()

    def test_apply_rate_limiting_initialization_values(self):
        """Test that rate limiting attributes are properly initialized"""
        # Act
        adapter = BedrockInferenceAdapter(region_name=self.test_region, rate_limit=5)
        
        # Assert
        self.assertEqual(adapter.rate_limit, 5)
        self.assertEqual(adapter.request_timestamps, [])
        self.assertEqual(adapter.waiting_requests_count, 0)

    def test_apply_rate_limiting_default_rate_limit(self):
        """Test default rate limit value"""
        # Act
        adapter = BedrockInferenceAdapter(region_name=self.test_region)
        
        # Assert
        self.assertEqual(adapter.rate_limit, 2)  # Default value

    @patch('time.time')
    @patch('time.sleep')
    @patch('random.uniform')
    def test_apply_rate_limiting_multiple_waiting_requests(self,mock_random, mock_sleep, mock_time):
        """Test behavior with multiple waiting requests"""
        # Arrange
        mock_time.side_effect = [100.0, 100.0, 100.1]
        mock_random.return_value = 0.9
        adapter = BedrockInferenceAdapter(region_name=self.test_region, rate_limit=2)

        # Set up scenario with multiple waiting requests
        adapter.request_timestamps = [99.5, 99.8]
        adapter.waiting_requests_count = 2  # Simulate multiple waiting requests

        # Act
        adapter._apply_rate_limiting()

        # Assert
        mock_sleep.assert_called_once()
        self.assertEqual(adapter.waiting_requests_count, 2)

    @patch('time.time')
    @patch('time.sleep')
    @patch('random.uniform')
    def test_apply_rate_limiting_waiting_requests_count_floor(self,mock_random, mock_sleep, mock_time):
        """Test that waiting_requests_count doesn't go below 0"""
        # Arrange
        mock_time.return_value = 100.0
        mock_random.return_value = 0.9
        adapter = BedrockInferenceAdapter(region_name=self.test_region, rate_limit=5)
        
        # Set up scenario where waiting_requests_count would go negative
        adapter.request_timestamps = []
        adapter.waiting_requests_count = -1  # Start with negative value
        
        # Act
        adapter._apply_rate_limiting()
        
        # Assert
        self.assertEqual(adapter.waiting_requests_count, 0)  # Should be reset to 0

    @patch('amzn_nova_prompt_optimizer.core.inference.adapter.BedrockInferenceAdapter._apply_rate_limiting')
    def test_call_model_applies_rate_limiting(self, mock_rate_limiting):
        """Test that call_model applies rate limiting"""
        # Arrange
        adapter = BedrockInferenceAdapter(region_name=self.test_region)
        
        test_model_id = "test_model"
        test_system_prompt = "system prompt"
        test_message = [{"user": "user prompt"}]
        test_inf_config = {"maxTokens": 100}
        
        # Act
        adapter.call_model(test_model_id, test_system_prompt, test_message, test_inf_config)
        
        # Assert
        mock_rate_limiting.assert_called_once()

    @patch('time.time')
    @patch('time.sleep')
    @patch('random.uniform')
    def test_apply_rate_limiting_waiting_requests_negative_sleep(self, mock_random, mock_sleep, mock_time):
        """Test behavior with multiple waiting requests"""
        # Arrange
        mock_time.side_effect = [100.0, 100.0, 100.1]
        mock_random.return_value = 0.01 # low random value for testing negative sleep
        adapter = BedrockInferenceAdapter(region_name=self.test_region, rate_limit=2)

        # Set up scenario with multiple waiting requests
        adapter.request_timestamps = [99.1, 99.8]
        adapter.waiting_requests_count = 0

        # Act
        adapter._apply_rate_limiting()

        # Assert
        mock_sleep.assert_not_called()
        self.assertEqual(adapter.waiting_requests_count, 0)

    def test_call_model_with_retries(self):
        """Test call_model retry behavior with throttling"""
        # Arrange
        adapter = BedrockInferenceAdapter(
            region_name=self.test_region,
            max_retries=3,
            initial_backoff=0.1
        )

        test_model_id = "test_model"
        test_system_prompt = "system prompt"
        test_message = [{"user": "user prompt"}]
        test_inf_config = {"maxTokens": 100}

        throttling_error = ClientError(
            error_response={'Error': {'Code': 'ThrottlingException'}},
            operation_name='InvokeModel'
        )

        # Mock to fail twice with throttling, then succeed
        adapter.converse_client.call_model = Mock(
            side_effect=[throttling_error, throttling_error, "success"]
        )

        # Act
        response = adapter._call_model_with_retry(
            test_model_id,
            test_system_prompt,
            test_message,
            test_inf_config
        )

        # Assert
        self.assertEqual(response, "success")
        self.assertEqual(adapter.converse_client.call_model.call_count, 3)

    def test_call_model_max_retries_exceeded(self):
        """Test call_model when max retries are exceeded"""
        # Arrange
        adapter = BedrockInferenceAdapter(
            region_name=self.test_region,
            max_retries=2,
            initial_backoff=0.1
        )

        throttling_error = ClientError(
            error_response={'Error': {'Code': 'ThrottlingException'}},
            operation_name='InvokeModel'
        )

        adapter.converse_client.call_model = Mock(side_effect=throttling_error)

        # Act & Assert
        with self.assertRaises(Exception) as context:
            adapter._call_model_with_retry(
                "test_model",
                "system prompt",
                [{"user": "user prompt"}],
                {"maxTokens": 100}
            )

        self.assertTrue("Max retries (2) exceeded" in str(context.exception))
        self.assertEqual(adapter.converse_client.call_model.call_count, 2)

    @patch('random.uniform', return_value=0.5)
    def test_backoff_calculation(self, mock_random):
        """Test exponential backoff calculation"""
        # Arrange
        adapter = BedrockInferenceAdapter(
            region_name=self.test_region,
            initial_backoff=1
        )

        # Act & Assert
        self.assertEqual(adapter._calculate_backoff_time(0), 1.5)  # 1 * (2^0) + 0.5
        self.assertEqual(adapter._calculate_backoff_time(1), 2.5)  # 1 * (2^1) + 0.5
        self.assertEqual(adapter._calculate_backoff_time(2), 4.5)  # 1 * (2^2) + 0.5
