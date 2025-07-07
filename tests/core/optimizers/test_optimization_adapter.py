import unittest
from unittest.mock import Mock

from amzn_nova_prompt_optimizer.core.inference import InferenceAdapter
from amzn_nova_prompt_optimizer.core.input_adapters.dataset_adapter import DatasetAdapter
from amzn_nova_prompt_optimizer.core.input_adapters.metric_adapter import MetricAdapter
from amzn_nova_prompt_optimizer.core.input_adapters.prompt_adapter import PromptAdapter
from amzn_nova_prompt_optimizer.core.optimizers.adapter import OptimizationAdapter


class TestOptimizationAdapter(unittest.TestCase):
    def setUp(self):
        """Set up test fixtures before each test method."""
        self.prompt_adapter = Mock(spec=PromptAdapter)
        self.inference_adapter = Mock(spec=InferenceAdapter)
        self.dataset_adapter = Mock(spec=DatasetAdapter)
        self.metric_adapter = Mock(spec=MetricAdapter)

        # Create a concrete implementation of the abstract class for testing
        class ConcreteOptimizationAdapter(OptimizationAdapter):
            def optimize(self) -> PromptAdapter:
                return self.prompt_adapter

        self.optimization_adapter = ConcreteOptimizationAdapter(
            prompt_adapter=self.prompt_adapter,
            inference_adapter=self.inference_adapter,
            dataset_adapter=self.dataset_adapter,
            metric_adapter=self.metric_adapter
        )

    def test_initialization(self):
        """Test if the OptimizationAdapter initializes correctly with all parameters."""
        self.assertEqual(self.optimization_adapter.prompt_adapter, self.prompt_adapter)
        self.assertEqual(self.optimization_adapter.inference_adapter, self.inference_adapter)
        self.assertEqual(self.optimization_adapter.dataset_adapter, self.dataset_adapter)
        self.assertEqual(self.optimization_adapter.metric_adapter, self.metric_adapter)

    def test_initialization_with_optional_params(self):
        """Test initialization with optional parameters as None."""
        optimization_adapter = self.optimization_adapter.__class__(
            prompt_adapter=self.prompt_adapter
        )

        self.assertEqual(optimization_adapter.prompt_adapter, self.prompt_adapter)
        self.assertIsNone(optimization_adapter.inference_adapter)
        self.assertIsNone(optimization_adapter.dataset_adapter)
        self.assertIsNone(optimization_adapter.metric_adapter)

    def test_abstract_class_instantiation(self):
        """Test that OptimizationAdapter cannot be instantiated directly."""
        with self.assertRaises(TypeError):
            OptimizationAdapter(prompt_adapter=self.prompt_adapter)

    def test_optimize_method_implementation(self):
        """Test that the optimize method returns a PromptAdapter."""
        result = self.optimization_adapter.optimize()
        self.assertIsInstance(result, Mock)
        self.assertEqual(result, self.prompt_adapter)
