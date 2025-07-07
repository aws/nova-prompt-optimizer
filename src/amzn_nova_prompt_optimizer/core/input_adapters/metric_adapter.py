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
