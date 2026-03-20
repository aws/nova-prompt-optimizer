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
        """Test _get_messages instance method with text-only input"""
        # Arrange
        user_input = [{"user": "user prompt"}, {"assistant": "assistant message"}, {"user": "user message"}]

        # Act
        result = self.handler._get_messages(user_input)

        # Assert
        expected = [{"role": "user", "content": [{"text": "user prompt"}]},
                    {"role": "assistant", "content": [{"text": "assistant message"}]},
                    {"role": "user", "content": [{"text": "user message"}]}]
        self.assertEqual(result, expected)

    def test_enable_image_support_default_false(self):
        """Test that image support is disabled by default"""
        handler = BedrockConverseHandler(self.mock_client)
        self.assertFalse(handler.enable_image_support)

    def test_enable_image_support_opt_in(self):
        """Test that image support can be explicitly enabled"""
        from amzn_nova_prompt_optimizer.core.inference.bedrock_converse import IMAGE_SUPPORT_AVAILABLE
        handler = BedrockConverseHandler(self.mock_client, enable_image_support=True)
        # Only True if PIL/requests are installed
        self.assertEqual(handler.enable_image_support, IMAGE_SUPPORT_AVAILABLE)

    def test_get_messages_text_only_when_image_support_disabled(self):
        """Test that image paths are treated as plain text when image support is off"""
        handler = BedrockConverseHandler(self.mock_client, enable_image_support=False)
        user_input = [{"user": "Analyze this image for watermarks: /some/image.jpg"}]
        result = handler._get_messages(user_input)
        # Should be plain text, not an image block
        self.assertEqual(result[0]["content"], [{"text": "Analyze this image for watermarks: /some/image.jpg"}])

    def test_process_multimodal_content_template_variable_in_sentence(self):
        """Test that template variables embedded in sentences are not treated as image paths"""
        from amzn_nova_prompt_optimizer.core.inference.bedrock_converse import BedrockConverseHandler
        result = BedrockConverseHandler._process_multimodal_content(
            "Analyze this image for watermarks: {input}"
        )
        self.assertEqual(result, [{"text": "Analyze this image for watermarks: {input}"}])

    def test_process_multimodal_content_template_variable_double_braces(self):
        """Test that {{input}} template variables are not treated as image paths"""
        result = BedrockConverseHandler._process_multimodal_content(
            "Analyze this image for watermarks: {{input}}"
        )
        self.assertEqual(result, [{"text": "Analyze this image for watermarks: {{input}}"}])

    def test_process_multimodal_content_dspy_template(self):
        """Test that DSPy [[ ## ]] format is not treated as image path"""
        result = BedrockConverseHandler._process_multimodal_content(
            "[[ ## input ## ]]"
        )
        self.assertEqual(result, [{"text": "[[ ## input ## ]]"}])

    def test_process_multimodal_content_plain_text(self):
        """Test that plain text with no image indicators is returned as-is"""
        result = BedrockConverseHandler._process_multimodal_content(
            "What is machine learning?"
        )
        self.assertEqual(result, [{"text": "What is machine learning?"}])

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


    # --- _build_content_blocks tests ---

    def test_build_content_blocks_plain_string(self):
        """Plain string returns a single text block"""
        result = self.handler._build_content_blocks("hello world")
        self.assertEqual(result, [{"text": "hello world"}])

    def test_build_content_blocks_bytes_image_support_disabled(self):
        """bytes with image support off returns a text placeholder"""
        handler = BedrockConverseHandler(self.mock_client, enable_image_support=False)
        result = handler._build_content_blocks(b"\x89PNG\r\n")
        self.assertEqual(result, [{"text": "[image]"}])

    def test_build_content_blocks_dict_with_text_only(self):
        """dict with only 'text' key returns a text block"""
        result = self.handler._build_content_blocks({"text": "describe this"})
        self.assertEqual(result, [{"text": "describe this"}])

    def test_build_content_blocks_dict_with_image_bytes_support_disabled(self):
        """dict with image_bytes but image support off returns only text block"""
        handler = BedrockConverseHandler(self.mock_client, enable_image_support=False)
        result = handler._build_content_blocks({"text": "describe", "image_bytes": b"data"})
        self.assertEqual(result, [{"text": "describe"}])

    def test_get_messages_with_bytes_image_support_disabled(self):
        """bytes in user message with image support off produces text placeholder"""
        handler = BedrockConverseHandler(self.mock_client, enable_image_support=False)
        result = handler._get_messages([{"user": b"\x89PNG\r\n"}])
        self.assertEqual(result[0]["content"], [{"text": "[image]"}])

    def test_get_messages_with_structured_dict_text_only(self):
        """dict message with only text key produces text block"""
        result = self.handler._get_messages([{"user": {"text": "hello"}}])
        self.assertEqual(result[0]["content"], [{"text": "hello"}])
