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
from abc import ABC, abstractmethod
from typing import Optional

from amzn_nova_prompt_optimizer.core.inference import InferenceAdapter
from amzn_nova_prompt_optimizer.core.input_adapters.dataset_adapter import DatasetAdapter
from amzn_nova_prompt_optimizer.core.input_adapters.prompt_adapter import PromptAdapter
from amzn_nova_prompt_optimizer.core.input_adapters.metric_adapter import MetricAdapter


class OptimizationAdapter(ABC):
    def __init__(self, prompt_adapter: PromptAdapter,
                 inference_adapter: Optional[InferenceAdapter] = None,
                 dataset_adapter: Optional[DatasetAdapter] = None,
                 metric_adapter: Optional[MetricAdapter] = None):
        """
        Initialize the adapter with input and output column specifications.

        :param prompt_adapter: The initial PromptAdapter
        :param dataset_adapter: The DatasetAdapter containing the dataset
        :param metric_adapter: The MetricAdapter for evaluation
        """
        self.prompt_adapter = prompt_adapter
        self.dataset_adapter = dataset_adapter
        self.metric_adapter = metric_adapter
        self.inference_adapter = inference_adapter

    @abstractmethod
    def optimize(self) -> PromptAdapter:
        """
        Optimize the prompt using the given dataset and metric.

        :return: An optimized PromptAdapter
        """
        pass
