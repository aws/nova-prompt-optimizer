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
DSPy-Compatible Inference Adapter

This module provides the bridge between DSPy's LM interface and the
InferenceAdapter interface used throughout the Nova Prompt Optimizer.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional
import logging

logger = logging.getLogger(__name__)


class DSPyCompatibleInferenceAdapter(ABC):
    """
    Abstract base class that makes any InferenceAdapter compatible with DSPy's LM interface.
    
    This adapter acts as a bridge between DSPy's expected interface and the
    InferenceAdapter interface used throughout the Nova Prompt Optimizer.
    
    Attributes:
        inference_adapter: The underlying InferenceAdapter instance
        model_id: The model identifier to use for inference
        history: List of previous calls (required by DSPy)
        cache: Whether to cache responses (required by DSPy)
        kwargs: Additional model-specific kwargs (required by DSPy)
    """
    
    def __init__(
        self,
        inference_adapter: 'InferenceAdapter',
        model_id: str,
        cache: bool = False,
        **kwargs
    ):
        """
        Initialize the DSPy-compatible adapter.
        
        Args:
            inference_adapter: The InferenceAdapter instance to wrap
            model_id: The model identifier for inference
            cache: Whether to enable response caching
            **kwargs: Additional model-specific parameters
        """
        self.inference_adapter = inference_adapter
        self.model_id = model_id
        self.history = []  # Required by DSPy for tracking calls
        self.cache = cache
        
        # Initialize kwargs with defaults that DSPy expects
        self.kwargs = {
            'temperature': 1.0,
            'max_tokens': 1000,
            'top_p': 1.0,
            **kwargs  # User-provided kwargs override defaults
        }
        self.model = model_id  # Alias for DSPy compatibility
        
    def __call__(self, messages: List[Dict[str, str]], **lm_kwargs) -> List[str]:
        """
        Main interface method called by DSPy.
        
        Args:
            messages: List of message dicts in DSPy format:
                     [{"role": "system", "content": "..."},
                      {"role": "user", "content": "..."},
                      {"role": "assistant", "content": "..."}]
            **lm_kwargs: Additional parameters (temperature, max_tokens, etc.)
        
        Returns:
            List of completion strings (DSPy expects list for n>1 generations)
        """
        # Convert DSPy format to InferenceAdapter format
        system_prompt, conversation_messages = self._convert_messages_to_adapter_format(messages)
        
        # Build inference config
        inf_config = self._build_inference_config(lm_kwargs)
        
        # Call the underlying inference adapter
        try:
            response = self.inference_adapter.call_model(
                model_id=self.model_id,
                system_prompt=system_prompt,
                messages=conversation_messages,
                inf_config=inf_config
            )
            
            # Track in history (DSPy requirement)
            self.history.append({
                "messages": messages,
                "kwargs": lm_kwargs,
                "response": response
            })
            
            # Return as list (DSPy expects list for multiple generations)
            return [response]
            
        except Exception as e:
            logger.error(f"Error calling inference adapter: {e}")
            raise
    
    async def acall(self, messages: List[Dict[str, str]], **lm_kwargs) -> List[str]:
        """
        Async version of __call__.
        
        Args:
            messages: List of message dicts in DSPy format
            **lm_kwargs: Additional parameters
        
        Returns:
            List of completion strings
        """
        # For now, delegate to synchronous version
        # Can be overridden by subclasses for true async support
        return self.__call__(messages, **lm_kwargs)
    
    def _convert_messages_to_adapter_format(
        self, 
        messages: List[Dict[str, str]]
    ) -> tuple:
        """
        Convert DSPy message format to InferenceAdapter format.
        
        DSPy format:
            [{"role": "system", "content": "..."},
             {"role": "user", "content": "..."},
             {"role": "assistant", "content": "..."}]
        
        InferenceAdapter format:
            system_prompt: str
            messages: [{"user": "..."}, {"assistant": "..."}, ...]
        
        Args:
            messages: Messages in DSPy format
        
        Returns:
            Tuple of (system_prompt, conversation_messages)
        """
        system_prompt = ""
        conversation_messages = []
        
        for msg in messages:
            role = msg.get("role", "")
            content = msg.get("content", "")
            
            if role == "system":
                # Accumulate system prompts (there might be multiple)
                if system_prompt:
                    system_prompt += "\n\n" + content
                else:
                    system_prompt = content
            elif role == "user":
                conversation_messages.append({"user": content})
            elif role == "assistant":
                conversation_messages.append({"assistant": content})
            else:
                logger.warning(f"Unknown message role: {role}")
        
        return system_prompt, conversation_messages
    
    @abstractmethod
    def _build_inference_config(self, lm_kwargs: Dict[str, Any]) -> Dict[str, Any]:
        """
        Build inference config from DSPy kwargs.
        
        This method should be implemented by subclasses to handle
        backend-specific parameter mapping.
        
        Args:
            lm_kwargs: Kwargs from DSPy (temperature, max_tokens, etc.)
        
        Returns:
            Inference config dict for the specific backend
        """
        pass
    
    def copy(self, **kwargs):
        """
        Create a copy of this adapter with updated parameters.
        Required by some DSPy optimizers.
        
        Args:
            **kwargs: Parameters to update
        
        Returns:
            New instance with updated parameters
        """
        # Extract special parameters
        model_id = kwargs.pop('model_id', self.model_id)
        cache = kwargs.pop('cache', self.cache)
        
        # Merge remaining kwargs
        new_kwargs = {**self.kwargs, **kwargs}
        
        return self.__class__(
            inference_adapter=self.inference_adapter,
            model_id=model_id,
            cache=cache,
            **new_kwargs
        )
    
    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(model_id={self.model_id})"


class DSPyBedrockAdapter(DSPyCompatibleInferenceAdapter):
    """
    DSPy-compatible adapter for Bedrock inference.
    
    This adapter wraps BedrockInferenceAdapter to make it compatible
    with DSPy's LM interface.
    """
    
    def _build_inference_config(self, lm_kwargs: Dict[str, Any]) -> Dict[str, Any]:
        """
        Build Bedrock-specific inference config.
        
        Maps DSPy parameters to Bedrock Converse API parameters.
        Merges call-time kwargs with initialization kwargs (self.kwargs).
        
        Args:
            lm_kwargs: DSPy kwargs passed at call time
        
        Returns:
            Bedrock inference config
        """
        from amzn_nova_prompt_optimizer.core.inference import (
            MAX_TOKENS_FIELD, TEMPERATURE_FIELD, TOP_P_FIELD, TOP_K_FIELD
        )
        
        # Merge self.kwargs (defaults) with lm_kwargs (call-time overrides)
        merged_kwargs = {**self.kwargs, **lm_kwargs}
        
        return {
            MAX_TOKENS_FIELD: merged_kwargs.get("max_tokens", 5000),
            TEMPERATURE_FIELD: merged_kwargs.get("temperature", 0.0),
            TOP_P_FIELD: merged_kwargs.get("top_p", 1.0),
            TOP_K_FIELD: merged_kwargs.get("top_k", 1)
        }


class DSPySageMakerAdapter(DSPyCompatibleInferenceAdapter):
    """
    DSPy-compatible adapter for SageMaker inference.
    
    This adapter wraps SageMakerInferenceAdapter to make it compatible
    with DSPy's LM interface.
    """
    
    def _build_inference_config(self, lm_kwargs: Dict[str, Any]) -> Dict[str, Any]:
        """
        Build SageMaker-specific inference config.
        
        Maps DSPy parameters to SageMaker endpoint parameters.
        Different SageMaker endpoints may expect different formats.
        Merges call-time kwargs with initialization kwargs (self.kwargs).
        
        Args:
            lm_kwargs: DSPy kwargs passed at call time
        
        Returns:
            SageMaker inference config
        """
        # Merge self.kwargs (defaults) with lm_kwargs (call-time overrides)
        merged_kwargs = {**self.kwargs, **lm_kwargs}
        
        # SageMaker endpoints often use different parameter names
        # This is a common format, but may need customization
        temperature = merged_kwargs.get("temperature", 0.0)
        
        return {
            "max_new_tokens": merged_kwargs.get("max_tokens", 5000),
            "temperature": temperature,
            "top_p": merged_kwargs.get("top_p", 1.0),
            "top_k": merged_kwargs.get("top_k", 1),
            # Additional SageMaker-specific parameters
            "do_sample": temperature > 0,
            "return_full_text": False
        }


def create_dspy_adapter(
    inference_adapter: 'InferenceAdapter',
    model_id: str,
    **kwargs
) -> DSPyCompatibleInferenceAdapter:
    """
    Factory function to create the appropriate DSPy-compatible adapter.
    
    Automatically detects the type of InferenceAdapter and returns
    the corresponding DSPy-compatible wrapper.
    
    Args:
        inference_adapter: The InferenceAdapter instance
        model_id: Model identifier
        **kwargs: Additional parameters
    
    Returns:
        Appropriate DSPyCompatibleInferenceAdapter instance
    
    Example:
        >>> bedrock_adapter = BedrockInferenceAdapter(region_name="us-east-1")
        >>> dspy_lm = create_dspy_adapter(bedrock_adapter, "us.amazon.nova-pro-v1:0")
        >>> dspy.configure(lm=dspy_lm)
    """
    adapter_type = type(inference_adapter).__name__
    
    if "Bedrock" in adapter_type:
        return DSPyBedrockAdapter(inference_adapter, model_id, **kwargs)
    elif "SageMaker" in adapter_type:
        return DSPySageMakerAdapter(inference_adapter, model_id, **kwargs)
    else:
        # Default to Bedrock-style config for unknown adapters
        logger.warning(
            f"Unknown adapter type: {adapter_type}. "
            f"Using DSPyBedrockAdapter as default."
        )
        return DSPyBedrockAdapter(inference_adapter, model_id, **kwargs)
