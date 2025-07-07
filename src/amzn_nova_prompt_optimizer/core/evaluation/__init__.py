# Copyright 2025 Amazon Inc

# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
import logging
import json

from amzn_nova_prompt_optimizer.core.inference.adapter import InferenceAdapter
from amzn_nova_prompt_optimizer.core.inference import InferenceRunner, INFERENCE_OUTPUT_FIELD
from amzn_nova_prompt_optimizer.core.input_adapters.dataset_adapter import DatasetAdapter, OUTPUTS_FIELD
from amzn_nova_prompt_optimizer.core.input_adapters.prompt_adapter import PromptAdapter
from amzn_nova_prompt_optimizer.core.input_adapters.metric_adapter import MetricAdapter

from typing import Tuple, List, Any, Dict
from pathlib import Path


EVALUATION_FIELD = "evaluation"


class Evaluator:
    # Class-level cache to store inference results
    _inference_cache: Dict[Tuple, List] = {}

    def __init__(self, prompt_adapter: PromptAdapter, dataset_adapter: DatasetAdapter,
                 metric_adapter: MetricAdapter, inference_adapter: InferenceAdapter):
        """
        Evaluator Class to run evaluations on a Prompt given a dataset and an evaluation metric.
        :param prompt_adapter:
        :param dataset_adapter:
        :param metric_adapter:
        """
        self.logger = logging.getLogger(__name__)
        self.prompt_adapter: PromptAdapter = prompt_adapter
        self.dataset_adapter: DatasetAdapter = dataset_adapter
        self.metric_adapter: MetricAdapter = metric_adapter
        self.inference_adapter: InferenceAdapter = inference_adapter
        self.inference_runner: InferenceRunner = InferenceRunner(prompt_adapter, dataset_adapter, inference_adapter)
        self.y_preds: List[Any] = []
        self.y_trues: List[Any] = []
        self.evaluation_results: List[Dict] = []
        self.inference_results: List[Dict] = []

    def _get_cache_key(self, model_id: str) -> Tuple:
        """Generate a unique cache key based on model and adapters"""
        return (
            model_id,
            id(self.dataset_adapter),
            id(self.prompt_adapter),
            id(self.metric_adapter)
        )

    def _get_or_run_inference(self, model_id: str) -> list:
        """Get cached inference results or run inference if not cached"""
        cache_key = self._get_cache_key(model_id)

        if cache_key not in self._inference_cache:
            self.logger.info("Cache miss - Running new inference on Dataset")
            self._inference_cache[cache_key] = self.inference_runner.run(model_id)
        else:
            self.logger.info("Using cached inference results")

        return self._inference_cache[cache_key]

    def aggregate_score(self, model_id: str):
        """
        Runs Batch evaluation on the dataset using the batch_apply function of the metric
        :param model_id: The Model Id for which we want to evaluate against
        :return:
        """
        # TODO: Replace Implicit Bedrock calls with an InferenceAdapter
        self.inference_results = self._get_or_run_inference(model_id)

        self.logger.info("Running Batch Evaluation on Dataset, using `batch_apply` metric")
        self.y_preds = []
        self.y_trues = []

        for row in self.inference_results:
            self.y_preds.append(row[INFERENCE_OUTPUT_FIELD])
            output_field = list(self.dataset_adapter.output_columns)[0]
            self.y_trues.append(row[OUTPUTS_FIELD][output_field])

        self.scores(model_id)

        return self.metric_adapter.batch_apply(self.y_preds, self.y_trues)

    def scores(self, model_id: str):
        """
        Runs evaluation on the dataset a row at a time and returns the eval results as a whole.
        :param model_id: The Model Id for which we want to evaluate against
        :return:
        """
        self.inference_results = self._get_or_run_inference(model_id)

        self.logger.info("Running Evaluation on Dataset, using `apply` metric")
        self.evaluation_results = []

        for row in self.inference_results:
            y_pred = row[INFERENCE_OUTPUT_FIELD]
            output_field = list(self.dataset_adapter.output_columns)[0]
            y_true = row[OUTPUTS_FIELD][output_field]
            row[EVALUATION_FIELD] = self.metric_adapter.apply(y_pred, y_true)
            self.evaluation_results.append(row)
        return self.evaluation_results

    def save(self, output_path: str):
        """
        Save results to a JSONL file.

        Args:
            output_path (str): Path where to save the JSONL file
        """
        output_file_path = Path(output_path)
        output_file_path.parent.mkdir(parents=True, exist_ok=True)

        # Determine which results to save
        if not self.evaluation_results:
            self.logger.warning(f"No results to save")
            return
        try:
            with output_file_path.open('w', encoding='utf-8') as f:
                for result in self.evaluation_results:
                    # Convert each result to JSON and write as a single line
                    json_line = json.dumps(result, ensure_ascii=False)
                    f.write(json_line + '\n')

            self.logger.info(f"Successfully saved evaluation results to {output_file_path}")

        except Exception as e:
            self.logger.error(f"Error saving results to {output_file_path}: {str(e)}")
            raise
