import random
import time
import boto3
import logging

from amzn_nova_prompt_optimizer.core.inference.bedrock_converse import BedrockConverseHandler

from abc import ABC, abstractmethod
from typing import Optional, Dict, Any, List
from botocore.exceptions import ClientError

logger = logging.getLogger(__name__)

class InferenceAdapter(ABC):
    def __init__(self, region: str):
        self.region = region

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
                 rate_limit: float = 2,
                 initial_backoff: int = 1):
        """
        Initialize Bedrock Inference Adapter with AWS credentials

        Args:
            region_name: AWS region name
            max_retries: Maximum number of retries for API calls
        """
        super().__init__(region=region_name)
        self.initial_backoff = initial_backoff
        self.max_retries = max_retries

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
        self.aws_region = region_name
        self.rate_limit = rate_limit
        self.request_timestamps: list[float] = []
        self.waiting_requests_count = 0
        self.converse_client = BedrockConverseHandler(self.bedrock_client)

    def call_model(self, model_id: str, system_prompt: str,
                   messages: List[Dict[str, str]], inf_config: Dict[str, Any]) -> str:
        self._apply_rate_limiting()
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

    def _apply_rate_limiting(self):
        current_time = time.time()

        # Remove timestamps older than 1 second
        self.request_timestamps = [ts for ts in self.request_timestamps if current_time - ts < 1.0]

        # If we've reached the rate limit, sleep until we can make another request
        if len(self.request_timestamps) >= self.rate_limit:
            self.waiting_requests_count += 1
            sleep_time = (((self.waiting_requests_count/self.rate_limit) * 1.0) -
                          (current_time - self.request_timestamps[0]) + random.uniform(0, 1))
            if sleep_time > 0:
                time.sleep(sleep_time)

        self.waiting_requests_count -= 1
        if self.waiting_requests_count < 0:
            self.waiting_requests_count = 0

        # Add current timestamp to the list
        self.request_timestamps.append(time.time())
