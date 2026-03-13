"""
Integration test for separate inference adapters feature.

This test verifies that the NovaPromptOptimizer correctly uses separate
adapters for meta-prompting and task optimization phases.
"""

import unittest
from unittest.mock import Mock, patch, call

from amzn_nova_prompt_optimizer.core.inference import InferenceAdapter
from amzn_nova_prompt_optimizer.core.input_adapters.dataset_adapter import DatasetAdapter
from amzn_nova_prompt_optimizer.core.input_adapters.metric_adapter import MetricAdapter
from amzn_nova_prompt_optimizer.core.input_adapters.prompt_adapter import PromptAdapter
from amzn_nova_prompt_optimizer.core.optimizers import NovaPromptOptimizer


class TestSeparateAdaptersIntegration(unittest.TestCase):
    """Integration tests for separate inference adapters."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Create mock adapters
        self.meta_prompt_adapter = Mock(spec=InferenceAdapter)
        self.task_adapter = Mock(spec=InferenceAdapter)
        
        # Create mock prompt adapter
        self.prompt_adapter = Mock(spec=PromptAdapter)
        self.prompt_adapter.fetch.return_value = {
            "user_prompt": {"content": "Test {{input}}", "variables": ["input"]},
            "system_prompt": {"content": "You are helpful"}
        }
        self.prompt_adapter.fetch_system_template.return_value = "You are helpful"
        self.prompt_adapter.fetch_user_template.return_value = "Test {{input}}"
        
        # Create mock dataset adapter
        self.dataset_adapter = Mock(spec=DatasetAdapter)
        self.dataset_adapter.input_columns = ["input"]
        self.dataset_adapter.output_columns = ["output"]
        self.dataset_adapter.fetch.return_value = [
            {"inputs": {"input": "test1"}, "outputs": {"output": "result1"}},
            {"inputs": {"input": "test2"}, "outputs": {"output": "result2"}}
        ]
        
        # Create mock metric adapter
        self.metric_adapter = Mock(spec=MetricAdapter)
        self.metric_adapter.apply.return_value = 1.0
        self.metric_adapter.batch_apply.return_value = 1.0
    
    @patch('amzn_nova_prompt_optimizer.core.optimizers.nova_prompt_optimizer.nova_prompt_optimizer.NovaMIPROv2OptimizationAdapter')
    def test_separate_adapters_used_correctly(self, mock_mipro_class):
        """Test that separate adapters are used in correct phases."""
        
        # Setup mocks
        mock_intermediate_prompt = Mock(spec=PromptAdapter)
        mock_final_prompt = Mock(spec=PromptAdapter)
        
        mock_mipro_instance = Mock()
        mock_mipro_instance.optimize.return_value = mock_final_prompt
        mock_mipro_class.return_value = mock_mipro_instance
        
        # Create optimizer with separate adapters
        optimizer = NovaPromptOptimizer(
            prompt_adapter=self.prompt_adapter,
            inference_adapter=self.task_adapter,
            dataset_adapter=self.dataset_adapter,
            metric_adapter=self.metric_adapter,
            meta_prompt_inference_adapter=self.meta_prompt_adapter
        )
        
        # Verify initialization
        self.assertIs(optimizer.inference_adapter, self.task_adapter)
        self.assertIs(optimizer.meta_prompt_inference_adapter, self.meta_prompt_adapter)
        
        # Verify meta-prompt optimization adapter uses meta-prompt adapter
        self.assertIs(
            optimizer.meta_prompt_optimization_adapter.inference_adapter,
            self.meta_prompt_adapter
        )
        
        # Mock the meta-prompt optimization
        optimizer.meta_prompt_optimization_adapter.optimize = Mock(
            return_value=mock_intermediate_prompt
        )
        
        # Run optimization
        result = optimizer.optimize(mode="lite")
        
        # Verify meta-prompt adapter was used for meta-prompting
        optimizer.meta_prompt_optimization_adapter.optimize.assert_called_once()
        
        # Verify task adapter was used for MIPROv2
        mock_mipro_class.assert_called_once()
        mipro_call_kwargs = mock_mipro_class.call_args[1]
        self.assertIs(mipro_call_kwargs['inference_adapter'], self.task_adapter)
        
        # Verify result
        self.assertIs(result, mock_final_prompt)
    
    @patch('amzn_nova_prompt_optimizer.core.inference.BedrockInferenceAdapter')
    @patch('amzn_nova_prompt_optimizer.core.optimizers.nova_prompt_optimizer.nova_prompt_optimizer.NovaMIPROv2OptimizationAdapter')
    def test_single_adapter_creates_default_bedrock(self, mock_mipro_class, mock_bedrock_class):
        """Test that default BedrockInferenceAdapter is created when only one adapter is provided."""
        
        # Setup mocks
        mock_bedrock_instance = Mock(spec=InferenceAdapter)
        mock_bedrock_class.return_value = mock_bedrock_instance
        
        mock_intermediate_prompt = Mock(spec=PromptAdapter)
        mock_final_prompt = Mock(spec=PromptAdapter)
        
        mock_mipro_instance = Mock()
        mock_mipro_instance.optimize.return_value = mock_final_prompt
        mock_mipro_class.return_value = mock_mipro_instance
        
        # Create optimizer with single adapter (creates default Bedrock for meta-prompting)
        optimizer = NovaPromptOptimizer(
            prompt_adapter=self.prompt_adapter,
            inference_adapter=self.task_adapter,
            dataset_adapter=self.dataset_adapter,
            metric_adapter=self.metric_adapter
            # No meta_prompt_inference_adapter provided
        )
        
        # Verify Bedrock adapter was created for meta-prompting
        mock_bedrock_class.assert_called_once()
        
        # Verify different adapters are used
        self.assertIs(optimizer.inference_adapter, self.task_adapter)
        self.assertIs(optimizer.meta_prompt_inference_adapter, mock_bedrock_instance)
        
        # Verify meta-prompt optimization adapter uses Bedrock adapter
        self.assertIs(
            optimizer.meta_prompt_optimization_adapter.inference_adapter,
            mock_bedrock_instance
        )
        
        # Mock the meta-prompt optimization
        optimizer.meta_prompt_optimization_adapter.optimize = Mock(
            return_value=mock_intermediate_prompt
        )
        
        # Run optimization
        result = optimizer.optimize(mode="pro")
        
        # Verify Bedrock adapter was used for meta-prompting
        optimizer.meta_prompt_optimization_adapter.optimize.assert_called_once()
        
        # Verify task adapter was used for MIPROv2
        mock_mipro_class.assert_called_once()
        mipro_call_kwargs = mock_mipro_class.call_args[1]
        self.assertIs(mipro_call_kwargs['inference_adapter'], self.task_adapter)
        
        # Verify result
        self.assertIs(result, mock_final_prompt)
    
    @patch('amzn_nova_prompt_optimizer.core.optimizers.nova_prompt_optimizer.nova_prompt_optimizer.NovaMIPROv2OptimizationAdapter')
    @patch('amzn_nova_prompt_optimizer.core.optimizers.nova_prompt_optimizer.nova_prompt_optimizer.NovaMPOptimizationAdapter')
    def test_custom_mode_with_separate_adapters(self, mock_mp_class, mock_mipro_class):
        """Test custom mode with separate adapters and custom parameters."""
        
        # Setup mocks
        mock_mp_instance = Mock()
        mock_intermediate_prompt = Mock(spec=PromptAdapter)
        mock_mp_instance.optimize.return_value = mock_intermediate_prompt
        mock_mp_class.return_value = mock_mp_instance
        
        mock_mipro_instance = Mock()
        mock_final_prompt = Mock(spec=PromptAdapter)
        mock_mipro_instance.optimize.return_value = mock_final_prompt
        mock_mipro_class.return_value = mock_mipro_instance
        
        # Create optimizer with separate adapters
        optimizer = NovaPromptOptimizer(
            prompt_adapter=self.prompt_adapter,
            inference_adapter=self.task_adapter,
            dataset_adapter=self.dataset_adapter,
            metric_adapter=self.metric_adapter,
            meta_prompt_inference_adapter=self.meta_prompt_adapter
        )
        
        # Custom parameters
        custom_params = {
            "meta_prompt_model_id": "us.amazon.nova-2-lite-v1:0",
            "task_model_id": "custom-task-model",
            "num_candidates": 10,
            "num_trials": 15,
            "max_bootstrapped_demos": 2,
            "max_labeled_demos": 3
        }
        
        # Run optimization with custom params
        result = optimizer.optimize(mode="custom", custom_params=custom_params)
        
        # Verify meta-prompt adapter was used with correct model ID
        mock_mp_instance.optimize.assert_called_once_with(
            prompter_model_id="us.amazon.nova-2-lite-v1:0"
        )
        
        # Verify task adapter was used with correct parameters
        mock_mipro_instance.optimize.assert_called_once_with(
            task_model_id="custom-task-model",
            num_candidates=10,
            num_trials=15,
            max_bootstrapped_demos=2,
            max_labeled_demos=3,
            enable_json_fallback=False
        )
        
        # Verify result
        self.assertIs(result, mock_final_prompt)
    
    def test_adapter_types_preserved(self):
        """Test that adapter types are preserved correctly."""
        
        # Create optimizer with separate adapters
        optimizer = NovaPromptOptimizer(
            prompt_adapter=self.prompt_adapter,
            inference_adapter=self.task_adapter,
            dataset_adapter=self.dataset_adapter,
            metric_adapter=self.metric_adapter,
            meta_prompt_inference_adapter=self.meta_prompt_adapter
        )
        
        # Verify adapters are stored correctly
        self.assertIsInstance(optimizer.inference_adapter, InferenceAdapter)
        self.assertIsInstance(optimizer.meta_prompt_inference_adapter, InferenceAdapter)
        self.assertIsNot(optimizer.inference_adapter, optimizer.meta_prompt_inference_adapter)
        
        # Verify meta-prompt optimization adapter uses correct adapter
        self.assertIs(
            optimizer.meta_prompt_optimization_adapter.inference_adapter,
            self.meta_prompt_adapter
        )


class TestRealWorldScenarios(unittest.TestCase):
    """Test real-world usage scenarios."""
    
    def test_bedrock_sagemaker_combination(self):
        """Test typical scenario: Bedrock for meta-prompting, SageMaker for task."""
        
        # This test verifies the typical use case structure
        # In real usage, these would be actual adapter instances
        
        meta_adapter = Mock(spec=InferenceAdapter)
        task_adapter = Mock(spec=InferenceAdapter)
        
        prompt_adapter = Mock(spec=PromptAdapter)
        dataset_adapter = Mock(spec=DatasetAdapter)
        metric_adapter = Mock(spec=MetricAdapter)
        
        # Create optimizer
        optimizer = NovaPromptOptimizer(
            prompt_adapter=prompt_adapter,
            inference_adapter=task_adapter,
            dataset_adapter=dataset_adapter,
            metric_adapter=metric_adapter,
            meta_prompt_inference_adapter=meta_adapter
        )
        
        # Verify configuration - adapters are correctly assigned
        self.assertIs(optimizer.meta_prompt_inference_adapter, meta_adapter)
        self.assertIs(optimizer.inference_adapter, task_adapter)
        self.assertIsNot(optimizer.meta_prompt_inference_adapter, optimizer.inference_adapter)


if __name__ == '__main__':
    unittest.main()
