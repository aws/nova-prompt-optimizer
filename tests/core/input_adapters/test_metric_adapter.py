import unittest

from amzn_nova_prompt_optimizer.core.input_adapters.metric_adapter import MetricAdapter

from typing import Any, List


class AccuracyMetricAdapter(MetricAdapter):
    def apply(self, y_pred: Any, y_true: Any) -> float:
        return 1.0 if y_pred == y_true else 0.0

    def batch_apply(self, y_preds: List[Any], y_trues: List[Any]) -> float:
        if len(y_preds) != len(y_trues):
            raise ValueError("Length of predictions and ground truths must match")
        if not y_preds:
            raise ValueError("Empty predictions list")
        return sum(self.apply(p, t) for p, t in zip(y_preds, y_trues)) / len(y_preds)


class TestMetricAdapter(unittest.TestCase):
    def setUp(self):
        """Set up test cases"""
        self.metric = AccuracyMetricAdapter()
        self.single_pred = "class_a"
        self.single_true = "class_a"
        self.batch_preds = ["class_a", "class_b", "class_a"]
        self.batch_trues = ["class_a", "class_b", "class_b"]

    def test_cannot_instantiate_abstract_class(self):
        """Test that MetricAdapter cannot be instantiated directly"""
        with self.assertRaises(TypeError):
            MetricAdapter()

    def test_single_correct_prediction(self):
        """Test metric for a single correct prediction"""
        score = self.metric.apply(self.single_pred, self.single_true)
        self.assertEqual(score, 1.0)

    def test_single_incorrect_prediction(self):
        """Test metric for a single incorrect prediction"""
        score = self.metric.apply("class_b", "class_a")
        self.assertEqual(score, 0.0)

    def test_batch_predictions(self):
        """Test metric for batch predictions"""
        score = self.metric.batch_apply(self.batch_preds, self.batch_trues)
        # 2 correct predictions out of 3
        self.assertEqual(score, 2 / 3)

    def test_empty_batch(self):
        """Test metric with empty batch"""
        with self.assertRaises(ValueError):
            self.metric.batch_apply([], [])

    def test_mismatched_lengths(self):
        """Test metric with mismatched prediction and truth lengths"""
        with self.assertRaises(ValueError):
            self.metric.batch_apply(["class_a"], ["class_a", "class_b"])

    def test_batch_all_correct(self):
        """Test metric with all correct predictions"""
        preds = ["class_a", "class_b"]
        trues = ["class_a", "class_b"]
        score = self.metric.batch_apply(preds, trues)
        self.assertEqual(score, 1.0)

    def test_batch_all_incorrect(self):
        """Test metric with all incorrect predictions"""
        preds = ["class_a", "class_b"]
        trues = ["class_b", "class_a"]
        score = self.metric.batch_apply(preds, trues)
        self.assertEqual(score, 0.0)

    def test_different_data_types(self):
        """Test metric with different data types"""
        # Test with integers
        self.assertEqual(self.metric.apply(1, 1), 1.0)
        self.assertEqual(self.metric.apply(1, 2), 0.0)

        # Test with mixed types (should still work based on equality)
        self.assertEqual(self.metric.apply("1", 1), 0.0)

    def test_batch_apply_with_different_types(self):
        """Test batch_apply with different data types"""
        preds = [1, "2", 3.0]
        trues = [1, "2", 3.0]
        score = self.metric.batch_apply(preds, trues)
        self.assertEqual(score, 1.0)


class MockMetricAdapter(MetricAdapter):
    """Mock implementation for testing abstract methods"""

    def apply(self, y_pred: Any, y_true: Any) -> float:
        return 0.0

    def batch_apply(self, y_preds: List[Any], y_trues: List[Any]) -> float:
        return 0.0


class TestMetricAdapterInterface(unittest.TestCase):
    """Test cases for the MetricAdapter interface"""

    def test_abstract_methods_implementation(self):
        """Test that concrete class must implement abstract methods"""
        # Should work
        mock = MockMetricAdapter()
        self.assertIsInstance(mock, MetricAdapter)

        # Should fail
        with self.assertRaises(TypeError):
            class IncompleteMetricAdapter(MetricAdapter):
                pass

            IncompleteMetricAdapter()

    def test_method_signatures(self):
        """Test that method signatures are correct"""
        mock = MockMetricAdapter()

        # Test apply method
        result = mock.apply("pred", "true")
        self.assertIsInstance(result, float)

        # Test batch_apply method
        result = mock.batch_apply(["pred"], ["true"])
        self.assertIsInstance(result, float)
