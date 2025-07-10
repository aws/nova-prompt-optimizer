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
import dspy  # type: ignore

from amzn_nova_prompt_optimizer.util.rate_limiter import RateLimiter


class RateLimitedLM(dspy.LM):
    """
    A wrapper around DSPy language models that applies rate limiting.
    
    This class wraps any DSPy LM instance and applies rate limiting before
    each model call to prevent API rate limit violations. It maintains the
    same interface as the wrapped model while adding rate limiting functionality.
    
    Attributes:
        rate_limiter (RateLimiter): The rate limiter instance
        wrapped_model (dspy.LM): The underlying DSPy language model
    """

    def __init__(self, model: dspy.LM, rate_limit: int = 2, *args, **kwargs):
        # Initialize rate limiter with specified limit
        self.rate_limiter = RateLimiter(rate_limit=rate_limit)
        # Store the wrapped model for delegation.
        self.wrapped_model = model

    def __call__(self, *args, **kwargs):
        # Apply rate limiting before making the actual model call
        self.rate_limiter.apply_rate_limiting()
        # Delegate to the wrapped model
        return self.wrapped_model(*args, **kwargs)

    def __getattr__(self, name):
        # Delegate attribute access to the wrapped model to make it act like origin dspy.LM
        return getattr(self.wrapped_model, name)
