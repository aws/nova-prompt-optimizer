# Rate Limiting Analysis for Nova Prompt Optimization

## Overview

This document explains the dual rate limiting system in the Nova Prompt Optimizer and why users experience rate limit errors despite setting appropriate limits.

## Rate Limiting Architecture

### Dual Rate Limiter System

The Nova Prompt Optimizer implements **two independent rate limiters** that both use the same configuration value but operate on different API call streams:

#### 1. Frontend Rate Limiter (BedrockInferenceAdapter)
- **File**: `/src/amzn_nova_prompt_optimizer/core/inference/adapter.py`
- **Class**: `BedrockInferenceAdapter`
- **Purpose**: Controls evaluation phase API calls
- **Scope**: 
  - Baseline prompt evaluation
  - Optimized prompt evaluation
  - Custom metric evaluation calls
- **Implementation**: Uses `RateLimiter` utility class
- **Configuration**: `rate_limit` parameter from optimization config

#### 2. Backend Rate Limiter (RateLimitedLM)
- **File**: `/src/amzn_nova_prompt_optimizer/core/optimizers/miprov2/custom_lm/rate_limited_lm.py`
- **Class**: `RateLimitedLM`
- **Purpose**: Controls DSPy optimization phase API calls
- **Scope**:
  - Meta-prompter calls
  - Instruction generation
  - Few-shot demo selection
  - Prompt candidate testing
- **Implementation**: Wraps DSPy language models with rate limiting
- **Configuration**: Same `rate_limit` parameter from optimization config

## Rate Limiter Implementation Details

### RateLimiter Utility Class
**File**: `/src/amzn_nova_prompt_optimizer/util/rate_limiter.py`

```python
class RateLimiter:
    """
    Thread-safe rate limiter that controls the frequency of requests.
    """
    def __init__(self, rate_limit: int = 2):
        self.rate_limit = rate_limit  # requests per minute
        self.request_times = []
        self.lock = threading.Lock()
    
    def apply_rate_limiting(self):
        # Implements sliding window rate limiting
```

**Features**:
- Thread-safe implementation
- Sliding window algorithm
- Configurable requests per minute
- Automatic request spacing

### RateLimitedLM Wrapper
**File**: `/src/amzn_nova_prompt_optimizer/core/optimizers/miprov2/custom_lm/rate_limited_lm.py`

```python
class RateLimitedLM(dspy.LM):
    """
    A wrapper around DSPy language models that applies rate limiting.
    """
    def __init__(self, model: dspy.LM, rate_limit: int = 2):
        self.rate_limiter = RateLimiter(rate_limit=rate_limit)
        self.wrapped_model = model
    
    def __call__(self, *args, **kwargs):
        self.rate_limiter.apply_rate_limiting()
        return self.wrapped_model(*args, **kwargs)
```

**Features**:
- Wraps any DSPy language model
- Applies rate limiting before each call
- Maintains original model interface
- Used for both task and prompt models

## Rate Limit Configuration Flow

### Configuration Source
```python
# In sdk_worker.py
rate_limit_value = config.get('rate_limit', 2)
```

### Frontend Application
```python
# BedrockInferenceAdapter initialization
inference_adapter = BedrockInferenceAdapter(
    region_name="us-east-1", 
    rate_limit=rate_limit_value
)
```

### Backend Optimization
```python
# In miprov2_optimizer.py
task_lm = RateLimitedLM(
    dspy.LM(f'bedrock/{task_model_id}'), 
    rate_limit=self.inference_adapter.rate_limit
)
prompt_lm = RateLimitedLM(
    dspy.LM(f'bedrock/{prompter_model_id}'), 
    rate_limit=self.inference_adapter.rate_limit
)
```

## The Rate Limiting Problem

### Why Users Experience Rate Limit Errors

**Root Cause**: Both rate limiters operate **independently** and **simultaneously**, effectively doubling the actual API call rate.

**Example Scenario**:
- User sets rate limit: **20 RPM**
- Frontend rate limiter: **20 RPM** for evaluation calls
- Backend rate limiter: **20 RPM** for optimization calls
- **Actual combined rate**: Up to **40 RPM**

### Call Pattern Analysis

During optimization, both systems make calls concurrently:

```
Time: 0-30 seconds
├── Backend: Meta-prompting (2 calls at 20 RPM)
├── Backend: Instruction generation (5 calls at 20 RPM)
└── Backend: Demo selection (3 calls at 20 RPM)

Time: 30-60 seconds  
├── Backend: Candidate testing (15 calls at 20 RPM)
└── Frontend: Evaluation (2 calls at 20 RPM)

Total: ~27 calls in 60 seconds = 27 RPM (exceeds AWS limits)
```

### AWS Bedrock Rate Limits

**Nova Premier**:
- Default: 10-20 RPM (varies by region/account)
- Burst: Limited burst capacity

**Nova Lite**:
- Default: 50-100 RPM (higher limits)
- Better for development/testing

## Solutions and Recommendations

### 1. Reduce Configured Rate Limit

**Recommended Settings**:
```python
# For Nova Premier
rate_limit = 5  # Allows ~10 RPM combined

# For Nova Lite  
rate_limit = 15  # Allows ~30 RPM combined
```

### 2. Model Selection Strategy

**Development/Testing**:
- Use **Nova Lite** for higher rate limits
- Faster iteration and testing

**Production**:
- Use **Nova Premier** for best quality
- Set conservative rate limits (5-8 RPM)

### 3. Dataset Size Optimization

**Reduce API Calls**:
- Limit dataset to 3-5 records for testing
- Use batched evaluation (implemented)
- Consider record sampling for large datasets

### 4. Optimization Timing

**Sequential Processing**:
- Wait 2-3 minutes between optimization runs
- Allow rate limit windows to reset
- Monitor AWS CloudWatch for actual usage

## Rate Limiting Best Practices

### Configuration Guidelines

1. **Start Conservative**: Begin with 5 RPM and increase gradually
2. **Monitor Usage**: Check AWS CloudWatch metrics
3. **Account for Both Systems**: Remember the dual limiter architecture
4. **Test with Small Datasets**: Validate rate limits before scaling

### Debugging Rate Limit Issues

**Check Configuration**:
```bash
# Verify rate limit setting in logs
grep "Rate limit" optimization_logs.txt

# Look for rate limit debug messages
grep "DEBUG.*rate_limit" optimization_logs.txt
```

**Monitor API Calls**:
```bash
# Count Bedrock calls in logs
grep "bedrock" optimization_logs.txt | wc -l

# Check for throttling errors
grep "ThrottlingException\|Too many requests" optimization_logs.txt
```

### Error Patterns

**Common Rate Limit Errors**:
```
litellm.RateLimitError: BedrockException - {"message":"Too many requests, please wait before trying again."}
```

**Throttling Indicators**:
```
ClientError: ThrottlingException
HTTP 429 Too Many Requests
```

## Implementation Locations

### Rate Limit Usage Points

1. **SDK Worker** (`/frontend/sdk_worker.py`):
   - Lines 241-243: BedrockInferenceAdapter initialization
   - Lines 284-292: Rate limit configuration and logging

2. **MiPro Optimizer** (`/src/amzn_nova_prompt_optimizer/core/optimizers/miprov2/miprov2_optimizer.py`):
   - Lines 254, 256: Task and prompt model rate limiting
   - Lines 375, 377: Duplicate rate limiting setup

3. **Inference Adapter** (`/src/amzn_nova_prompt_optimizer/core/inference/adapter.py`):
   - Line 78: Rate limiting application before model calls
   - Line 56: Rate limiter initialization

4. **Rate Limited LM** (`/src/amzn_nova_prompt_optimizer/core/optimizers/miprov2/custom_lm/rate_limited_lm.py`):
   - Line 42: Rate limiting before wrapped model calls

## Future Improvements

### Potential Optimizations

1. **Unified Rate Limiter**: Single rate limiter for both systems
2. **Dynamic Rate Adjustment**: Adjust based on AWS response times
3. **Queue-based Processing**: Serialize API calls across systems
4. **Regional Rate Limits**: Different limits per AWS region
5. **Account-aware Limiting**: Adjust based on account quotas

### Monitoring Enhancements

1. **Real-time Rate Tracking**: Dashboard showing current API usage
2. **Predictive Throttling**: Slow down before hitting limits
3. **Automatic Backoff**: Exponential backoff on rate limit errors
4. **Usage Analytics**: Historical rate limit usage patterns

## Troubleshooting Guide

### Quick Fixes

1. **Immediate**: Reduce rate limit to 5 RPM
2. **Short-term**: Switch to Nova Lite model
3. **Long-term**: Implement batching optimizations

### Diagnostic Steps

1. Check current rate limit setting
2. Review recent optimization logs for throttling
3. Verify AWS account rate limits
4. Test with minimal dataset (2-3 records)
5. Monitor CloudWatch Bedrock metrics

### Configuration Examples

**Conservative (Recommended)**:
```json
{
  "model_mode": "lite",
  "rate_limit": 5,
  "record_limit": 5
}
```

**Aggressive (Advanced Users)**:
```json
{
  "model_mode": "premier", 
  "rate_limit": 10,
  "record_limit": 3
}
```

This dual rate limiting architecture explains why users experience unexpected rate limit errors and provides clear guidance for optimal configuration.
