import unittest
from unittest.mock import Mock, PropertyMock

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

        self.nova_optima = NovaPromptOptimizer(
            prompt_adapter=self.prompt_adapter,
            inference_adapter=self.inference_adapter,
            dataset_adapter=self.dataset_adapter,
            metric_adapter=self.metric_adapter
        )
        self.prompt_adapter = Mock()
        self.inference_adapter = Mock()
        self.dataset_adapter = Mock()
        self.metric_adapter = Mock()

    def test_optimize_no_inference_adapter(self):
        # Create NovaPromptOptimizer instance without inference_adapter
        nova_optima_no_inference = NovaPromptOptimizer(
            prompt_adapter=self.prompt_adapter,
            inference_adapter=None,
            dataset_adapter=self.dataset_adapter,
            metric_adapter=self.metric_adapter
        )

        # Assert that ValueError is raised when optimize is called
        with self.assertRaises(ValueError) as context:
            nova_optima_no_inference.optimize()

        self.assertTrue("Inference Adapter not passed." in str(context.exception))

    def test_optimize_no_dataset_adapter(self):
        nova_optima_no_dataset = NovaPromptOptimizer(
            prompt_adapter=self.prompt_adapter,
            inference_adapter=self.inference_adapter,
            dataset_adapter=None,
            metric_adapter=self.metric_adapter
        )

        mock_intermediate_prompt_adapter = Mock(spec=PromptAdapter)
        nova_optima_no_dataset.meta_prompt_optimization_adapter.optimize = Mock(return_value=mock_intermediate_prompt_adapter)

        result = nova_optima_no_dataset.optimize()

        self.assertIs(result, mock_intermediate_prompt_adapter)
        nova_optima_no_dataset.meta_prompt_optimization_adapter.optimize.assert_called_once()

    def test_optimize_no_metric_adapter(self):
        nova_optima_no_metric = NovaPromptOptimizer(
            prompt_adapter=self.prompt_adapter,
            inference_adapter=self.inference_adapter,
            dataset_adapter=self.dataset_adapter,
            metric_adapter=None
        )

        mock_intermediate_prompt_adapter = Mock(spec=PromptAdapter)
        nova_optima_no_metric.meta_prompt_optimization_adapter.optimize = Mock(return_value=mock_intermediate_prompt_adapter)

        result = nova_optima_no_metric.optimize()

        self.assertIs(result, mock_intermediate_prompt_adapter)
        nova_optima_no_metric.meta_prompt_optimization_adapter.optimize.assert_called_once()
