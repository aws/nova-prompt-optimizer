# Nova Prompt Optimizer SDK - Official Workflow

## Overview
The Nova Prompt Optimizer SDK follows a structured workflow for prompt optimization using the Nova Meta Prompter + MIPROv2 with Nova Model Tips.

## Step-by-Step Workflow

### 1. Initial Setup
- Upload dataset
- Create prompt (system + user prompts)
- Define custom metrics
- Initialize optimization job

### 2. Dataset Adapter Initialization
```python
# Dataset adapter handles training/test data
dataset_adapter = JSONDatasetAdapter(dataset_path)
```

### 3. Prompt Adapter Setup
```python
# Prompt adapter processes system and user prompts
prompt_adapter = TextPromptAdapter()
prompt_adapter.set_system_prompt(content=system_prompt)
prompt_adapter.set_user_prompt(content=user_prompt, variables={"input"})
```

### 4. Metric Adapter Initialization
```python
# Custom metric adapter for evaluation (inherits from MetricAdapter abstract class)
metric_adapter = CustomMetricAdapter()
```

### 5. Inference Adapter Setup
```python
# Handles Bedrock API calls with rate limiting
inference_adapter = BedrockInferenceAdapter(region_name="us-east-1", rate_limit=rate_limit)
```

### 6. Baseline Evaluation
```python
from amzn_nova_prompt_optimizer.core.evaluation import Evaluator

# Evaluator uses InferenceRunner internally to generate results then evaluate
evaluator = Evaluator(prompt_adapter, test_set, metric_adapter, inference_adapter)
original_prompt_score = evaluator.aggregate_score(model_id=NOVA_MODEL_ID)

print(f"Original Prompt Evaluation Score = {original_prompt_score}")
```

**Key Components:**
- **Evaluator**: Orchestrates evaluation process
- **InferenceRunner**: Generates inference results using model_id
- **Metric Adapter**: Evaluates output against custom metrics
- **Process**: Generate inference → Evaluate against metrics → Aggregate score

### 7. Optimization Process
```python
from amzn_nova_prompt_optimizer.core.optimizers import NovaPromptOptimizer

# Nova Prompt Optimizer = Nova Meta Prompter + MIPROv2 + Nova Model Tips
nova_prompt_optimizer = NovaPromptOptimizer(
    prompt_adapter=prompt_adapter,
    inference_adapter=inference_adapter, 
    dataset_adapter=train_set,
    metric_adapter=metric_adapter
)

# Run optimization (mode: "lite", "pro", "premier")
optimized_prompt_adapter = nova_prompt_optimizer.optimize(mode="pro")
```

### 8. Extract Optimized Results
```python
# Access optimized components
print(optimized_prompt_adapter.system_prompt)  # Optimized system prompt
print(optimized_prompt_adapter.user_prompt)    # Optimized user prompt
print(optimized_prompt_adapter.few_shot_examples)  # Few-shot examples
```

### 9. Evaluate Optimized Prompt
```python
# Evaluate optimized prompt using same process as baseline
evaluator = Evaluator(optimized_prompt_adapter, test_set, metric_adapter, inference_adapter)
nova_prompt_optimizer_evaluation_score = evaluator.aggregate_score(model_id=NOVA_MODEL_ID)

print(f"Nova Prompt Optimizer = {nova_prompt_optimizer_evaluation_score}")
```

### 10. Save Results
```python
# Save optimized prompt adapter
optimized_prompt_adapter.save("optimized_prompt/")
```

## Key Architecture Components

### Core Adapters
1. **DatasetAdapter**: Handles training/test data formatting
2. **PromptAdapter**: Manages system/user prompts and variables
3. **MetricAdapter**: Custom evaluation logic (abstract class implementation)
4. **InferenceAdapter**: Bedrock API interface with rate limiting

### Evaluation System
- **Evaluator**: Main evaluation orchestrator
- **InferenceRunner**: Internal component for generating model responses
- **Process Flow**: Input → InferenceRunner → Model Response → MetricAdapter → Score

### Optimization Engine
- **NovaPromptOptimizer**: Meta-optimizer combining:
  - Nova Meta Prompter
  - MIPROv2 algorithm
  - Nova Model Tips
- **Modes**: lite, pro, premier (different optimization intensities)

## Critical Implementation Notes

1. **Evaluation Flow**: Evaluator → InferenceRunner → Bedrock API → MetricAdapter → Aggregate Score
2. **Optimization**: Uses DSPy MIPROv2 internally with Nova-specific enhancements
3. **Rate Limiting**: InferenceAdapter handles Bedrock rate limits
4. **Custom Metrics**: Must inherit from MetricAdapter abstract class
5. **Model Support**: Designed specifically for Nova models (lite, pro, premier)

## Expected Outputs
- **Baseline Score**: Original prompt performance
- **Optimized Score**: Improved prompt performance  
- **Optimized Prompts**: Enhanced system/user prompts
- **Few-shot Examples**: Generated training examples
- **Saved Artifacts**: Serialized optimized prompt adapter

This workflow ensures systematic prompt optimization using Nova's advanced capabilities while maintaining evaluation consistency between baseline and optimized versions.
---

## Frontend Implementation Architecture

### Two Distinct Bedrock Usage Patterns

Our frontend implementation separates concerns between enhancement features and core optimization workflow:

#### 1. Frontend Enhancement Features (Direct Bedrock Calls)
**Purpose**: Productivity features that enhance user experience
**Implementation**: Direct `boto3.client('bedrock-runtime')` calls

**Use Cases:**
- ✅ **Metric Generation**: AI-powered custom metric creation
- ✅ **Dataset Enhancement**: AI-powered dataset expansion/validation  
- ✅ **Prompt Suggestions**: AI-powered initial prompt recommendations
- ✅ **Database Operations**: Store/retrieve user data
- ✅ **UI Intelligence**: Any AI features we add to enhance UX

**Example:**
```python
def generate_custom_metric(description):
    bedrock = boto3.client('bedrock-runtime')  # Our direct call
    response = bedrock.converse(
        modelId="us.amazon.nova-premier-v1:0",
        messages=[{"role": "user", "content": f"Generate metric code for: {description}"}],
        system=[{"text": "You are a Python code generator..."}]
    )
    return response['output']['message']['content'][0]['text']
```

#### 2. Core Optimization Workflow (Official SDK)
**Purpose**: The actual prompt optimization that users expect
**Implementation**: Official Nova SDK classes and methods

**Use Cases:**
- ✅ **Baseline Evaluation**: Use `Evaluator` class
- ✅ **Optimization Process**: Use `NovaPromptOptimizer`
- ✅ **Final Evaluation**: Use `Evaluator` class again
- ✅ **Result Storage**: Use `optimized_prompt_adapter.save()`

**Corrected Implementation:**
```python
# Baseline evaluation (OFFICIAL WAY)
baseline_evaluator = Evaluator(prompt_adapter, test_dataset, metric_adapter, inference_adapter)
baseline_score = baseline_evaluator.aggregate_score(model_id=NOVA_MODEL_ID)

# Optimization (already correct)
nova_optimizer = NovaPromptOptimizer(prompt_adapter, inference_adapter, dataset_adapter, metric_adapter)
optimized_prompt_adapter = nova_optimizer.optimize(mode=model_mode)

# Final evaluation (OFFICIAL WAY)
optimized_evaluator = Evaluator(optimized_prompt_adapter, test_dataset, metric_adapter, inference_adapter)
optimized_score = optimized_evaluator.aggregate_score(model_id=NOVA_MODEL_ID)

# Save results (OFFICIAL WAY)
optimized_prompt_adapter.save(f"optimized_prompts/{optimization_id}/")
```

### Architecture Benefits

- ✅ **Clear Separation**: Frontend features vs core optimization
- ✅ **Official Workflow**: Baseline/optimization evaluation uses SDK properly  
- ✅ **Enhanced UX**: Keep our AI-powered frontend improvements
- ✅ **Maintainable**: Each system handles what it's designed for
- ✅ **Rate Limiting**: Separate rate limits for different use cases

### Implementation Guidelines

1. **Use Direct Bedrock Calls For**: Frontend productivity and enhancement features
2. **Use Official SDK For**: Core prompt optimization workflow (baseline → optimize → evaluate)
3. **Separate Rate Limits**: Frontend features get minimal allocation, SDK gets majority
4. **Proper Error Handling**: Each system handles its own error patterns
5. **Data Flow**: Frontend features enhance inputs → SDK processes optimization → Frontend displays results

This dual approach ensures we maintain the official SDK workflow integrity while providing enhanced user experience through AI-powered frontend features.
