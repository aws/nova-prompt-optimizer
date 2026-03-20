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

"""
Base Inference Adapter

This module provides the abstract base class for all inference adapters.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, List


class InferenceAdapter(ABC):
    """
    Abstract base class for inference adapters.

    All inference adapters must inherit from this class and implement
    the call_model method. This provides a consistent interface for
    making inference calls across different backends (Bedrock, SageMaker, etc.).

    Attributes:
        region: AWS region or endpoint region
        rate_limit: Maximum requests per second
    """

    def __init__(self, region: str, rate_limit: int = 2):
        """
        Initialize the inference adapter.

        Args:
            region: AWS region or endpoint region
            rate_limit: Maximum requests per second (default: 2)
        """
        self.region = region
        self.rate_limit = rate_limit

    @abstractmethod
    def call_model(self, model_id: str, system_prompt: str,
                   messages: List[Dict[str, str]],
                   inf_config: Dict[str, Any]) -> str:
        """
        Call the model for inference.

        This method must be implemented by all subclasses.

        Args:
            model_id: Model identifier
            system_prompt: System prompt text
            messages: List of conversation messages in format:
                     [{"user": "..."}, {"assistant": "..."}, ...]
            inf_config: Inference configuration parameters

        Returns:
            Model response text

        Raises:
            NotImplementedError: If not implemented by subclass
        """
        pass

    def to_dspy_lm(self, model_id: str, **kwargs):
        """
        Create a DSPy-compatible wrapper for this adapter.

        This is a convenience method that automatically creates the
        appropriate DSPy-compatible adapter based on the adapter type.

        Args:
            model_id: Model identifier to use
            **kwargs: Additional parameters for the DSPy adapter

        Returns:
            DSPy-compatible adapter instance

        Example:
            >>> adapter = BedrockInferenceAdapter(region_name="us-east-1")
            >>> dspy_lm = adapter.to_dspy_lm("us.amazon.nova-pro-v1:0")
            >>> import dspy
            >>> dspy.configure(lm=dspy_lm)
        """
        from amzn_nova_prompt_optimizer.core.inference.dspy_compatible import (
            create_dspy_adapter
        )
        return create_dspy_adapter(self, model_id, **kwargs)


__all__ = ['InferenceAdapter']
