import unittest
from unittest.mock import Mock, patch

from amzn_nova_prompt_optimizer.core.inference import InferenceAdapter, MAX_TOKENS_FIELD, TEMPERATURE_FIELD, \
    TOP_P_FIELD, TOP_K_FIELD
from amzn_nova_prompt_optimizer.core.input_adapters.dataset_adapter import DatasetAdapter
from amzn_nova_prompt_optimizer.core.input_adapters.metric_adapter import MetricAdapter
from amzn_nova_prompt_optimizer.core.input_adapters.prompt_adapter import PromptAdapter
from amzn_nova_prompt_optimizer.core.optimizers import NovaMPOptimizationAdapter, OptimizationAdapter


class TestNovaMPOptimizationAdapter(unittest.TestCase):
    def setUp(self):
        self.prompt_adapter = Mock()
        self.inference_adapter = Mock()
        self.dataset_adapter = Mock()
        self.metric_adapter = Mock()

        self.optimizer = NovaMPOptimizationAdapter(
            prompt_adapter=self.prompt_adapter,
            inference_adapter=self.inference_adapter,
            dataset_adapter=self.dataset_adapter,
            metric_adapter=self.metric_adapter
        )

    def test_init(self):
        """Test initialization of NovaMPOptimizationAdapter"""
        self.assertEqual(self.optimizer.inference_config[MAX_TOKENS_FIELD], 5000)
        self.assertEqual(self.optimizer.inference_config[TEMPERATURE_FIELD], 1.0)
        self.assertEqual(self.optimizer.inference_config[TOP_P_FIELD], 1.0)
        self.assertEqual(self.optimizer.inference_config[TOP_K_FIELD], 1)

    def test_optimize_no_inference_adapter(self):
        """Test optimize method raises error when inference_adapter is None"""
        optimizer = NovaMPOptimizationAdapter(
            prompt_adapter=self.prompt_adapter,
            inference_adapter=None
        )
        with self.assertRaises(ValueError):
            optimizer.optimize()

    def test_split_prompt_valid(self):
        """Test _split_prompt with valid input"""
        prompt = "<system_prompt>System content</system_prompt><user_prompt>User content</user_prompt>"
        system_prompt, user_prompt = self.optimizer._split_prompt(prompt)
        self.assertEqual(system_prompt, "System content")
        self.assertEqual(user_prompt, "User content")

    def test_split_prompt_invalid(self):
        """Test _split_prompt with invalid input"""
        prompt = "Invalid prompt format"
        system_prompt, user_prompt = self.optimizer._split_prompt(prompt)
        self.assertIsNone(system_prompt)
        self.assertIsNone(user_prompt)

    def test_validate_prompt(self):
        """Test _validate_prompt method"""
        system_prompt = "Test Prompt"
        user_prompt = "Test prompt with {{var1}} and {{var2}}"
        variables = ["var1", "var2"]
        self.assertTrue(self.optimizer._validate_user_prompt(user_prompt, variables))
        self.assertTrue(self.optimizer._validate_system_prompt(system_prompt, variables))

        # Test with missing variables
        variables = ["var1", "var2", "var3"]
        self.assertFalse(self.optimizer._validate_user_prompt(user_prompt, variables))
        self.assertTrue(self.optimizer._validate_system_prompt(user_prompt, variables))

        # Test with variables in System Prompt and User Prompt
        system_prompt = "Test Prompt with {{ var1 }}"
        user_prompt = "Test prompt with {{ var1 }}, {{var2}} and {{var3}}"
        variables = ["var1", "var2", "var3"]
        self.assertTrue(self.optimizer._validate_user_prompt(user_prompt, variables))
        self.assertFalse(self.optimizer._validate_system_prompt(user_prompt, variables))

        # Test with None prompt
        self.assertFalse(self.optimizer._validate_user_prompt(None, variables))
        self.assertFalse(self.optimizer._validate_system_prompt(None, variables))

        # Test with empty variables
        self.assertTrue(self.optimizer._validate_user_prompt(user_prompt, []))
        self.assertTrue(self.optimizer._validate_system_prompt(system_prompt, []))

    def test_format_prompt_with_variables(self):
        """Test _format_prompt_with_variables method"""
        prompt = "Test prompt with {{var1}}"
        variables = ["var1", "var2"]
        formatted_prompt = self.optimizer._format_prompt_with_variables(prompt, variables)

        self.assertIn("{{var1}}", formatted_prompt)
        self.assertIn("{{var2}}", formatted_prompt)
        self.assertIn("Here are the additional inputs:", formatted_prompt)

    @patch('logging.getLogger')
    def test_optimize_success(self, mock_logger):
        """Test successful optimization"""
        self.prompt_adapter.fetch.return_value = {
            'system': {'variables': []},
            'user': {'variables': []}
        }
        self.prompt_adapter.fetch_system_template.return_value = "System template"
        self.prompt_adapter.fetch_user_template.return_value = "User template"

        self.inference_adapter.call_model.return_value = (
            "<system_prompt>Optimized system</system_prompt>"
            "<user_prompt>Optimized user</user_prompt>"
        )

        result = self.optimizer.optimize()
        self.assertIsNotNone(result)
        self.inference_adapter.call_model.assert_called_once()

    def test_optimize_max_retries(self):
        """Test optimization with max retries"""
        # Setup mock responses
        self.prompt_adapter.fetch.return_value = {
            'system': {'variables': ['var1']},
            'user': {'variables': ['var2']}
        }
        self.prompt_adapter.fetch_system_template.return_value = "System template {var1}"
        self.prompt_adapter.fetch_user_template.return_value = "User template {var2}"

        # Create a real method instead of mocking _format_prompt_with_variables
        self.optimizer._format_prompt_with_variables = staticmethod(
            lambda p, v: p if p else ""
        )

        # Mock the inference adapter to return invalid responses
        self.inference_adapter.call_model.side_effect = ["Invalid", "Invalid"]

        # Call optimize
        result = self.optimizer.optimize(max_retries=2)

        # Assertions
        self.assertEqual(self.inference_adapter.call_model.call_count, 2)
        self.prompt_adapter.fetch_system_template.assert_called_once()
        self.prompt_adapter.fetch_user_template.assert_called_once()
