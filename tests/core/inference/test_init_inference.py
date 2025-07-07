import unittest

from amzn_nova_prompt_optimizer.core.inference import InferenceRunner, INFERENCE_OUTPUT_FIELD

from unittest.mock import Mock, patch


class TestInferenceRunner(unittest.TestCase):
    def setUp(self):
        self.mock_prompt_adapter = Mock()
        self.mock_dataset_adapter = Mock()
        self.mock_inference_adapter = Mock()

        self.runner = InferenceRunner(
            self.mock_prompt_adapter,
            self.mock_dataset_adapter,
            self.mock_inference_adapter
        )

        # Default test parameters
        self.model_id = "test-model"
        self.test_inputs = {"var1": "value1", "var2": "value2"}
        self.test_row = {"inputs": self.test_inputs}

    def test_format_template_basic(self):
        """Test basic template formatting"""
        template = "Test with {var1} and {var2}"
        variables = ["var1", "var2"]

        result = self.runner._format_template(template, variables, self.test_inputs)
        expected = "Test with value1 and value2"
        self.assertEqual(result, expected)

    def test_format_template_unused_variables(self):
        """Test template formatting with unused variables"""
        template = "Test with {var1}"
        variables = ["var1", "var2"]

        result = self.runner._format_template(template, variables, self.test_inputs)
        self.assertIn("value1", result)
        self.assertIn("[[ ## var2 ## ]]", result)
        self.assertIn("value2", result)

    def test_create_messages_basic(self):
        """Test basic message creation"""
        standardized_prompt = {
            "user_prompt": {
                "template": "User prompt with {var1}",
                "variables": ["var1"]
            },
            "system_prompt": {
                "template": "System prompt with {var2}",
                "variables": ["var2"]
            }
        }

        system_prompt, messages = self.runner._create_messages(standardized_prompt, self.test_inputs)

        self.assertEqual(system_prompt, "System prompt with value2")
        self.assertEqual(len(messages), 1)
        self.assertEqual(messages[0]["user"], "User prompt with value1")

    def test_create_messages_with_few_shot(self):
        """Test message creation with few-shot examples"""
        few_shot_examples = [
            {"input": "example input", "output": "example output"}
        ]

        standardized_prompt = {
            "user_prompt": {
                "template": "User prompt",
                "variables": []
            },
            "few_shot": {
                "examples": few_shot_examples,
                "format": "converse"
            }
        }

        _, messages = self.runner._create_messages(standardized_prompt, self.test_inputs)

        self.assertEqual(len(messages), 3)  # 2 for few-shot + 1 for user prompt
        self.assertEqual(messages[0]["user"], "example input")
        self.assertEqual(messages[1]["assistant"], "example output")

    @patch('concurrent.futures.ThreadPoolExecutor')
    def test_run_inference(self, mock_executor_class):
        """Test running inference"""
        # Setup mocks
        self.mock_dataset_adapter.fetch.return_value = [self.test_row]
        self.mock_prompt_adapter.fetch.return_value = {
            "user_prompt": {
                "template": "Test prompt",
                "variables": []
            }
        }
        self.mock_inference_adapter.call_model.return_value = "test output"

        # Setup mock executor
        mock_executor = Mock()
        mock_future = Mock()
        mock_future.result.return_value = {
            "inputs": self.test_inputs,
            INFERENCE_OUTPUT_FIELD: "test output"
        }
        mock_executor.submit.return_value = mock_future
        mock_executor_class.return_value.__enter__.return_value = mock_executor

        # Run inference
        results = self.runner.run(
            model_id=self.model_id,
            max_tokens=100,
            temperature=0.7,
            top_p=0.9,
            top_k=1
        )

        # Verify results
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0][INFERENCE_OUTPUT_FIELD], "test output")
        self.mock_inference_adapter.call_model.assert_called_once()

    def test_infer_row(self):
        """Test single row inference"""
        self.mock_prompt_adapter.fetch.return_value = {
            "user_prompt": {
                "template": "Test prompt",
                "variables": []
            }
        }
        self.mock_inference_adapter.call_model.return_value = "test output"

        self.runner.model_id = self.model_id
        self.runner.inf_config = {
            "max_tokens": 100,
            "temperature": 0.7,
            "top_p": 0.9,
            "top_k": 1
        }

        result = self.runner._infer_row(self.test_row)

        self.assertEqual(result[INFERENCE_OUTPUT_FIELD], "test output")
        self.mock_inference_adapter.call_model.assert_called_once()

    def test_infer_row_error(self):
        """Test error handling in row inference"""
        self.mock_prompt_adapter.fetch.side_effect = Exception("Test error")

        self.runner.model_id = self.model_id

        with self.assertRaises(Exception):
            self.runner._infer_row(self.test_row)

