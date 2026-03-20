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
Integration tests for DSPy compatibility
"""

import unittest
from unittest.mock import Mock, patch

from amzn_nova_prompt_optimizer.core.inference import (
    BedrockInferenceAdapter,
    SageMakerInferenceAdapter,
    DSPyBedrockAdapter,
    DSPySageMakerAdapter,
    create_dspy_adapter
)


# Simple RateLimitedLM implementation for testing
class RateLimitedLM:
    """Simple rate-limited LM wrapper for testing."""
    
    def __init__(self, model, rate_limit=2):
        self.wrapped_model = model
        self.rate_limit = rate_limit
    
    def __call__(self, *args, **kwargs):
        return self.wrapped_model(*args, **kwargs)
    
    def __getattr__(self, name):
        return getattr(self.wrapped_model, name)


class MockInferenceAdapter:
    """Mock inference adapter for testing without API calls."""
    
    def __init__(self, responses=None):
        self.region = "us-east-1"
        self.rate_limit = 100
        self.responses = responses or ["Mock response"]
        self.call_count = 0
        self.call_history = []
    
    def call_model(self, model_id, system_prompt, messages, inf_config):
        """Return mock response."""
        self.call_history.append({
            "model_id": model_id,
            "system_prompt": system_prompt,
            "messages": messages,
            "inf_config": inf_config
        })
        
        response = self.responses[self.call_count % len(self.responses)]
        self.call_count += 1
        return response
    
    def to_dspy_lm(self, model_id, **kwargs):
        """Create DSPy-compatible wrapper."""
        return DSPyBedrockAdapter(self, model_id, **kwargs)


class TestDSPyIntegration(unittest.TestCase):
    """Integration tests with DSPy."""
    
    def test_mock_adapter_basic(self):
        """Test basic usage with mock adapter."""
        mock = MockInferenceAdapter(responses=["Response 1", "Response 2"])
        
        dspy_lm = mock.to_dspy_lm("mock-model")
        
        # First call
        result1 = dspy_lm([{"role": "user", "content": "Test 1"}])
        self.assertEqual(result1, ["Response 1"])
        
        # Second call
        result2 = dspy_lm([{"role": "user", "content": "Test 2"}])
        self.assertEqual(result2, ["Response 2"])
        
        # Verify call history
        self.assertEqual(mock.call_count, 2)
        self.assertEqual(len(mock.call_history), 2)
    
    def test_with_rate_limited_lm(self):
        """Test integration with RateLimitedLM."""
        mock = MockInferenceAdapter(responses=["Response"])
        
        dspy_lm = mock.to_dspy_lm("mock-model")
        rate_limited = RateLimitedLM(dspy_lm, rate_limit=5)
        
        # Should work without errors
        messages = [{"role": "user", "content": "Test"}]
        result = rate_limited(messages)
        
        self.assertEqual(result, ["Response"])
        self.assertEqual(mock.call_count, 1)
    
    def test_conversation_history(self):
        """Test with conversation history."""
        mock = MockInferenceAdapter()
        dspy_lm = mock.to_dspy_lm("mock-model")
        
        messages = [
            {"role": "system", "content": "Be helpful"},
            {"role": "user", "content": "Hello"},
            {"role": "assistant", "content": "Hi"},
            {"role": "user", "content": "How are you?"}
        ]
        
        result = dspy_lm(messages)
        
        self.assertEqual(result, ["Mock response"])
        
        # Verify the adapter received correct format
        call = mock.call_history[0]
        self.assertEqual(call["system_prompt"], "Be helpful")
        self.assertEqual(len(call["messages"]), 3)
    
    def test_parameter_passing(self):
        """Test parameter passing through DSPy interface."""
        mock = MockInferenceAdapter()
        dspy_lm = mock.to_dspy_lm("mock-model")
        
        messages = [{"role": "user", "content": "Test"}]
        result = dspy_lm(
            messages,
            temperature=0.7,
            max_tokens=1000,
            top_p=0.9,
            top_k=50
        )
        
        self.assertEqual(result, ["Mock response"])
        
        # Verify parameters were passed and transformed by DSPyBedrockAdapter
        call = mock.call_history[0]
        config = call["inf_config"]
        # DSPyBedrockAdapter transforms max_tokens -> maxTokens
        from amzn_nova_prompt_optimizer.core.inference import (
            MAX_TOKENS_FIELD, TEMPERATURE_FIELD, TOP_P_FIELD, TOP_K_FIELD
        )
        self.assertEqual(config.get(TEMPERATURE_FIELD), 0.7)
        self.assertEqual(config.get(MAX_TOKENS_FIELD), 1000)
        self.assertEqual(config.get(TOP_P_FIELD), 0.9)
        self.assertEqual(config.get(TOP_K_FIELD), 50)
    
    def test_history_tracking(self):
        """Test that DSPy adapter tracks history."""
        mock = MockInferenceAdapter()
        dspy_lm = mock.to_dspy_lm("mock-model")
        
        # Make multiple calls
        dspy_lm([{"role": "user", "content": "Test 1"}])
        dspy_lm([{"role": "user", "content": "Test 2"}])
        dspy_lm([{"role": "user", "content": "Test 3"}])
        
        # Verify history
        self.assertEqual(len(dspy_lm.history), 3)
        self.assertEqual(dspy_lm.history[0]["response"], "Mock response")
    
    def test_copy_method(self):
        """Test copy method creates independent instance."""
        mock = MockInferenceAdapter()
        dspy_lm1 = mock.to_dspy_lm("model-1")
        dspy_lm2 = dspy_lm1.copy(model_id="model-2")
        
        # Should be different instances
        self.assertIsNot(dspy_lm1, dspy_lm2)
        
        # Should have different model IDs
        self.assertEqual(dspy_lm1.model_id, "model-1")
        self.assertEqual(dspy_lm2.model_id, "model-2")
        
        # Should share same underlying adapter
        self.assertIs(dspy_lm1.inference_adapter, dspy_lm2.inference_adapter)


class TestFactoryFunction(unittest.TestCase):
    """Test the factory function with different adapters."""
    
    def test_factory_with_mock(self):
        """Test factory function with mock adapter."""
        mock = MockInferenceAdapter()
        dspy_lm = create_dspy_adapter(mock, "test-model")
        
        self.assertIsInstance(dspy_lm, DSPyBedrockAdapter)
        self.assertEqual(dspy_lm.model_id, "test-model")
    
    @patch('boto3.Session')
    def test_factory_with_bedrock(self, mock_session):
        """Test factory function with Bedrock adapter."""
        mock_runtime = Mock()
        mock_session.return_value.client.return_value = mock_runtime
        
        bedrock_adapter = BedrockInferenceAdapter(region_name="us-east-1")
        dspy_lm = create_dspy_adapter(bedrock_adapter, "us.amazon.nova-pro-v1:0")
        
        self.assertIsInstance(dspy_lm, DSPyBedrockAdapter)
        self.assertEqual(dspy_lm.model_id, "us.amazon.nova-pro-v1:0")
    
    @patch('boto3.Session')
    def test_factory_with_sagemaker(self, mock_session):
        """Test factory function with SageMaker adapter."""
        mock_runtime = Mock()
        mock_session.return_value.client.return_value = mock_runtime
        
        sagemaker_adapter = SageMakerInferenceAdapter(
            endpoint_name="test-endpoint"
        )
        dspy_lm = create_dspy_adapter(sagemaker_adapter, "llama-3-70b")
        
        self.assertIsInstance(dspy_lm, DSPySageMakerAdapter)
        self.assertEqual(dspy_lm.model_id, "llama-3-70b")


class TestEndToEnd(unittest.TestCase):
    """End-to-end integration tests."""
    
    def test_complete_workflow(self):
        """Test complete workflow from adapter creation to inference."""
        # Create mock adapter
        mock = MockInferenceAdapter(responses=[
            "Response 1",
            "Response 2",
            "Response 3"
        ])
        
        # Create DSPy-compatible wrapper
        dspy_lm = mock.to_dspy_lm("test-model")
        
        # Wrap with rate limiting
        rate_limited_lm = RateLimitedLM(dspy_lm, rate_limit=10)
        
        # Make calls
        results = []
        for i in range(3):
            messages = [
                {"role": "system", "content": "Be helpful"},
                {"role": "user", "content": f"Question {i+1}"}
            ]
            result = rate_limited_lm(messages, temperature=0.0)
            results.append(result[0])
        
        # Verify results
        self.assertEqual(results, ["Response 1", "Response 2", "Response 3"])
        self.assertEqual(mock.call_count, 3)
        
        # Verify all calls had correct format
        for call in mock.call_history:
            self.assertEqual(call["system_prompt"], "Be helpful")
            self.assertEqual(len(call["messages"]), 1)
            self.assertIn("user", call["messages"][0])
    
    def test_switching_backends(self):
        """Test switching between different backends."""
        # Create different mock adapters with proper class names
        class BedrockInferenceAdapter(MockInferenceAdapter):
            pass
        
        class SageMakerInferenceAdapter(MockInferenceAdapter):
            pass
        
        bedrock_mock = BedrockInferenceAdapter(responses=["Bedrock response"])
        sagemaker_mock = SageMakerInferenceAdapter(responses=["SageMaker response"])
        
        # Create DSPy adapters
        bedrock_lm = create_dspy_adapter(bedrock_mock, "nova-model")
        sagemaker_lm = create_dspy_adapter(sagemaker_mock, "llama-model")
        
        # Verify correct adapter types
        self.assertIsInstance(bedrock_lm, DSPyBedrockAdapter)
        self.assertIsInstance(sagemaker_lm, DSPySageMakerAdapter)
        
        # Make calls
        messages = [{"role": "user", "content": "Test"}]
        
        bedrock_result = bedrock_lm(messages)
        sagemaker_result = sagemaker_lm(messages)
        
        # Verify different responses
        self.assertEqual(bedrock_result, ["Bedrock response"])
        self.assertEqual(sagemaker_result, ["SageMaker response"])


if __name__ == "__main__":
    unittest.main()
