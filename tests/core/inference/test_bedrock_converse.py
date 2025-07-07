import unittest

from amzn_nova_prompt_optimizer.core.inference import TOP_K_FIELD
from amzn_nova_prompt_optimizer.core.inference.inference_constants import \
    MAX_TOKENS_FIELD, TEMPERATURE_FIELD, TOP_P_FIELD
from amzn_nova_prompt_optimizer.core.inference.bedrock_converse import BedrockConverseHandler

from unittest.mock import Mock


class TestBedrockConverseHandler(unittest.TestCase):
    def setUp(self):
        self.mock_client = Mock()
        self.handler = BedrockConverseHandler(self.mock_client)
        self.mock_client.converse.return_value = {
            "output": {"message": {"content": [{"text": "model response"}]}}
        }

        # Common test data
        self.model_id = "us.amazon.nova-lite-v1:0"
        self.user_input = [{"user": "user input"}]
        self.inference_config = {
            MAX_TOKENS_FIELD: 100,
            TEMPERATURE_FIELD: 0.7,
            TOP_P_FIELD: 0.9,
            TOP_K_FIELD: 1
        }

    def test_call_model_with_system_prompt(self):
        """Test call_model method with a system prompt"""
        # Arrange
        system_prompt = "system prompt"

        # Act
        response = self.handler.call_model(
            self.model_id,
            system_prompt,
            self.user_input,
            self.inference_config
        )

        # Assert
        self.mock_client.converse.assert_called_once_with(
            modelId=self.model_id,
            messages=[{"role": "user", "content": [{"text": "user input"}]}],
            system=[{"text": system_prompt}],
            inferenceConfig={
                "maxTokens": 100,
                "temperature": 0.7,
                "topP": 0.9
            },
            additionalModelRequestFields={
                "inferenceConfig": {
                    "topK": self.inference_config.get(TOP_K_FIELD)
                }
            }
        )
        self.assertEqual(response, "model response")

    def test_call_model_with_system_prompt_anthropic(self):
        """Test call_model method with a system prompt for anthropic model"""
        # Arrange
        system_prompt = "system prompt"
        anthropic_model_id = "us.anthropic.claude-3-7-sonnet-20250219-v1:0"

        # Act
        response = self.handler.call_model(
            anthropic_model_id,
            system_prompt,
            self.user_input,
            self.inference_config
        )

        # Assert
        self.mock_client.converse.assert_called_once_with(
            modelId=anthropic_model_id,
            messages=[{"role": "user", "content": [{"text": "user input"}]}],
            system=[{"text": system_prompt}],
            inferenceConfig={
                "maxTokens": 100,
                "temperature": 0.7,
                "topP": 0.9
            },
            additionalModelRequestFields={
                "top_k": self.inference_config.get(TOP_K_FIELD)
            }
        )
        self.assertEqual(response, "model response")

    def test_call_model_without_system_prompt(self):
        """Test call_model method without a system prompt"""
        # Arrange
        system_prompt = ""

        # Act
        response = self.handler.call_model(
            self.model_id,
            system_prompt,
            self.user_input,
            self.inference_config
        )

        # Assert
        self.mock_client.converse.assert_called_once_with(
            modelId=self.model_id,
            messages=[{"role": "user", "content": [{"text": "user input"}]}],
            inferenceConfig={
                "maxTokens": 100,
                "temperature": 0.7,
                "topP": 0.9
            },
            additionalModelRequestFields={
                "inferenceConfig": {
                    "topK": self.inference_config.get(TOP_K_FIELD)
                }
            }
        )
        self.assertEqual(response, "model response")

    def test_call_model_without_system_prompt_anthropic(self):
        """Test call_model method without a system prompt for anthropic model"""
        # Arrange
        system_prompt = ""
        anthropic_model_id = "us.anthropic.claude-3-7-sonnet-20250219-v1:0"

        # Act
        response = self.handler.call_model(
            anthropic_model_id,
            system_prompt,
            self.user_input,
            self.inference_config
        )

        # Assert
        self.mock_client.converse.assert_called_once_with(
            modelId=anthropic_model_id,
            messages=[{"role": "user", "content": [{"text": "user input"}]}],
            inferenceConfig={
                "maxTokens": 100,
                "temperature": 0.7,
                "topP": 0.9
            },
            additionalModelRequestFields={
                "top_k": self.inference_config.get(TOP_K_FIELD)
            }
        )
        self.assertEqual(response, "model response")

    def test_get_inference_config(self):
        """Test _get_inference_config static method"""
        # Act
        result = BedrockConverseHandler._get_inference_config(self.inference_config)

        # Assert
        expected = {
            "maxTokens": 100,
            "temperature": 0.7,
            "topP": 0.9
        }
        self.assertEqual(result, expected)

    def test_get_additional_model_request_fields(self):
        """Test _get_additional_model_request_fields static method"""
        # Act
        result = BedrockConverseHandler._get_additional_model_request_fields(self.inference_config, self.model_id)

        # Assert
        expected = {
            "inferenceConfig": {
                "topK": self.inference_config.get(TOP_K_FIELD)
            }
        }
        self.assertEqual(result, expected)

    def test_get_additional_model_request_fields_anthropic(self):
        """Test _get_additional_model_request_fields static method with anthropic model"""
        # Arrange
        anthropic_model_id = "us.anthropic.claude-3-7-sonnet-20250219-v1:0"

        # Act
        result = BedrockConverseHandler._get_additional_model_request_fields(self.inference_config, anthropic_model_id)

        # Assert
        expected = {
            "top_k": self.inference_config.get(TOP_K_FIELD)
        }
        self.assertEqual(result, expected)

    def test_get_additional_model_request_fields_unsupported_model(self):
        """Test _get_additional_model_request_fields static method with unsupported model"""
        # Arrange
        unsupported_model_id = "unsupported-model"

        # Act
        result = BedrockConverseHandler._get_additional_model_request_fields(self.inference_config, unsupported_model_id)

        # Assert
        self.assertEqual(result, {})

    def test_get_messages(self):
        """Test _get_messages static method"""
        # Arrange
        user_input = [{"user": "user prompt"}, {"assistant":"assistant message"}, {"user": "user message"}]

        # Act
        result = BedrockConverseHandler._get_messages(user_input)

        # Assert
        expected = [{"role": "user", "content": [{"text": "user prompt"}]},
                    {"role": "assistant", "content": [{"text": "assistant message"}]},
                    {"role": "user", "content": [{"text": "user message"}]}]
        self.assertEqual(result, expected)

    def test_get_system_config_with_prompt(self):
        """Test _get_system_config static method with prompt"""
        # Arrange
        system_prompt = "test prompt"

        # Act
        result = BedrockConverseHandler._get_system_config(system_prompt)

        # Assert
        expected = [{"text": "test prompt"}]
        self.assertEqual(result, expected)

    def test_get_system_config_without_prompt(self):
        """Test _get_system_config static method without prompt"""
        # Arrange
        system_prompt = ""

        # Act
        result = BedrockConverseHandler._get_system_config(system_prompt)

        # Assert
        self.assertIsNone(result)
