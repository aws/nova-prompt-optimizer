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
Bedrock Inference Adapter

This module provides the BedrockInferenceAdapter for making inference calls
to Amazon Bedrock models using the Converse API.
"""

import logging
import random
import time
from typing import Optional, Dict, Any, List

import boto3
from botocore.exceptions import ClientError

from amzn_nova_prompt_optimizer.core.inference.adapter import InferenceAdapter
from amzn_nova_prompt_optimizer.core.inference.bedrock_converse import BedrockConverseHandler
from amzn_nova_prompt_optimizer.util.rate_limiter import RateLimiter

logger = logging.getLogger(__name__)


class BedrockInferenceAdapter(InferenceAdapter):
    """
    Inference adapter for Amazon Bedrock models.
    
    This adapter handles communication with Bedrock models using the Converse API,
    including automatic retry logic with exponential backoff and rate limiting.
    
    Attributes:
        region: AWS region name
        rate_limit: Maximum requests per second
        max_retries: Maximum number of retry attempts
        initial_backoff: Initial backoff time in seconds for retries
        bedrock_client: Boto3 Bedrock runtime client
        converse_client: Handler for Bedrock Converse API calls
        rate_limiter: Rate limiter instance
    """
    
    def __init__(self,
                 region_name: str = 'us-east-1',
                 profile_name: Optional[str] = None,
                 max_retries: int = 5,
                 rate_limit: int = 2,
                 initial_backoff: int = 1):
        """
        Initialize Bedrock Inference Adapter with AWS credentials.

        Args:
            region_name: AWS region name (default: 'us-east-1')
            profile_name: Optional AWS credential profile name
            max_retries: Maximum number of retries for API calls (default: 5)
            rate_limit: Max requests per second (default: 2)
            initial_backoff: Initial backoff time in seconds (default: 1)
        """
        super().__init__(region=region_name, rate_limit=rate_limit)
        self.initial_backoff = initial_backoff
        self.max_retries = max_retries
        self.rate_limiter = RateLimiter(rate_limit=self.rate_limit)

        # Initialize AWS session with provided credentials
        if profile_name:
            # Use AWS profile if specified
            session = boto3.Session(profile_name=profile_name)
        else:
            # Fall back to default credentials (environment variables or IAM role)
            session = boto3.Session()

        # Create Bedrock client
        self.bedrock_client = session.client(
            'bedrock-runtime',
            region_name=region_name
        )
        self.converse_client = BedrockConverseHandler(self.bedrock_client)

    def call_model(self, model_id: str, system_prompt: str,
                   messages: List[Dict[str, str]], inf_config: Dict[str, Any]) -> str:
        """
        Call a Bedrock model with rate limiting and retry logic.
        
        Args:
            model_id: Bedrock model identifier
            system_prompt: System prompt text
            messages: List of conversation messages
            inf_config: Inference configuration parameters
        
        Returns:
            Model response text
        
        Raises:
            Exception: If max retries exceeded or non-retryable error occurs
        """
        self.rate_limiter.apply_rate_limiting()
        return self._call_model_with_retry(model_id, system_prompt, messages, inf_config)

    def _call_model_with_retry(self, model_id: str, system_prompt: str,
                               messages: List[Dict[str, str]], inf_config: Dict[str, Any]) -> str:
        """
        Call model with automatic retry logic for transient errors.
        
        Retries on:
        - ThrottlingException
        - ModelErrorException
        - ServiceUnavailableException
        
        Args:
            model_id: Bedrock model identifier
            system_prompt: System prompt text
            messages: List of conversation messages
            inf_config: Inference configuration parameters
        
        Returns:
            Model response text
        
        Raises:
            ClientError: For non-retryable errors
            Exception: If max retries exceeded
        """
        retries = 0
        while retries < self.max_retries:
            try:
                return self.converse_client.call_model(model_id, system_prompt, messages, inf_config)
            except ClientError as e:
                error_code = e.response['Error']['Code']
                
                if error_code == 'ThrottlingException':
                    wait_time = self._calculate_backoff_time(retries)
                    logger.debug(
                        f"Throttled. Retrying in {wait_time} seconds... "
                        f"(Attempt {retries + 1}/{self.max_retries})"
                    )
                    time.sleep(wait_time)
                    retries += 1
                elif error_code == 'ModelErrorException':
                    wait_time = self._calculate_backoff_time(retries)
                    logger.debug(
                        f"Encountered ModelErrorException, Retrying in {wait_time} seconds... "
                        f"(Attempt {retries + 1}/{self.max_retries})"
                    )
                    time.sleep(wait_time)
                    retries += 1
                elif error_code == 'ServiceUnavailableException':
                    wait_time = self._calculate_backoff_time(retries)
                    logger.debug(
                        f"Retryable exception: ServiceUnavailableException {model_id}. "
                        f"Retrying in {wait_time} seconds... (Attempt {retries + 1}/{self.max_retries})"
                    )
                    time.sleep(wait_time)
                    retries += 1
                else:
                    # Non-retryable error
                    raise e
        
        raise Exception(f"Max retries ({self.max_retries}) exceeded for model call")

    def _calculate_backoff_time(self, retry_count: int) -> float:
        """
        Calculate exponential backoff time with jitter.
        
        Args:
            retry_count: Current retry attempt number
        
        Returns:
            Wait time in seconds
        """
        # Exponential backoff with jitter
        return self.initial_backoff * (2 ** retry_count) + random.uniform(0, 1)
