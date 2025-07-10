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
import random
from abc import ABC, abstractmethod
from typing import Optional, Dict, Any, List

import boto3
import time
from botocore.exceptions import ClientError

from amzn_nova_prompt_optimizer.core.inference.bedrock_converse import BedrockConverseHandler
from amzn_nova_prompt_optimizer.util.rate_limiter import RateLimiter

logger = logging.getLogger(__name__)

class InferenceAdapter(ABC):
    def __init__(self, region: str, rate_limit: int = 2):
        self.region = region
        self.rate_limit = rate_limit

    @abstractmethod
    def call_model(self, model_id: str, system_prompt: str,
                   messages: List[Dict[str, str]],
                   inf_config: Dict[str, Any]) -> str:
        pass


class BedrockInferenceAdapter(InferenceAdapter):
    def __init__(self,
                 region_name: str = 'us-east-1',
                 profile_name: Optional[str] = None,
                 max_retries: int = 5,
                 rate_limit: int = 2,
                 initial_backoff: int = 1):
        """
        Initialize Bedrock Inference Adapter with AWS credentials

        Args:
            region_name: AWS region name
            profile_name: Optional. AWS credential profile name.
            max_retries: Maximum number of retries for API calls
            rate_limit: Max TPS of the bedrock call this adapter can make. Default to 2.
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
        self.rate_limiter.apply_rate_limiting()
        return self._call_model_with_retry(model_id, system_prompt, messages, inf_config)

    def _call_model_with_retry(self, model_id:str, system_prompt: str,
                               messages: List[Dict[str, str]], inf_config: Dict[str, Any]) -> str:
        retries = 0
        while retries < self.max_retries:
            try:
                return self.converse_client.call_model(model_id, system_prompt, messages, inf_config)
            except ClientError as e:
                if e.response['Error']['Code'] == 'ThrottlingException':
                    wait_time = self._calculate_backoff_time(retries)
                    logger.debug(f"Throttled. Retrying in {wait_time} seconds... (Attempt {retries + 1}/{self.max_retries})")
                    time.sleep(wait_time)
                    retries += 1
                elif e.response['Error']['Code'] == 'ModelErrorException':
                    wait_time = self._calculate_backoff_time(retries)
                    logger.debug(f"Encountered ModelErrorException, Retrying in {wait_time} seconds...(Attempt {retries + 1}/{self.max_retries})")
                    time.sleep(wait_time)
                    retries += 1
                elif e.response['Error']['Code'] == 'ServiceUnavailableException':
                    wait_time = self._calculate_backoff_time(retries)
                    logger.debug(f"Retryable exception: ServiceUnavailableException {model_id}. Retrying in {wait_time} seconds... (Attempt {retries + 1}/{self.max_retries})")
                    time.sleep(wait_time)
                    retries += 1
                else:
                    raise e
        raise Exception(f"Max retries ({self.max_retries}) exceeded for model call")

    def _calculate_backoff_time(self, retry_count):
        # Exponential backoff with jitter
        return self.initial_backoff * (2 ** retry_count) + random.uniform(0, 1)
