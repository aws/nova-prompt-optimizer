# Copyright 2025 Amazon Inc

# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
Tests for SageMaker Inference Adapter
"""

import json
import unittest
from unittest.mock import Mock, MagicMock, patch

from botocore.exceptions import ClientError

from amzn_nova_prompt_optimizer.core.inference import SageMakerInferenceAdapter


class TestSageMakerInferenceAdapter(unittest.TestCase):
    """Test SageMaker inference adapter."""
    
    @patch('boto3.Session')
    def setUp(self, mock_session):
        """Set up test fixtures."""
        self.mock_runtime = Mock()
        mock_session.return_value.client.return_value = self.mock_runtime
        
        self.adapter = SageMakerInferenceAdapter(
            endpoint_name="test-endpoint",
            region_name="us-east-1",
            rate_limit=5
        )
    
    def test_initialization(self):
        """Test adapter initialization."""
        self.assertEqual(self.adapter.endpoint_name, "test-endpoint")
        self.assertEqual(self.adapter.region, "us-east-1")
        self.assertEqual(self.adapter.rate_limit, 5)
        self.assertEqual(self.adapter.max_retries, 5)
        self.assertEqual(self.adapter.content_type, "application/json")
    
    def test_payload_formatting(self):
        """Test payload formatting for SageMaker."""
        system_prompt = "You are helpful"
        messages = [
            {"user": "Hello"},
            {"assistant": "Hi"},
            {"user": "How are you?"}
        ]
        inf_config = {
            "max_new_tokens": 1000,
            "temperature": 0.7,
            "top_p": 0.9,
            "top_k": 50
        }
        
        payload = self.adapter._format_payload(
            system_prompt, messages, inf_config
        )
        
        # Check OpenAI-compatible format
        self.assertIn("messages", payload)
        self.assertIn("max_tokens", payload)
        self.assertIn("temperature", payload)
        self.assertIn("top_p", payload)
        self.assertIn("top_k", payload)
        
        # Check parameter values (max_tokens instead of max_new_tokens)
        self.assertEqual(payload["max_tokens"], 1000)
        self.assertEqual(payload["temperature"], 0.7)
        self.assertEqual(payload["top_p"], 0.9)
        self.assertEqual(payload["top_k"], 50)
        
        # Check message structure
        self.assertEqual(len(payload["messages"]), 4)
        self.assertEqual(payload["messages"][0]["role"], "system")
        self.assertEqual(payload["messages"][0]["content"], "You are helpful")
        self.assertEqual(payload["messages"][1]["role"], "user")
        self.assertEqual(payload["messages"][1]["content"], "Hello")
        self.assertEqual(payload["messages"][2]["role"], "assistant")
        self.assertEqual(payload["messages"][2]["content"], "Hi")
        self.assertEqual(payload["messages"][3]["role"], "user")
        self.assertEqual(payload["messages"][3]["content"], "How are you?")
    
    def test_payload_formatting_no_system_prompt(self):
        """Test payload formatting without system prompt."""
        messages = [{"user": "Hello"}]
        inf_config = {"max_new_tokens": 100}
        
        payload = self.adapter._format_payload("", messages, inf_config)
        
        # Check OpenAI-compatible format without system prompt
        self.assertIn("messages", payload)
        self.assertEqual(len(payload["messages"]), 1)
        self.assertEqual(payload["messages"][0]["role"], "user")
        self.assertEqual(payload["messages"][0]["content"], "Hello")
    
    def test_response_extraction_list_format(self):
        """Test extracting text from list response format."""
        response = [{"generated_text": "Test response"}]
        
        text = self.adapter._extract_text_from_response(response)
        
        self.assertEqual(text, "Test response")
    
    def test_response_extraction_dict_format(self):
        """Test extracting text from dict response format."""
        response = {"generated_text": "Test response"}
        
        text = self.adapter._extract_text_from_response(response)
        
        self.assertEqual(text, "Test response")
    
    def test_response_extraction_outputs_format(self):
        """Test extracting text from outputs format."""
        response = {"outputs": "Test response"}
        
        text = self.adapter._extract_text_from_response(response)
        
        self.assertEqual(text, "Test response")
    
    def test_response_extraction_string_format(self):
        """Test extracting text from string format."""
        response = "Test response"
        
        text = self.adapter._extract_text_from_response(response)
        
        self.assertEqual(text, "Test response")
    
    def test_response_extraction_unknown_format(self):
        """Test extracting text from unknown format."""
        response = {"unknown_field": "value"}
        
        with self.assertLogs('amzn_nova_prompt_optimizer.core.inference.sagemaker_adapter', level='WARNING') as log:
            text = self.adapter._extract_text_from_response(response)
        
        # Should return JSON string
        self.assertIn("unknown_field", text)
        self.assertTrue(any("Unknown SageMaker response format" in message for message in log.output))
    
    @patch('time.sleep')
    def test_successful_call(self, mock_sleep):
        """Test successful model call."""
        # Mock successful response
        self.mock_runtime.invoke_endpoint.return_value = {
            "Body": Mock(
                read=Mock(
                    return_value=b'{"generated_text": "Success"}'
                )
            )
        }
        
        result = self.adapter.call_model(
            model_id="test",
            system_prompt="Test",
            messages=[{"user": "Test"}],
            inf_config={"max_new_tokens": 100}
        )
        
        self.assertEqual(result, "Success")
        self.mock_runtime.invoke_endpoint.assert_called_once()
        mock_sleep.assert_not_called()
    
    @patch('time.sleep')
    def test_retry_on_throttling(self, mock_sleep):
        """Test retry logic on throttling."""
        # Mock throttling error then success
        self.mock_runtime.invoke_endpoint.side_effect = [
            ClientError(
                {"Error": {"Code": "ThrottlingException"}},
                "invoke_endpoint"
            ),
            {
                "Body": Mock(
                    read=Mock(
                        return_value=b'{"generated_text": "Success"}'
                    )
                )
            }
        ]
        
        result = self.adapter.call_model(
            model_id="test",
            system_prompt="Test",
            messages=[{"user": "Test"}],
            inf_config={"max_new_tokens": 100}
        )
        
        # Should have retried
        self.assertEqual(self.mock_runtime.invoke_endpoint.call_count, 2)
        self.assertEqual(result, "Success")
        mock_sleep.assert_called_once()
    
    @patch('time.sleep')
    def test_retry_on_model_error(self, mock_sleep):
        """Test retry logic on model error."""
        # Mock model error then success
        self.mock_runtime.invoke_endpoint.side_effect = [
            ClientError(
                {"Error": {"Code": "ModelError"}},
                "invoke_endpoint"
            ),
            {
                "Body": Mock(
                    read=Mock(
                        return_value=b'{"generated_text": "Success"}'
                    )
                )
            }
        ]
        
        result = self.adapter.call_model(
            model_id="test",
            system_prompt="Test",
            messages=[{"user": "Test"}],
            inf_config={"max_new_tokens": 100}
        )
        
        self.assertEqual(self.mock_runtime.invoke_endpoint.call_count, 2)
        self.assertEqual(result, "Success")
    
    @patch('time.sleep')
    def test_max_retries_exceeded(self, mock_sleep):
        """Test max retries exceeded."""
        # Mock continuous throttling
        self.mock_runtime.invoke_endpoint.side_effect = ClientError(
            {"Error": {"Code": "ThrottlingException"}},
            "invoke_endpoint"
        )
        
        with self.assertRaises(Exception) as context:
            self.adapter.call_model(
                model_id="test",
                system_prompt="Test",
                messages=[{"user": "Test"}],
                inf_config={"max_new_tokens": 100}
            )
        
        self.assertIn("Max retries", str(context.exception))
        self.assertEqual(self.mock_runtime.invoke_endpoint.call_count, 5)
    
    @patch('time.sleep')
    def test_non_retryable_error(self, mock_sleep):
        """Test non-retryable error is raised immediately."""
        # Mock non-retryable error
        self.mock_runtime.invoke_endpoint.side_effect = ClientError(
            {"Error": {"Code": "ValidationException"}},
            "invoke_endpoint"
        )
        
        with self.assertRaises(ClientError):
            self.adapter.call_model(
                model_id="test",
                system_prompt="Test",
                messages=[{"user": "Test"}],
                inf_config={"max_new_tokens": 100}
            )
        
        # Should not retry
        self.assertEqual(self.mock_runtime.invoke_endpoint.call_count, 1)
        mock_sleep.assert_not_called()
    
    def test_backoff_calculation(self):
        """Test exponential backoff calculation."""
        # Test backoff increases exponentially
        backoff_0 = self.adapter._calculate_backoff_time(0)
        backoff_1 = self.adapter._calculate_backoff_time(1)
        backoff_2 = self.adapter._calculate_backoff_time(2)
        
        # Should increase (with jitter, so approximate)
        self.assertGreater(backoff_1, backoff_0)
        self.assertGreater(backoff_2, backoff_1)
        
        # Check rough exponential growth
        self.assertGreater(backoff_2, 3.0)  # 1 * 2^2 = 4, minus jitter
    
    def test_to_dspy_lm(self):
        """Test creating DSPy-compatible wrapper uses endpoint_name."""
        dspy_lm = self.adapter.to_dspy_lm("test-model")
        
        from amzn_nova_prompt_optimizer.core.inference import DSPySageMakerAdapter
        self.assertIsInstance(dspy_lm, DSPySageMakerAdapter)
        # For SageMaker, model_id should be the endpoint_name, not the provided model_id
        self.assertEqual(dspy_lm.model_id, "test-endpoint")
    
    def test_to_dspy_lm_overrides_model_id_with_endpoint_name(self):
        """Test that to_dspy_lm overrides model_id with endpoint_name for SageMaker."""
        # The task_model_id passed should be ignored, endpoint_name should be used instead
        dspy_lm = self.adapter.to_dspy_lm("any-model-id-ignored")
        
        from amzn_nova_prompt_optimizer.core.inference import DSPySageMakerAdapter
        self.assertIsInstance(dspy_lm, DSPySageMakerAdapter)
        # Should use endpoint_name, not the provided model_id
        self.assertEqual(dspy_lm.model_id, "test-endpoint")
        self.assertNotEqual(dspy_lm.model_id, "any-model-id-ignored")


class TestSageMakerAdapterCustomization(unittest.TestCase):
    """Test customization of SageMaker adapter."""
    
    @patch('boto3.Session')
    def test_custom_content_type(self, mock_session):
        """Test custom content type."""
        mock_runtime = Mock()
        mock_session.return_value.client.return_value = mock_runtime
        
        adapter = SageMakerInferenceAdapter(
            endpoint_name="test-endpoint",
            content_type="text/plain",
            accept="text/plain"
        )
        
        self.assertEqual(adapter.content_type, "text/plain")
        self.assertEqual(adapter.accept, "text/plain")
    
    @patch('boto3.Session')
    def test_custom_retries(self, mock_session):
        """Test custom max retries."""
        mock_runtime = Mock()
        mock_session.return_value.client.return_value = mock_runtime
        
        adapter = SageMakerInferenceAdapter(
            endpoint_name="test-endpoint",
            max_retries=10
        )
        
        self.assertEqual(adapter.max_retries, 10)
    
    @patch('boto3.Session')
    def test_custom_rate_limit(self, mock_session):
        """Test custom rate limit."""
        mock_runtime = Mock()
        mock_session.return_value.client.return_value = mock_runtime
        
        adapter = SageMakerInferenceAdapter(
            endpoint_name="test-endpoint",
            rate_limit=20
        )
        
        self.assertEqual(adapter.rate_limit, 20)


if __name__ == "__main__":
    unittest.main()
