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
import threading

import time


class RateLimiter:
    """
    Thread-safe rate limiter that controls the frequency of requests.
    """

    def __init__(self, rate_limit: int = 2):
        self.rate_limit = rate_limit
        self.logger = logging.getLogger(__name__)
        self.request_timestamps: list[float] = []  # Track request timestamps in sliding window
        self.waiting_requests_count = 0  # Count of requests waiting for rate limit
        self._lock = threading.Lock()  # Thread safety lock

    def apply_rate_limiting(self):
        if self.rate_limit <= 0:
            # Disable rate limit when rate_limit <=0
            return

        with self._lock:  # Ensure thread safety for all shared state access
            current_time = time.time()

            # Clean up old timestamps - only keep requests from the last 1 second
            self.request_timestamps = [ts for ts in self.request_timestamps if current_time - ts < 1.0]

            # Check if we've exceeded the rate limit
            if len(self.request_timestamps) >= self.rate_limit:
                self.waiting_requests_count += 1

                # Calculate sleep time with exponential backoff and jitter
                # Formula accounts for: queue position, time window, and randomization
                sleep_time = (((self.waiting_requests_count / self.rate_limit) * 1.0) -
                              (current_time - self.request_timestamps[0]) + random.uniform(0, 1))

                if sleep_time > 0:
                    self.logger.debug(f"Exceed rate limit, retry in {sleep_time} seconds...")
                    time.sleep(sleep_time)

            # Decrement waiting count and ensure it doesn't go negative
            self.waiting_requests_count -= 1
            if self.waiting_requests_count < 0:
                self.waiting_requests_count = 0

            # Record this request's timestamp
            self.request_timestamps.append(time.time())
