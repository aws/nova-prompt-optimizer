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
from typing import Any, List


class MetricAdapter(ABC):
    @abstractmethod
    def apply(self, y_pred: Any, y_true: Any) -> float:
        """
        Apply the metric on a prediction and ground truth

        :param y_pred: The prediction
        :param y_true: The ground truth
        :return: The metric score
        """
        pass

    @abstractmethod
    def batch_apply(self, y_preds: List[Any], y_trues: List[Any]) -> float:
        """
        Apply the metric on a list of predictions and ground truths

        :param y_preds: The prediction
        :param y_trues: The ground truth
        :return: The metric score
        """
        pass
