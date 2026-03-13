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
SageMaker Inference Adapter

This module provides an InferenceAdapter implementation for calling
LLMs deployed on AWS SageMaker endpoints.
"""

import json
import logging
import random
import time
from typing import Any, Dict, List, Optional

import boto3
from botocore.exceptions import ClientError

from amzn_nova_prompt_optimizer.core.inference.adapter import InferenceAdapter
from amzn_nova_prompt_optimizer.util.rate_limiter import RateLimiter

logger = logging.getLogger(__name__)


class SageMakerInferenceAdapter(InferenceAdapter):
    """
    SageMaker inference adapter for calling SageMaker endpoints.
    
    This adapter supports calling LLMs deployed on SageMaker endpoints,
    with automatic DSPy compatibility through the to_dspy_lm() method.
    """
    
    def __init__(
        self,
        endpoint_name: str,
        region_name: str = 'us-east-1',
        profile_name: Optional[str] = None,
        max_retries: int = 5,
        rate_limit: int = 2,
        initial_backoff: int = 1,
        content_type: str = "application/json",
        accept: str = "application/json"
    ):
        """
        Initialize SageMaker inference adapter.
        
        Args:
            endpoint_name: Name of the SageMaker endpoint
            region_name: AWS region name
            profile_name: Optional AWS profile name
            max_retries: Maximum number of retries
            rate_limit: Max TPS for endpoint calls
            initial_backoff: Initial backoff time for retries
            content_type: Content type for requests
            accept: Accept type for responses
        """
        super().__init__(region=region_name, rate_limit=rate_limit)
        self.endpoint_name = endpoint_name
        self.profile_name = profile_name
        self.max_retries = max_retries
        self.initial_backoff = initial_backoff
        self.content_type = content_type
        self.accept = accept
        
        # Initialize rate limiter
        self.rate_limiter = RateLimiter(rate_limit=self.rate_limit)
        
        # Initialize SageMaker client
        if profile_name:
            session = boto3.Session(profile_name=profile_name)
        else:
            session = boto3.Session()
        
        self.sagemaker_runtime = session.client(
            'sagemaker-runtime',
            region_name=region_name
        )
        
        logger.info(f"Initialized SageMaker adapter for endpoint: {endpoint_name}")
    
    def test_connection(self) -> bool:
        """
        Test if the SageMaker endpoint is accessible and responding.
        
        Returns:
            True if endpoint is accessible, False otherwise
        """
        try:
            # Try a simple test payload with 'messages' format
            # Parameters should be at root level, not nested
            test_payload = {
                "messages": [{"role": "user", "content": "Test"}],
                "max_tokens": 10,
                "temperature": 0.0
            }
            
            logger.info(f"Testing connection to endpoint: {self.endpoint_name}")
            response = self.sagemaker_runtime.invoke_endpoint(
                EndpointName=self.endpoint_name,
                ContentType=self.content_type,
                Accept=self.accept,
                Body=json.dumps(test_payload)
            )
            
            logger.info(f"✓ Endpoint {self.endpoint_name} is accessible")
            return True
            
        except ClientError as e:
            error_code = e.response['Error']['Code']
            error_message = e.response['Error'].get('Message', 'No message')
            logger.error(
                f"✗ Endpoint {self.endpoint_name} error: {error_code} - {error_message}"
            )
            return False
        except Exception as e:
            logger.error(
                f"✗ Endpoint {self.endpoint_name} error: {type(e).__name__}: {str(e)}"
            )
            return False
    
    def call_model(
        self, 
        model_id: str, 
        system_prompt: str,
        messages: List[Dict[str, str]],
        inf_config: Dict[str, Any]
    ) -> str:
        """
        Call SageMaker endpoint with the given parameters.
        
        Args:
            model_id: Model identifier (can be used for routing if needed)
            system_prompt: System prompt string
            messages: List of conversation messages
            inf_config: Inference configuration
        
        Returns:
            Model response as string
        """
        self.rate_limiter.apply_rate_limiting()
        return self._call_model_with_retry(
            model_id, system_prompt, messages, inf_config
        )
    
    def _call_model_with_retry(
        self,
        model_id: str,
        system_prompt: str,
        messages: List[Dict[str, str]],
        inf_config: Dict[str, Any]
    ) -> str:
        """
        Call SageMaker endpoint with retry logic.
        
        Args:
            model_id: Model identifier
            system_prompt: System prompt
            messages: Conversation messages
            inf_config: Inference config
        
        Returns:
            Model response
        """
        retries = 0
        last_error = None
        
        while retries < self.max_retries:
            try:
                # Format the payload for SageMaker endpoint
                payload = self._format_payload(
                    system_prompt, messages, inf_config
                )
                
                logger.debug(f"Calling SageMaker endpoint: {self.endpoint_name}")
                
                # Call SageMaker endpoint
                response = self.sagemaker_runtime.invoke_endpoint(
                    EndpointName=self.endpoint_name,
                    ContentType=self.content_type,
                    Accept=self.accept,
                    Body=json.dumps(payload)
                )
                
                # Parse response
                result = json.loads(response['Body'].read().decode())
                return self._extract_text_from_response(result)
                
            except ClientError as e:
                error_code = e.response['Error']['Code']
                error_message = e.response['Error'].get('Message', 'No message')
                last_error = e
                
                logger.warning(
                    f"SageMaker ClientError: {error_code} - {error_message}"
                )
                
                if error_code in ['ThrottlingException', 'ModelError', 'ServiceUnavailable']:
                    wait_time = self._calculate_backoff_time(retries)
                    logger.debug(
                        f"Retryable error: {error_code}. "
                        f"Retrying in {wait_time}s... "
                        f"(Attempt {retries + 1}/{self.max_retries})"
                    )
                    time.sleep(wait_time)
                    retries += 1
                else:
                    # Non-retryable error
                    logger.error(
                        f"Non-retryable SageMaker error: {error_code} - {error_message}"
                    )
                    raise e
                    
            except Exception as e:
                # Catch all other exceptions (JSON decode errors, etc.)
                last_error = e
                logger.warning(
                    f"SageMaker error (attempt {retries + 1}/{self.max_retries}): "
                    f"{type(e).__name__}: {str(e)}"
                )
                wait_time = self._calculate_backoff_time(retries)
                time.sleep(wait_time)
                retries += 1
        
        # Max retries exceeded - provide detailed error
        error_msg = (
            f"Max retries ({self.max_retries}) exceeded for SageMaker endpoint '{self.endpoint_name}'. "
            f"Last error: {type(last_error).__name__}: {str(last_error)}"
        )
        logger.error(error_msg)
        raise Exception(error_msg)
    
    def _format_payload(
        self,
        system_prompt: str,
        messages: List[Dict[str, str]],
        inf_config: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Format the payload for SageMaker endpoint.
        
        Different SageMaker endpoints may expect different formats.
        This implementation uses the OpenAI-compatible format with 'messages'
        and parameters at the root level.
        Override this method for custom endpoint formats.
        
        Args:
            system_prompt: System prompt
            messages: Conversation messages
            inf_config: Inference config
        
        Returns:
            Payload dict for SageMaker endpoint
        """
        # Build chat messages in OpenAI format
        chat_messages = []
        
        if system_prompt:
            chat_messages.append({
                "role": "system",
                "content": system_prompt
            })
        
        for msg in messages:
            if "user" in msg:
                chat_messages.append({
                    "role": "user",
                    "content": msg["user"]
                })
            elif "assistant" in msg:
                chat_messages.append({
                    "role": "assistant",
                    "content": msg["assistant"]
                })
        
        # OpenAI-compatible format: parameters at root level
        # Use max_tokens instead of max_new_tokens for compatibility
        payload = {
            "messages": chat_messages,
            "max_tokens": inf_config.get("max_new_tokens", inf_config.get("max_tokens", 5000)),
            "temperature": inf_config.get("temperature", 0.0),
            "top_p": inf_config.get("top_p", 1.0),
            "top_k": inf_config.get("top_k", 1)
        }
        
        return payload
    
    def _extract_text_from_response(self, response: Dict[str, Any]) -> str:
        """
        Extract text from SageMaker endpoint response.
        
        Different endpoints return different response formats.
        This handles common formats including OpenAI-compatible responses.
        Override for custom formats.
        
        Args:
            response: Response dict from SageMaker
        
        Returns:
            Extracted text
        """
        # OpenAI-compatible format: {"choices": [{"message": {"content": "..."}}]}
        if "choices" in response and len(response["choices"]) > 0:
            choice = response["choices"][0]
            if "message" in choice and "content" in choice["message"]:
                return choice["message"]["content"]
            elif "text" in choice:
                return choice["text"]
        
        # Common response formats
        if isinstance(response, list) and len(response) > 0:
            # Format: [{"generated_text": "..."}]
            if "generated_text" in response[0]:
                return response[0]["generated_text"]
        
        if "generated_text" in response:
            # Format: {"generated_text": "..."}
            return response["generated_text"]
        
        if "outputs" in response:
            # Format: {"outputs": "..."}
            return response["outputs"]
        
        if isinstance(response, str):
            # Format: "..."
            return response
        
        # Fallback: return JSON string
        logger.warning(
            f"Unknown SageMaker response format. Returning JSON string."
        )
        return json.dumps(response)
    
    def _calculate_backoff_time(self, retry_count: int) -> float:
        """Calculate exponential backoff time with jitter."""
        return self.initial_backoff * (2 ** retry_count) + random.uniform(0, 1)
    
    def to_dspy_lm(self, model_id: str, **kwargs):
        """
        Create a DSPy-compatible wrapper for this adapter.
        
        For SageMaker, we override the model_id to use the endpoint_name
        since SageMaker endpoints don't use traditional model IDs.
        
        Args:
            model_id: Model identifier (ignored for SageMaker, endpoint_name is used instead)
            **kwargs: Additional parameters for the DSPy adapter
        
        Returns:
            DSPy-compatible adapter instance with endpoint_name as model_id
        
        Example:
            >>> adapter = SageMakerInferenceAdapter(endpoint_name="my-endpoint")
            >>> # task_model_id is ignored, endpoint_name is used instead
            >>> dspy_lm = adapter.to_dspy_lm("any-model-id")
            >>> import dspy
            >>> dspy.configure(lm=dspy_lm)
        """
        from amzn_nova_prompt_optimizer.core.inference.dspy_compatible import (
            create_dspy_adapter
        )
        # Override model_id with endpoint_name for SageMaker
        logger.info(
            f"SageMaker adapter: Using endpoint_name '{self.endpoint_name}' "
            f"as model_id (provided model_id '{model_id}' is ignored)"
        )
        return create_dspy_adapter(self, self.endpoint_name, **kwargs)
