import unittest
import json

from unittest.mock import Mock, patch, mock_open

from amzn_nova_prompt_optimizer.core.evaluation import EVALUATION_FIELD
from amzn_nova_prompt_optimizer.core.inference import INFERENCE_OUTPUT_FIELD
from amzn_nova_prompt_optimizer.core.input_adapters.dataset_adapter import OUTPUTS_FIELD
from amzn_nova_prompt_optimizer.core.evaluation import Evaluator


class TestEvaluator(unittest.TestCase):
    def setUp(self):
        self.mock_prompt_adapter = Mock()
        self.mock_dataset_adapter = Mock()
        self.mock_metric_adapter = Mock()
        self.mock_inference_adapter = Mock()

        self.evaluator = Evaluator(
            self.mock_prompt_adapter,
            self.mock_dataset_adapter,
            self.mock_metric_adapter,
            self.mock_inference_adapter
        )

        # Clear the class-level cache before each test
        Evaluator._inference_cache.clear()

    def test_get_cache_key(self):
        model_id = "test_model"
        cache_key = self.evaluator._get_cache_key(model_id)
        expected_key = (
            model_id,
            id(self.mock_dataset_adapter),
            id(self.mock_prompt_adapter),
            id(self.mock_metric_adapter)
        )
        self.assertEqual(cache_key, expected_key)

    @patch.object(Evaluator, '_get_or_run_inference')
    def test_aggregate_score(self, mock_get_or_run_inference):
        model_id = "test_model"
        mock_inference_results = [
            {INFERENCE_OUTPUT_FIELD: "pred1", OUTPUTS_FIELD: {"output": "true1"}},
            {INFERENCE_OUTPUT_FIELD: "pred2", OUTPUTS_FIELD: {"output": "true2"}}
        ]
        mock_get_or_run_inference.return_value = mock_inference_results

        self.mock_dataset_adapter.output_columns = ["output"]
        self.mock_metric_adapter.batch_apply.return_value = 0.75

        result = self.evaluator.aggregate_score(model_id)

        self.mock_metric_adapter.batch_apply.assert_called_once_with(["pred1", "pred2"], ["true1", "true2"])
        self.assertEqual(result, 0.75)

    @patch.object(Evaluator, '_get_or_run_inference')
    def test_scores(self, mock_get_or_run_inference):
        model_id = "test_model"
        mock_inference_results = [
            {INFERENCE_OUTPUT_FIELD: "pred1", OUTPUTS_FIELD: {"output": "true1"}},
            {INFERENCE_OUTPUT_FIELD: "pred2", OUTPUTS_FIELD: {"output": "true2"}}
        ]
        mock_get_or_run_inference.return_value = mock_inference_results

        self.mock_dataset_adapter.output_columns = ["output"]
        self.mock_metric_adapter.apply.side_effect = [0.8, 0.9]

        results = self.evaluator.scores(model_id)

        self.assertEqual(len(results), 2)
        self.assertEqual(results[0][EVALUATION_FIELD], 0.8)
        self.assertEqual(results[1][EVALUATION_FIELD], 0.9)

    @patch('amzn_nova_prompt_optimizer.core.evaluation.Path')
    def test_save(self, mock_path):
        mock_file = mock_open()
        mock_path.return_value.open.return_value = mock_file()

        self.evaluator.evaluation_results = [
            {"result1": "value1"},
            {"result2": "value2"}
        ]

        self.evaluator.save("test_output.jsonl")

        mock_path.return_value.parent.mkdir.assert_called_once_with(parents=True, exist_ok=True)
        mock_file().write.assert_any_call(json.dumps({"result1": "value1"}) + '\n')
        mock_file().write.assert_any_call(json.dumps({"result2": "value2"}) + '\n')

    def test_save_no_results(self):
        self.evaluator.evaluation_results = []
        with self.assertLogs(level='WARNING', logger=self.evaluator.logger) as cm:
            self.evaluator.save("test_output.jsonl")
        self.assertIn("No results to save", cm.output[0])

    @patch('amzn_nova_prompt_optimizer.core.evaluation.Path')
    def test_save_exception(self, mock_path):
        mock_path.return_value.open.side_effect = Exception("Test exception")

        self.evaluator.evaluation_results = [{"result": "value"}]

        with self.assertRaises(Exception):
            self.evaluator.save("test_output.jsonl")
