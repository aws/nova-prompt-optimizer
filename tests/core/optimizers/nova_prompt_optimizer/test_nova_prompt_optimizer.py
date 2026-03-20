import unittest
from unittest.mock import Mock, PropertyMock, patch

from amzn_nova_prompt_optimizer.core.inference import InferenceAdapter
from amzn_nova_prompt_optimizer.core.input_adapters.dataset_adapter import DatasetAdapter
from amzn_nova_prompt_optimizer.core.input_adapters.metric_adapter import MetricAdapter
from amzn_nova_prompt_optimizer.core.input_adapters.prompt_adapter import PromptAdapter
from amzn_nova_prompt_optimizer.core.optimizers import NovaPromptOptimizer, NovaMPOptimizationAdapter


class TestNovaPromptOptimizer(unittest.TestCase):
    def setUp(self):
        self.mock_variables = {"var1": "value1", "var2": "value2"}
        self.prompt_adapter = Mock(spec=PromptAdapter)
        self.prompt_adapter.variables = self.mock_variables
        # Create a mock PromptAdapter class that can be instantiated
        self.mock_prompt_adapter_class = Mock()
        self.mock_prompt_adapter_instance = Mock(spec=PromptAdapter)
        self.mock_prompt_adapter_class.return_value = self.mock_prompt_adapter_instance
        self.prompt_adapter.__class__ = self.mock_prompt_adapter_class
        self.dataset_adapter = Mock(spec=DatasetAdapter)
        # Configure the input_columns property
        type(self.dataset_adapter).input_columns = PropertyMock(
            return_value=["input1", "input2"]
        )
        # Configure the output_columns property
        type(self.dataset_adapter).output_columns = PropertyMock(
            return_value=["output1"]
        )
        self.dataset_adapter.fetch.return_value = [
            {
                "inputs": {"input1": "test input 1"},
                "outputs": {"output1": "test output 1"}
            },
            {
                "inputs": {"input1": "test input 2"},
                "outputs": {"output1": "test output 2"}
            }
        ]
        self.inference_adapter = Mock(spec=InferenceAdapter)
        self.metric_adapter = Mock(spec=MetricAdapter)

        self.nova_prompt_optimizer = NovaPromptOptimizer(
            prompt_adapter=self.prompt_adapter,
            inference_adapter=self.inference_adapter,
            dataset_adapter=self.dataset_adapter,
            metric_adapter=self.metric_adapter
        )

    def test_optimize_no_inference_adapter(self):
        # Create NovaPromptOptimizer instance without inference_adapter
        nova_prompt_optimizer_no_inference = NovaPromptOptimizer(
            prompt_adapter=self.prompt_adapter,
            inference_adapter=None,
            dataset_adapter=self.dataset_adapter,
            metric_adapter=self.metric_adapter
        )

        # Assert that ValueError is raised when optimize is called
        with self.assertRaises(ValueError) as context:
            nova_prompt_optimizer_no_inference.optimize()

        self.assertTrue("Inference Adapter not passed." in str(context.exception))

    def test_optimize_no_dataset_adapter(self):
        nova_prompt_optimizer_no_dataset = NovaPromptOptimizer(
            prompt_adapter=self.prompt_adapter,
            inference_adapter=self.inference_adapter,
            dataset_adapter=None,
            metric_adapter=self.metric_adapter
        )

        mock_intermediate_prompt_adapter = Mock(spec=PromptAdapter)
        nova_prompt_optimizer_no_dataset.meta_prompt_optimization_adapter.optimize = Mock(return_value=mock_intermediate_prompt_adapter)

        result = nova_prompt_optimizer_no_dataset.optimize()

        self.assertIs(result, mock_intermediate_prompt_adapter)
        nova_prompt_optimizer_no_dataset.meta_prompt_optimization_adapter.optimize.assert_called_once()

    def test_optimize_no_metric_adapter(self):
        nova_prompt_optimizer_no_metric = NovaPromptOptimizer(
            prompt_adapter=self.prompt_adapter,
            inference_adapter=self.inference_adapter,
            dataset_adapter=self.dataset_adapter,
            metric_adapter=None
        )

        mock_intermediate_prompt_adapter = Mock(spec=PromptAdapter)
        nova_prompt_optimizer_no_metric.meta_prompt_optimization_adapter.optimize = Mock(return_value=mock_intermediate_prompt_adapter)

        result = nova_prompt_optimizer_no_metric.optimize()

        self.assertIs(result, mock_intermediate_prompt_adapter)
        nova_prompt_optimizer_no_metric.meta_prompt_optimization_adapter.optimize.assert_called_once()

    @patch('amzn_nova_prompt_optimizer.core.optimizers.nova_prompt_optimizer.nova_prompt_optimizer.NovaMIPROv2OptimizationAdapter')
    def test_optimize_with_all_adapters_default_mode(self, mock_miprov2_class):
        # Setup mocks
        mock_intermediate_prompt_adapter = Mock(spec=PromptAdapter)
        mock_final_prompt_adapter = Mock(spec=PromptAdapter)
        
        self.nova_prompt_optimizer.meta_prompt_optimization_adapter.optimize = Mock(
            return_value=mock_intermediate_prompt_adapter
        )
        
        mock_miprov2_instance = Mock()
        mock_miprov2_instance.optimize.return_value = mock_final_prompt_adapter
        mock_miprov2_class.return_value = mock_miprov2_instance
        
        # Test default mode (pro)
        result = self.nova_prompt_optimizer.optimize()
        
        # Verify meta prompt optimization was called
        self.nova_prompt_optimizer.meta_prompt_optimization_adapter.optimize.assert_called_once_with(
            prompter_model_id="us.amazon.nova-2-lite-v1:0"
        )
        
        # Verify MIPROv2 was initialized and called
        mock_miprov2_class.assert_called_once_with(
            prompt_adapter=mock_intermediate_prompt_adapter,
            dataset_adapter=self.dataset_adapter,
            metric_adapter=self.metric_adapter,
            inference_adapter=self.inference_adapter
        )
        
        mock_miprov2_instance.optimize.assert_called_once_with(
            prompter_model_id="us.amazon.nova-2-lite-v1:0",
            task_model_id="us.amazon.nova-pro-v1:0",
            num_candidates=20,
            num_trials=30,
            max_bootstrapped_demos=4,
            max_labeled_demos=4,
            enable_json_fallback=False
        )
        
        self.assertIs(result, mock_final_prompt_adapter)

    @patch('amzn_nova_prompt_optimizer.core.optimizers.nova_prompt_optimizer.nova_prompt_optimizer.NovaMIPROv2OptimizationAdapter')
    def test_optimize_with_lite_mode(self, mock_miprov2_class):
        mock_intermediate_prompt_adapter = Mock(spec=PromptAdapter)
        mock_final_prompt_adapter = Mock(spec=PromptAdapter)
        
        self.nova_prompt_optimizer.meta_prompt_optimization_adapter.optimize = Mock(
            return_value=mock_intermediate_prompt_adapter
        )
        
        mock_miprov2_instance = Mock()
        mock_miprov2_instance.optimize.return_value = mock_final_prompt_adapter
        mock_miprov2_class.return_value = mock_miprov2_instance
        
        result = self.nova_prompt_optimizer.optimize(mode="lite")

        # Verify meta prompt optimization was called
        self.nova_prompt_optimizer.meta_prompt_optimization_adapter.optimize.assert_called_once_with(
            prompter_model_id="us.amazon.nova-2-lite-v1:0"
        )
        
        mock_miprov2_instance.optimize.assert_called_once_with(
            prompter_model_id="us.amazon.nova-2-lite-v1:0",
            task_model_id="us.amazon.nova-lite-v1:0",
            num_candidates=20,
            num_trials=30,
            max_bootstrapped_demos=4,
            max_labeled_demos=4,
            enable_json_fallback=False
        )
        
        self.assertIs(result, mock_final_prompt_adapter)

    @patch('amzn_nova_prompt_optimizer.core.optimizers.nova_prompt_optimizer.nova_prompt_optimizer.NovaMIPROv2OptimizationAdapter')
    def test_optimize_with_custom_mode(self, mock_miprov2_class):
        mock_intermediate_prompt_adapter = Mock(spec=PromptAdapter)
        mock_final_prompt_adapter = Mock(spec=PromptAdapter)
        
        self.nova_prompt_optimizer.meta_prompt_optimization_adapter.optimize = Mock(
            return_value=mock_intermediate_prompt_adapter
        )
        
        mock_miprov2_instance = Mock()
        mock_miprov2_instance.optimize.return_value = mock_final_prompt_adapter
        mock_miprov2_class.return_value = mock_miprov2_instance
        
        custom_params = {
            "task_model_id": "custom-model",
            "num_candidates": 10,
            "num_trials": 15,
            "max_bootstrapped_demos": 2,
            "max_labeled_demos": 3,
            "meta_prompt_model_id": "custom-meta-model"
        }
        
        result = self.nova_prompt_optimizer.optimize(mode="custom", custom_params=custom_params)
        
        self.nova_prompt_optimizer.meta_prompt_optimization_adapter.optimize.assert_called_once_with(
            prompter_model_id="custom-meta-model"
        )
        
        mock_miprov2_instance.optimize.assert_called_once_with(
            task_model_id="custom-model",
            num_candidates=10,
            num_trials=15,
            max_bootstrapped_demos=2,
            max_labeled_demos=3,
            enable_json_fallback=False
        )
        
        self.assertIs(result, mock_final_prompt_adapter)

    @patch('amzn_nova_prompt_optimizer.core.optimizers.nova_prompt_optimizer.nova_prompt_optimizer.NovaMIPROv2OptimizationAdapter')
    def test_optimize_with_custom_mode_no_meta_prompt_model_id(self, mock_miprov2_class):
        mock_intermediate_prompt_adapter = Mock(spec=PromptAdapter)
        mock_final_prompt_adapter = Mock(spec=PromptAdapter)

        self.nova_prompt_optimizer.meta_prompt_optimization_adapter.optimize = Mock(
            return_value=mock_intermediate_prompt_adapter
        )

        mock_miprov2_instance = Mock()
        mock_miprov2_instance.optimize.return_value = mock_final_prompt_adapter
        mock_miprov2_class.return_value = mock_miprov2_instance

        custom_params = {
            "task_model_id": "custom-model",
            "num_candidates": 10,
            "num_trials": 15,
            "max_bootstrapped_demos": 2,
            "max_labeled_demos": 3,
        }

        result = self.nova_prompt_optimizer.optimize(mode="custom", custom_params=custom_params)

        self.nova_prompt_optimizer.meta_prompt_optimization_adapter.optimize.assert_called_once_with()

        mock_miprov2_instance.optimize.assert_called_once_with(
            task_model_id="custom-model",
            num_candidates=10,
            num_trials=15,
            max_bootstrapped_demos=2,
            max_labeled_demos=3,
            enable_json_fallback=False
        )

        self.assertIs(result, mock_final_prompt_adapter)

    def test_optimize_custom_mode_no_params(self):
        with self.assertRaises(ValueError) as context:
            self.nova_prompt_optimizer.optimize(mode="custom")
        
        self.assertIn("Custom mode requires custom_params dictionary", str(context.exception))

    @patch('amzn_nova_prompt_optimizer.core.optimizers.nova_prompt_optimizer.nova_prompt_optimizer.NovaMIPROv2OptimizationAdapter')
    def test_optimize_with_separate_meta_prompt_adapter(self, mock_miprov2_class):
        """Test using separate inference adapters for meta-prompting and task optimization."""
        # Create separate mock adapters
        meta_prompt_adapter = Mock(spec=InferenceAdapter)
        task_adapter = Mock(spec=InferenceAdapter)
        
        # Create optimizer with separate adapters
        optimizer = NovaPromptOptimizer(
            prompt_adapter=self.prompt_adapter,
            inference_adapter=task_adapter,
            dataset_adapter=self.dataset_adapter,
            metric_adapter=self.metric_adapter,
            meta_prompt_inference_adapter=meta_prompt_adapter
        )
        
        # Verify the adapters are set correctly
        self.assertIs(optimizer.inference_adapter, task_adapter)
        self.assertIs(optimizer.meta_prompt_inference_adapter, meta_prompt_adapter)
        self.assertIs(optimizer.meta_prompt_optimization_adapter.inference_adapter, meta_prompt_adapter)
        
        # Mock the optimization process
        mock_intermediate_prompt_adapter = Mock(spec=PromptAdapter)
        mock_final_prompt_adapter = Mock(spec=PromptAdapter)
        
        optimizer.meta_prompt_optimization_adapter.optimize = Mock(
            return_value=mock_intermediate_prompt_adapter
        )
        
        mock_miprov2_instance = Mock()
        mock_miprov2_instance.optimize.return_value = mock_final_prompt_adapter
        mock_miprov2_class.return_value = mock_miprov2_instance
        
        # Run optimization
        result = optimizer.optimize(mode="pro")
        
        # Verify meta-prompt adapter was used for meta-prompting
        optimizer.meta_prompt_optimization_adapter.optimize.assert_called_once()
        
        # Verify task adapter was passed to MIPROv2
        mock_miprov2_class.assert_called_once()
        call_kwargs = mock_miprov2_class.call_args[1]
        self.assertIs(call_kwargs['inference_adapter'], task_adapter)
        
        self.assertIs(result, mock_final_prompt_adapter)

    @patch('amzn_nova_prompt_optimizer.core.inference.BedrockInferenceAdapter')
    def test_separate_adapter_defaults_to_bedrock(self, mock_bedrock_class):
        """Test that meta_prompt_inference_adapter defaults to BedrockInferenceAdapter if not provided."""
        mock_bedrock_instance = Mock(spec=InferenceAdapter)
        mock_bedrock_class.return_value = mock_bedrock_instance
        
        optimizer = NovaPromptOptimizer(
            prompt_adapter=self.prompt_adapter,
            inference_adapter=self.inference_adapter,
            dataset_adapter=self.dataset_adapter,
            metric_adapter=self.metric_adapter
        )
        
        # Should create a default BedrockInferenceAdapter for meta-prompting
        mock_bedrock_class.assert_called_once()
        call_kwargs = mock_bedrock_class.call_args[1]
        self.assertEqual(call_kwargs['rate_limit'], 5)
        
        # Should use the created Bedrock adapter for meta-prompting
        self.assertIs(optimizer.meta_prompt_inference_adapter, mock_bedrock_instance)
        
        # Should use the provided adapter for task optimization
        self.assertIs(optimizer.inference_adapter, self.inference_adapter)
        
        # Meta-prompt optimization adapter should use the Bedrock adapter
        self.assertIs(optimizer.meta_prompt_optimization_adapter.inference_adapter, mock_bedrock_instance)

    def test_optimize_custom_mode_missing_required_keys(self):
        incomplete_params = {
            "task_model_id": "custom-model",
            "num_candidates": 10
            # Missing other required keys
        }
        
        with self.assertRaises(ValueError) as context:
            self.nova_prompt_optimizer.optimize(mode="custom", custom_params=incomplete_params)
        
        self.assertIn("custom_params must contain all required keys", str(context.exception))

    @patch('amzn_nova_prompt_optimizer.core.optimizers.nova_prompt_optimizer.nova_prompt_optimizer.NovaMIPROv2OptimizationAdapter')
    @patch('amzn_nova_prompt_optimizer.core.optimizers.nova_prompt_optimizer.nova_prompt_optimizer.logger')
    def test_optimize_invalid_mode_defaults_to_pro(self, mock_logger, mock_miprov2_class):
        mock_intermediate_prompt_adapter = Mock(spec=PromptAdapter)
        mock_final_prompt_adapter = Mock(spec=PromptAdapter)

        self.nova_prompt_optimizer.meta_prompt_optimization_adapter.optimize = Mock(
            return_value=mock_intermediate_prompt_adapter
        )

        mock_miprov2_instance = Mock()
        mock_miprov2_instance.optimize.return_value = mock_final_prompt_adapter
        mock_miprov2_class.return_value = mock_miprov2_instance

        result = self.nova_prompt_optimizer.optimize(mode="invalid_mode")

        mock_logger.warning.assert_called_once_with(
            "Mode 'invalid_mode' not detected, defaulting to 'pro' mode"
        )

        # Verify meta prompt optimization was called
        self.nova_prompt_optimizer.meta_prompt_optimization_adapter.optimize.assert_called_once_with(
            prompter_model_id="us.amazon.nova-2-lite-v1:0"
        )

        # Verify MIPROv2 was initialized and called
        mock_miprov2_class.assert_called_once_with(
            prompt_adapter=mock_intermediate_prompt_adapter,
            dataset_adapter=self.dataset_adapter,
            metric_adapter=self.metric_adapter,
            inference_adapter=self.inference_adapter
        )

        mock_miprov2_instance.optimize.assert_called_once_with(
            prompter_model_id="us.amazon.nova-2-lite-v1:0",
            task_model_id="us.amazon.nova-pro-v1:0",
            num_candidates=20,
            num_trials=30,
            max_bootstrapped_demos=4,
            max_labeled_demos=4,
            enable_json_fallback=False
        )

        self.assertIs(result, mock_final_prompt_adapter)

    @patch('amzn_nova_prompt_optimizer.core.optimizers.nova_prompt_optimizer.nova_prompt_optimizer.NovaMIPROv2OptimizationAdapter')
    def test_optimize_all_modes(self, mock_miprov2_class):
        modes = ["micro", "lite", "pro", "lite-2"]
        expected_task_models = {
            "micro": "us.amazon.nova-micro-v1:0",
            "lite": "us.amazon.nova-lite-v1:0",
            "pro": "us.amazon.nova-pro-v1:0",
            "lite-2": "us.amazon.nova-2-lite-v1:0"
        }
        
        for mode in modes:
            with self.subTest(mode=mode):
                mock_intermediate_prompt_adapter = Mock(spec=PromptAdapter)
                mock_final_prompt_adapter = Mock(spec=PromptAdapter)
                
                self.nova_prompt_optimizer.meta_prompt_optimization_adapter.optimize = Mock(
                    return_value=mock_intermediate_prompt_adapter
                )
                
                mock_miprov2_instance = Mock()
                mock_miprov2_instance.optimize.return_value = mock_final_prompt_adapter
                mock_miprov2_class.return_value = mock_miprov2_instance
                
                result = self.nova_prompt_optimizer.optimize(mode=mode)
                
                mock_miprov2_instance.optimize.assert_called_with(
                    prompter_model_id="us.amazon.nova-2-lite-v1:0",
                    task_model_id=expected_task_models[mode],
                    num_candidates=20,
                    num_trials=30,
                    max_bootstrapped_demos=4,
                    max_labeled_demos=4,
                    enable_json_fallback=False
                )
                
                self.assertIs(result, mock_final_prompt_adapter)
                
                # Reset mocks for next iteration
                mock_miprov2_class.reset_mock()
                mock_miprov2_instance.reset_mock()
