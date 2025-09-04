# Bedrock API Calls Analysis for Nova Prompt Optimization

## Overview

This document traces all Amazon Bedrock API calls that occur during a Nova prompt optimization job, using a 5-record dataset as an example.

## Optimization Flow and Bedrock Calls

### Phase 1: Optimization Process (Nova SDK)

#### 1. Meta-Prompter Calls
- **File**: `/src/amzn_nova_prompt_optimizer/core/optimizers/nova_meta_prompter/nova_prompt_template.py`
- **Purpose**: Convert user prompt into structured system/user prompts
- **Bedrock Calls**: 1-2 calls
- **Model**: Nova Premier (as selected)
- **Template Used**: "You are tasked with translating the Original Prompt into a..."

#### 2. Instruction Generation
- **File**: `/src/amzn_nova_prompt_optimizer/core/optimizers/nova_prompt_optimizer/nova_grounded_proposer.py`
- **Purpose**: Generate optimized instruction candidates using tips (like "high_stakes")
- **Bedrock Calls**: 3-5 calls per instruction candidate
- **Model**: Nova Premier
- **Why**: Creates multiple prompt variations to test
- **Tips Used**: From `NOVA_TIPS` dictionary (high_stakes, creative, simple, etc.)

#### 3. Few-shot Demo Selection
- **File**: `/.venv/lib/python3.13/site-packages/dspy/propose/grounded_proposer.py`
- **Purpose**: Select best examples from your 5 records to include in prompts
- **Bedrock Calls**: 2-3 calls to evaluate which examples work best
- **Model**: Nova Premier

#### 4. Prompt Candidate Testing
- **File**: MiPro optimizer (DSPy)
- **Purpose**: Test each prompt candidate against your dataset
- **Bedrock Calls**: ~10-15 calls (3-5 prompt candidates × 5 records each)
- **Model**: Nova Premier
- **Why**: Evaluate performance of each optimized prompt

### Phase 2: Evaluation Process (SDK Worker)

#### 5. Baseline Evaluation
- **File**: `/frontend/sdk_worker.py` (line 308)
- **Purpose**: Test original prompt against dataset
- **Bedrock Calls**: 5 calls (1 per record) - **ORIGINAL**
- **Bedrock Calls**: 1 call (all records batched) - **OPTIMIZED**
- **Model**: Nova Premier
- **Code**: `baseline_evaluator.aggregate_score()`
- **API**: Uses `BedrockInferenceAdapter.call_model()`

#### 6. Optimized Evaluation
- **File**: `/frontend/sdk_worker.py` (line 312)
- **Purpose**: Test best optimized prompt against dataset
- **Bedrock Calls**: 5 calls (1 per record) - **ORIGINAL**
- **Bedrock Calls**: 1 call (all records batched) - **OPTIMIZED**
- **Model**: Nova Premier
- **Code**: `optimized_evaluator.aggregate_score()`
- **API**: Uses `BedrockInferenceAdapter.call_model()`

## Bedrock API Call Locations

### Direct Bedrock Clients

1. **BedrockInferenceAdapter** (`/src/amzn_nova_prompt_optimizer/core/inference/adapter.py`)
   - **Line 70-73**: Creates `bedrock-runtime` client
   - **Line 76-79**: `call_model()` method (main entry point)
   - **Line 86**: Calls `converse_client.call_model()`

2. **BedrockConverseHandler** (`/src/amzn_nova_prompt_optimizer/core/inference/bedrock_converse.py`)
   - **Line 48-54**: `client.converse()` call with system prompt
   - **Line 56-62**: `client.converse()` call without system prompt

3. **MetricService** (`/frontend/metric_service.py`)
   - **Line 15**: Creates `bedrock-runtime` client
   - **Line 36**: `bedrock.invoke_model()` call for metric generation

4. **BatchedEvaluator** (`/frontend/batched_evaluator.py`) - **NEW**
   - **Purpose**: Reduce evaluation API calls by batching multiple records
   - **Method**: Combines all dataset records into single prompt
   - **Fallback**: Reverts to individual calls if batching fails

5. **Rate-limited calls through DSPy/LiteLLM** (indirect)
   - DSPy uses LiteLLM which calls Bedrock for optimization prompts
   - Includes meta-prompter template calls

## Total Estimated Bedrock Calls

For a 5-record dataset optimization:

### Original Implementation
| Phase | Calls | Purpose |
|-------|-------|---------|
| Meta-prompting | 1-2 | Restructure user prompt |
| Instruction generation | 3-5 | Create prompt candidates |
| Demo selection | 2-3 | Select best examples |
| Candidate testing | 10-15 | Test prompt variations |
| Baseline evaluation | 5 | Test original prompt |
| Optimized evaluation | 5 | Test best prompt |
| **Total** | **26-35** | **Complete optimization** |

### Optimized Implementation (With Batching)
| Phase | Calls | Purpose | Improvement |
|-------|-------|---------|-------------|
| Meta-prompting | 1-2 | Restructure user prompt | No change |
| Instruction generation | 3-5 | Create prompt candidates | No change |
| Demo selection | 2-3 | Select best examples | No change |
| Candidate testing | 10-15 | Test prompt variations | No change |
| Baseline evaluation | 1 | Test original prompt (batched) | **-4 calls** |
| Optimized evaluation | 1 | Test best prompt (batched) | **-4 calls** |
| **Total** | **18-27** | **Complete optimization** | **-8 calls (23% reduction)** |

## Rate Limiting Analysis

### Why Rate Limiting Occurs

With a 20 RPM limit and ~30 calls happening rapidly:

1. **Burst Pattern**: Calls happen in concentrated bursts during:
   - Instruction generation (5-10 calls quickly)
   - Candidate testing (10-15 calls quickly)
   - Final evaluation (10 calls quickly)

2. **Rate Limit Exceeded**: 30 calls in ~2-3 minutes exceeds 20 RPM

### Solutions

1. **Lower Rate Limit**: Set to 5-10 RPM to spread calls over time
2. **Use Nova Lite**: Higher rate limits than Premier
3. **Reduce Dataset Size**: Fewer records = fewer evaluation calls
4. **Wait Between Runs**: Allow rate limits to reset
5. **Batched Evaluation**: **NEW** - Reduces evaluation calls by 80%

## Call Flow Diagram

### Original Flow
```
User Starts Optimization
    ↓
Meta-Prompter (1-2 calls)
    ↓
Instruction Generation (3-5 calls)
    ↓
Demo Selection (2-3 calls)
    ↓
Candidate Testing (10-15 calls)
    ↓
Baseline Evaluation (5 calls)
    ↓
Optimized Evaluation (5 calls)
    ↓
Results Displayed
```

### Optimized Flow (With Batching)
```
User Starts Optimization
    ↓
Meta-Prompter (1-2 calls)
    ↓
Instruction Generation (3-5 calls)
    ↓
Demo Selection (2-3 calls)
    ↓
Candidate Testing (10-15 calls)
    ↓
Baseline Evaluation (1 batched call) ← IMPROVED
    ↓
Optimized Evaluation (1 batched call) ← IMPROVED
    ↓
Results Displayed
```

## Batching Implementation Details

### BatchedEvaluator Class (`/frontend/batched_evaluator.py`)

**Key Features:**
- **Single API Call**: Combines all dataset records into one prompt
- **JSON Response Parsing**: Expects structured array response
- **Fallback Mechanism**: Reverts to individual calls if batching fails
- **Configurable Batch Size**: Default 5 records per batch

**Batched Prompt Format:**
```
Process the following inputs and provide responses in the exact format shown:

Format your response as a JSON array with one response per input:
[{"response": "your_response_1"}, {"response": "your_response_2"}, ...]

Inputs to process:
1. Hello, I need help with my order
2. Thank you for your excellent service
3. I want to cancel my subscription
4. How do I track my package?
5. What are your business hours?

Provide exactly 5 responses in JSON array format.
```

**Response Parsing:**
- Extracts JSON array from model response
- Falls back to numbered response parsing
- Handles malformed responses gracefully

### Integration Points

**Modified Files:**
- `/frontend/sdk_worker.py`: Updated to use `BatchedEvaluator`
- `/frontend/batched_evaluator.py`: New batching implementation

**Usage:**
```python
# Before
baseline_evaluator = Evaluator(prompt_adapter, test_dataset, metric_adapter, inference_adapter)

# After  
baseline_evaluator = BatchedEvaluator(prompt_adapter, test_dataset, metric_adapter, inference_adapter)
```

## Performance Impact

### API Call Reduction
- **Evaluation Phase**: 80% reduction (10 calls → 2 calls)
- **Overall Optimization**: 23% reduction (26-35 calls → 18-27 calls)
- **Rate Limiting**: Significantly reduced due to fewer burst calls

### Trade-offs
- **Pros**: Fewer API calls, reduced rate limiting, faster evaluation
- **Cons**: More complex response parsing, potential for batch failures
- **Mitigation**: Automatic fallback to individual calls on failure

## Monitoring Calls

The optimization monitor page shows meta-prompter calls because they're captured during the optimization process. These are internal Nova SDK calls, not your actual job prompts.

To see your actual prompts, check the prompt candidates generated after optimization completes.

## Future Optimizations

Potential areas for further API call reduction:
1. **Batch Candidate Testing**: Combine multiple prompt candidates in single calls
2. **Parallel Processing**: Use async calls where possible
3. **Caching**: Cache similar prompt evaluations
4. **Smart Sampling**: Use subset of dataset for initial candidate filtering
