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
Tests for DSPy-Compatible Inference Adapters
"""

import unittest
from unittest.mock import Mock, MagicMock

from amzn_nova_prompt_optimizer.core.inference import (
    DSPyCompatibleInferenceAdapter,
    DSPyBedrockAdapter,
    DSPySageMakerAdapter,
    create_dspy_adapter,
    BedrockInferenceAdapter,
    MAX_TOKENS_FIELD,
    TEMPERATURE_FIELD,
    TOP_P_FIELD,
    TOP_K_FIELD
)


class TestDSPyCompatibleInferenceAdapter(unittest.TestCase):
    """Test the base DSPy-compatible adapter."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.mock_inference_adapter = Mock()
        self.mock_inference_adapter.call_model.return_value = "Test response"
        self.mock_inference_adapter.rate_limit = 5
        
        self.adapter = DSPyBedrockAdapter(
            inference_adapter=self.mock_inference_adapter,
            model_id="test-model"
        )
    
    def test_initialization(self):
        """Test adapter initialization."""
        self.assertEqual(self.adapter.model_id, "test-model")
        self.assertEqual(self.adapter.model, "test-model")
        self.assertFalse(self.adapter.cache)
        self.assertEqual(self.adapter.history, [])
        
        # Verify default kwargs are set (required by DSPy MIPROv2)
        self.assertIn('temperature', self.adapter.kwargs)
        self.assertIn('max_tokens', self.adapter.kwargs)
        self.assertIn('top_p', self.adapter.kwargs)
        self.assertEqual(self.adapter.kwargs['temperature'], 1.0)
        self.assertEqual(self.adapter.kwargs['max_tokens'], 1000)
        self.assertEqual(self.adapter.kwargs['top_p'], 1.0)
    
    def test_message_conversion_simple(self):
        """Test simple DSPy message format conversion."""
        dspy_messages = [
            {"role": "system", "content": "You are helpful"},
            {"role": "user", "content": "Hello"}
        ]
        
        system_prompt, messages = self.adapter._convert_messages_to_adapter_format(
            dspy_messages
        )
        
        self.assertEqual(system_prompt, "You are helpful")
        self.assertEqual(len(messages), 1)
        self.assertEqual(messages[0], {"user": "Hello"})
    
    def test_message_conversion_conversation(self):
        """Test conversation DSPy message format conversion."""
        dspy_messages = [
            {"role": "system", "content": "You are helpful"},
            {"role": "user", "content": "Hello"},
            {"role": "assistant", "content": "Hi"},
            {"role": "user", "content": "How are you?"}
        ]
        
        system_prompt, messages = self.adapter._convert_messages_to_adapter_format(
            dspy_messages
        )
        
        self.assertEqual(system_prompt, "You are helpful")
        self.assertEqual(len(messages), 3)
        self.assertEqual(messages[0], {"user": "Hello"})
        self.assertEqual(messages[1], {"assistant": "Hi"})
        self.assertEqual(messages[2], {"user": "How are you?"})
    
    def test_multiple_system_prompts(self):
        """Test handling multiple system prompts."""
        dspy_messages = [
            {"role": "system", "content": "First instruction"},
            {"role": "system", "content": "Second instruction"},
            {"role": "user", "content": "Hello"}
        ]
        
        system_prompt, messages = self.adapter._convert_messages_to_adapter_format(
            dspy_messages
        )
        
        self.assertEqual(system_prompt, "First instruction\n\nSecond instruction")
        self.assertEqual(len(messages), 1)
    
    def test_empty_system_prompt(self):
        """Test handling no system prompt."""
        dspy_messages = [
            {"role": "user", "content": "Hello"}
        ]
        
        system_prompt, messages = self.adapter._convert_messages_to_adapter_format(
            dspy_messages
        )
        
        self.assertEqual(system_prompt, "")
        self.assertEqual(len(messages), 1)
    
    def test_call_method(self):
        """Test the __call__ method."""
        dspy_messages = [
            {"role": "system", "content": "Be helpful"},
            {"role": "user", "content": "Test question"}
        ]
        
        result = self.adapter(
            messages=dspy_messages,
            temperature=0.5,
            max_tokens=100
        )
        
        # Verify call_model was called
        self.mock_inference_adapter.call_model.assert_called_once()
        
        # Verify result format
        self.assertIsInstance(result, list)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0], "Test response")
        
        # Verify history tracking
        self.assertEqual(len(self.adapter.history), 1)
        self.assertEqual(self.adapter.history[0]["response"], "Test response")
    
    def test_call_with_conversation(self):
        """Test calling with conversation history."""
        dspy_messages = [
            {"role": "system", "content": "Be helpful"},
            {"role": "user", "content": "Hello"},
            {"role": "assistant", "content": "Hi"},
            {"role": "user", "content": "How are you?"}
        ]
        
        result = self.adapter(messages=dspy_messages)
        
        # Verify call was made
        self.mock_inference_adapter.call_model.assert_called_once()
        
        # Verify arguments
        call_args = self.mock_inference_adapter.call_model.call_args
        self.assertEqual(call_args[1]["system_prompt"], "Be helpful")
        self.assertEqual(len(call_args[1]["messages"]), 3)
    
    def test_copy_method(self):
        """Test the copy method."""
        new_adapter = self.adapter.copy(model_id="new-model", cache=True)
        
        self.assertEqual(new_adapter.model_id, "new-model")
        self.assertTrue(new_adapter.cache)
        self.assertIsNot(new_adapter, self.adapter)
        # Verify it shares the same underlying adapter
        self.assertIs(new_adapter.inference_adapter, self.adapter.inference_adapter)
    
    def test_repr(self):
        """Test string representation."""
        repr_str = repr(self.adapter)
        self.assertIn("DSPyBedrockAdapter", repr_str)
        self.assertIn("test-model", repr_str)


class TestDSPyBedrockAdapter(unittest.TestCase):
    """Test Bedrock-specific DSPy adapter."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.mock_bedrock_adapter = Mock(spec=BedrockInferenceAdapter)
        self.mock_bedrock_adapter.call_model.return_value = "Bedrock response"
        self.mock_bedrock_adapter.rate_limit = 2
        
        self.adapter = DSPyBedrockAdapter(
            inference_adapter=self.mock_bedrock_adapter,
            model_id="us.amazon.nova-pro-v1:0"
        )
    
    def test_bedrock_config_format(self):
        """Test Bedrock-specific config format."""
        config = self.adapter._build_inference_config({
            "temperature": 1.0,
            "max_tokens": 5000,
            "top_p": 0.9,
            "top_k": 50
        })
        
        self.assertIn(MAX_TOKENS_FIELD, config)
        self.assertIn(TEMPERATURE_FIELD, config)
        self.assertIn(TOP_P_FIELD, config)
        self.assertIn(TOP_K_FIELD, config)
        self.assertEqual(config[MAX_TOKENS_FIELD], 5000)
        self.assertEqual(config[TEMPERATURE_FIELD], 1.0)
        self.assertEqual(config[TOP_P_FIELD], 0.9)
        self.assertEqual(config[TOP_K_FIELD], 50)
    
    def test_bedrock_config_defaults(self):
        """Test Bedrock config with default values from self.kwargs."""
        config = self.adapter._build_inference_config({})
        
        # Should use defaults from self.kwargs (set in __init__)
        self.assertEqual(config[MAX_TOKENS_FIELD], 1000)  # From self.kwargs
        self.assertEqual(config[TEMPERATURE_FIELD], 1.0)  # From self.kwargs
        self.assertEqual(config[TOP_P_FIELD], 1.0)  # From self.kwargs
        self.assertEqual(config[TOP_K_FIELD], 1)  # Hardcoded fallback
    
    def test_bedrock_config_uses_init_kwargs(self):
        """Test that config uses kwargs from initialization."""
        # Create adapter with custom kwargs at init
        adapter = DSPyBedrockAdapter(
            self.mock_bedrock_adapter,
            "us.amazon.nova-pro-v1:0",
            temperature=0.7,
            max_tokens=2000
        )
        
        # Call without any kwargs - should use init kwargs
        config = adapter._build_inference_config({})
        
        self.assertEqual(config[TEMPERATURE_FIELD], 0.7)
        self.assertEqual(config[MAX_TOKENS_FIELD], 2000)
        self.assertEqual(config[TOP_P_FIELD], 1.0)  # Default
    
    def test_bedrock_config_call_kwargs_override_init(self):
        """Test that call-time kwargs override init kwargs."""
        # Create adapter with custom kwargs at init
        adapter = DSPyBedrockAdapter(
            self.mock_bedrock_adapter,
            "us.amazon.nova-pro-v1:0",
            temperature=0.7,
            max_tokens=2000
        )
        
        # Call with different kwargs - should override
        config = adapter._build_inference_config({
            "temperature": 0.9,
            "top_p": 0.8
        })
        
        self.assertEqual(config[TEMPERATURE_FIELD], 0.9)  # Overridden
        self.assertEqual(config[MAX_TOKENS_FIELD], 2000)  # From init
        self.assertEqual(config[TOP_P_FIELD], 0.8)  # Overridden
    
    def test_bedrock_call(self):
        """Test calling Bedrock through DSPy interface."""
        messages = [
            {"role": "system", "content": "System prompt"},
            {"role": "user", "content": "User message"}
        ]
        
        result = self.adapter(messages, temperature=0.0, max_tokens=1000)
        
        # Verify call was made
        self.mock_bedrock_adapter.call_model.assert_called_once()
        
        # Verify arguments
        call_args = self.mock_bedrock_adapter.call_model.call_args
        self.assertEqual(call_args[1]["model_id"], "us.amazon.nova-pro-v1:0")
        self.assertEqual(call_args[1]["system_prompt"], "System prompt")
        
        # Verify result
        self.assertEqual(result, ["Bedrock response"])


class TestDSPySageMakerAdapter(unittest.TestCase):
    """Test SageMaker-specific DSPy adapter."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.mock_sagemaker_adapter = Mock()
        self.mock_sagemaker_adapter.call_model.return_value = "SageMaker response"
        self.mock_sagemaker_adapter.rate_limit = 10
        
        self.adapter = DSPySageMakerAdapter(
            inference_adapter=self.mock_sagemaker_adapter,
            model_id="llama-3-70b"
        )
    
    def test_sagemaker_config_format(self):
        """Test SageMaker-specific config format."""
        config = self.adapter._build_inference_config({
            "temperature": 0.8,
            "max_tokens": 3000,
            "top_p": 0.95,
            "top_k": 40
        })
        
        self.assertIn("max_new_tokens", config)
        self.assertIn("temperature", config)
        self.assertIn("do_sample", config)
        self.assertIn("return_full_text", config)
        self.assertEqual(config["max_new_tokens"], 3000)
        self.assertEqual(config["temperature"], 0.8)
        self.assertTrue(config["do_sample"])  # temperature > 0
    
    def test_sagemaker_do_sample_false(self):
        """Test do_sample is False when temperature is 0."""
        config = self.adapter._build_inference_config({"temperature": 0.0})
        self.assertFalse(config["do_sample"])
    
    def test_sagemaker_config_uses_init_kwargs(self):
        """Test that config uses kwargs from initialization."""
        # Create adapter with custom kwargs at init
        adapter = DSPySageMakerAdapter(
            self.mock_sagemaker_adapter,
            "llama-3-70b",
            temperature=0.7,
            max_tokens=2000
        )
        
        # Call without any kwargs - should use init kwargs
        config = adapter._build_inference_config({})
        
        self.assertEqual(config["temperature"], 0.7)
        self.assertEqual(config["max_new_tokens"], 2000)
        self.assertTrue(config["do_sample"])  # temperature > 0
    
    def test_sagemaker_config_call_kwargs_override_init(self):
        """Test that call-time kwargs override init kwargs."""
        # Create adapter with custom kwargs at init
        adapter = DSPySageMakerAdapter(
            self.mock_sagemaker_adapter,
            "llama-3-70b",
            temperature=0.7,
            max_tokens=2000
        )
        
        # Call with different kwargs - should override
        config = adapter._build_inference_config({
            "temperature": 0.0,
            "top_p": 0.8
        })
        
        self.assertEqual(config["temperature"], 0.0)  # Overridden
        self.assertEqual(config["max_new_tokens"], 2000)  # From init
        self.assertEqual(config["top_p"], 0.8)  # Overridden
        self.assertFalse(config["do_sample"])  # temperature is 0
    
    def test_sagemaker_do_sample_true(self):
        """Test do_sample is True when temperature > 0."""
        config = self.adapter._build_inference_config({"temperature": 0.5})
        self.assertTrue(config["do_sample"])
    
    def test_sagemaker_config_defaults(self):
        """Test SageMaker config with default values from self.kwargs."""
        config = self.adapter._build_inference_config({})
        
        # Should use defaults from self.kwargs (set in __init__)
        self.assertEqual(config["max_new_tokens"], 1000)  # From self.kwargs
        self.assertEqual(config["temperature"], 1.0)  # From self.kwargs
        self.assertTrue(config["do_sample"])  # temperature > 0
        self.assertFalse(config["return_full_text"])


class TestCreateDSPyAdapter(unittest.TestCase):
    """Test the factory function."""
    
    def test_bedrock_detection(self):
        """Test automatic detection of Bedrock adapter."""
        mock_adapter = Mock(spec=BedrockInferenceAdapter)
        mock_adapter.__class__.__name__ = "BedrockInferenceAdapter"
        
        result = create_dspy_adapter(mock_adapter, "test-model")
        
        self.assertIsInstance(result, DSPyBedrockAdapter)
        self.assertEqual(result.model_id, "test-model")
    
    def test_sagemaker_detection(self):
        """Test automatic detection of SageMaker adapter."""
        mock_adapter = Mock()
        mock_adapter.__class__.__name__ = "SageMakerInferenceAdapter"
        
        result = create_dspy_adapter(mock_adapter, "test-model")
        
        self.assertIsInstance(result, DSPySageMakerAdapter)
        self.assertEqual(result.model_id, "test-model")
    
    def test_unknown_adapter_fallback(self):
        """Test fallback for unknown adapter types."""
        mock_adapter = Mock()
        mock_adapter.__class__.__name__ = "UnknownAdapter"
        
        with self.assertLogs('amzn_nova_prompt_optimizer.core.inference.dspy_compatible', level='WARNING') as log:
            result = create_dspy_adapter(mock_adapter, "test-model")
        
        # Should fallback to Bedrock adapter
        self.assertIsInstance(result, DSPyBedrockAdapter)
        self.assertTrue(any("Unknown adapter type" in message for message in log.output))
    
    def test_factory_with_kwargs(self):
        """Test factory function with additional kwargs."""
        mock_adapter = Mock(spec=BedrockInferenceAdapter)
        mock_adapter.__class__.__name__ = "BedrockInferenceAdapter"
        
        result = create_dspy_adapter(
            mock_adapter, 
            "test-model",
            cache=True,
            custom_param="value"
        )
        
        self.assertTrue(result.cache)
        self.assertEqual(result.kwargs.get("custom_param"), "value")


class TestErrorHandling(unittest.TestCase):
    """Test error handling in DSPy adapters."""
    
    def test_call_model_error_propagation(self):
        """Test that errors from call_model are propagated."""
        mock_adapter = Mock()
        mock_adapter.call_model.side_effect = Exception("API Error")
        
        dspy_adapter = DSPyBedrockAdapter(mock_adapter, "test-model")
        
        with self.assertRaises(Exception) as context:
            dspy_adapter([{"role": "user", "content": "test"}])
        
        self.assertIn("API Error", str(context.exception))
    
    def test_unknown_role_warning(self):
        """Test warning for unknown message roles."""
        mock_adapter = Mock()
        mock_adapter.call_model.return_value = "response"
        
        dspy_adapter = DSPyBedrockAdapter(mock_adapter, "test-model")
        
        messages = [
            {"role": "unknown", "content": "test"}
        ]
        
        with self.assertLogs('amzn_nova_prompt_optimizer.core.inference.dspy_compatible', level='WARNING') as log:
            dspy_adapter._convert_messages_to_adapter_format(messages)
        
        self.assertTrue(any("Unknown message role" in message for message in log.output))


if __name__ == "__main__":
    unittest.main()
