# Instructor Implementation Plan for Nova Prompt Optimizer

## Overview

This document outlines the plan to integrate [Instructor](https://python.useinstructor.com/) into the Nova Prompt Optimizer to improve structured output reliability, reduce JSON parsing errors, and add automatic validation with retries.

## Current State Analysis

### Current Issues
1. **JSON Parsing Errors**: Manual JSON parsing from LLM responses is error-prone
2. **No Validation**: No automatic validation of LLM outputs against expected schemas
3. **No Retry Logic**: Failed responses require manual intervention
4. **Type Safety**: No compile-time type checking for LLM responses
5. **Inconsistent Outputs**: LLM responses vary in structure and quality

### Current LLM Usage Points
1. **Dataset Analysis** (`prompt_templates.py::dataset_analysis`)
   - Input: Dataset content, prompt content, analysis depth
   - Output: JSON with `intent_analysis`, `metrics[]`, `reasoning`
   - Current: Manual JSON parsing with `json.loads()`

2. **Metric Code Generation** (`prompt_templates.py::metric_code_generation`)
   - Input: Metric name, criteria dict
   - Output: Python code as string
   - Current: Direct string response

3. **Metric Inference** (`app.py::call_ai_for_metric_inference`)
   - Uses Bedrock Nova models
   - Current: Manual JSON parsing with error handling

## Implementation Plan

### Phase 1: Core Infrastructure Setup

#### 1.1 Dependencies and Installation
```bash
pip install instructor tenacity pydantic
```

#### 1.2 Create Pydantic Models
Create `models/instructor_models.py`:

```python
from pydantic import BaseModel, Field, field_validator
from typing import List, Optional, Dict, Any
from enum import Enum

class MetricField(BaseModel):
    """Individual metric field definition"""
    name: str = Field(description="Field name from dataset")
    type: str = Field(description="Data type (string, number, boolean, object)")
    description: str = Field(description="What this field represents")

class EvaluationMetric(BaseModel):
    """Single evaluation metric definition"""
    name: str = Field(description="Clear, descriptive metric name")
    intent_understanding: str = Field(description="How this metric measures prompt success")
    data_fields: List[str] = Field(description="Exact field names from dataset")
    evaluation_logic: str = Field(description="Simple comparison logic")
    example: str = Field(description="Example using actual data structure")
    
    @field_validator('name')
    @classmethod
    def validate_name(cls, v):
        if len(v) < 3:
            raise ValueError("Metric name must be at least 3 characters")
        return v

class DatasetAnalysisResponse(BaseModel):
    """Structured response for dataset analysis"""
    intent_analysis: str = Field(description="What the prompt is asking for and expected output format")
    data_structure: Dict[str, Any] = Field(description="Analysis of actual data structure")
    metrics: List[EvaluationMetric] = Field(
        description="2-3 simple evaluation metrics",
        min_items=2,
        max_items=3
    )
    reasoning: str = Field(description="Why these metrics effectively measure the prompt's task")
    
    @field_validator('metrics')
    @classmethod
    def validate_metrics(cls, v):
        if len(v) < 2:
            raise ValueError("Must provide at least 2 metrics")
        return v

class MetricCodeResponse(BaseModel):
    """Structured response for metric code generation"""
    class_name: str = Field(description="Generated Python class name")
    python_code: str = Field(description="Complete Python class code")
    imports: List[str] = Field(description="Required imports")
    dependencies: List[str] = Field(description="External dependencies needed")
    
    @field_validator('python_code')
    @classmethod
    def validate_code(cls, v):
        # Basic validation that it contains class definition
        if 'class ' not in v or 'def apply(' not in v:
            raise ValueError("Code must contain class definition with apply method")
        return v
```

#### 1.3 Create Instructor Client Wrapper
Create `services/instructor_client.py`:

```python
import instructor
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
from pydantic import ValidationError
import boto3
from typing import TypeVar, Type
import json

T = TypeVar('T', bound='BaseModel')

class InstructorClient:
    """Wrapper for Instructor with Bedrock Nova integration"""
    
    def __init__(self, model_id: str = "us.amazon.nova-premier-v1:0"):
        self.model_id = model_id
        self.bedrock = boto3.client('bedrock-runtime')
        
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        retry=retry_if_exception_type((ValidationError, json.JSONDecodeError))
    )
    def extract(self, prompt: str, response_model: Type[T], **kwargs) -> T:
        """Extract structured data with automatic retries"""
        
        # Create system prompt for structured output
        system_prompt = f"""You are a precise data extraction assistant. 
        You must respond with valid JSON that matches the required schema exactly.
        
        Required Schema:
        {response_model.model_json_schema()}
        
        Rules:
        1. Return only valid JSON
        2. Include all required fields
        3. Follow the exact field names and types
        4. Do not add extra fields not in the schema
        """
        
        # Call Bedrock Nova
        response = self.bedrock.invoke_model(
            modelId=self.model_id,
            body=json.dumps({
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": prompt}
                ],
                "max_tokens": kwargs.get('max_tokens', 4000),
                "temperature": kwargs.get('temperature', 0.1)
            })
        )
        
        # Parse response
        result = json.loads(response['body'].read())
        content = result['output']['message']['content'][0]['text']
        
        # Parse and validate with Pydantic
        try:
            data = json.loads(content)
            return response_model.model_validate(data)
        except json.JSONDecodeError as e:
            # Try to extract JSON from response if wrapped in text
            import re
            json_match = re.search(r'\{.*\}', content, re.DOTALL)
            if json_match:
                data = json.loads(json_match.group())
                return response_model.model_validate(data)
            raise ValueError(f"Invalid JSON response: {e}")
```

### Phase 2: Replace Current LLM Calls

#### 2.1 Update Dataset Analysis
Replace `prompt_templates.py::dataset_analysis` usage:

```python
# Before (in app.py)
prompt = get_dataset_analysis_prompt(dataset_content, [], analysis_depth, prompt_content)
inferred_metrics = await call_ai_for_metric_inference(prompt, rate_limit, model_id)

# After
from services.instructor_client import InstructorClient
from models.instructor_models import DatasetAnalysisResponse

client = InstructorClient(model_id)
analysis_prompt = f"""
Analyze this dataset and prompt to create simple evaluation metrics:

Dataset: {dataset_content}
Prompt: {prompt_content}
Analysis Depth: {analysis_depth}

Create 2-3 simple metrics that measure success for the specific task.
"""

inferred_metrics = client.extract(
    prompt=analysis_prompt,
    response_model=DatasetAnalysisResponse,
    max_tokens=3000
)
```

#### 2.2 Update Metric Code Generation
Replace manual code generation:

```python
# Before
generated_code = await call_ai_for_code_generation(prompt)

# After
from models.instructor_models import MetricCodeResponse

code_response = client.extract(
    prompt=code_generation_prompt,
    response_model=MetricCodeResponse,
    max_tokens=2000
)
```

### Phase 3: Enhanced Error Handling and Validation

#### 3.1 Add Semantic Validation
For complex validation requirements:

```python
from instructor import llm_validator
from pydantic import BeforeValidator
from typing import Annotated

class ValidatedMetric(BaseModel):
    name: str
    evaluation_logic: Annotated[
        str,
        BeforeValidator(
            llm_validator(
                "Logic must be implementable in Python and use only the specified data fields",
                client=instructor_client
            )
        )
    ]
```

#### 3.2 Add Custom Retry Strategies
```python
from tenacity import retry_if_result

def should_retry_analysis(result: DatasetAnalysisResponse) -> bool:
    """Custom retry logic for dataset analysis"""
    # Retry if metrics are too generic or don't use actual field names
    for metric in result.metrics:
        if not metric.data_fields or 'generic' in metric.name.lower():
            return True
    return False

@retry(
    retry=retry_if_result(should_retry_analysis),
    stop=stop_after_attempt(2)
)
def analyze_dataset_with_validation(prompt: str) -> DatasetAnalysisResponse:
    return client.extract(prompt, DatasetAnalysisResponse)
```

### Phase 4: Integration Points

#### 4.1 Update API Endpoints
Modify these endpoints to use Instructor:

1. `/metrics/infer-from-dataset` - Dataset analysis
2. `/metrics/generate-code` - Code generation
3. Any other LLM-dependent endpoints

#### 4.2 Update Frontend Integration
Add validation feedback to UI:

```python
try:
    analysis = client.extract(prompt, DatasetAnalysisResponse)
    return {
        "success": True,
        "data": analysis.model_dump(),
        "validation_passed": True
    }
except ValidationError as e:
    return {
        "success": False,
        "error": "Validation failed",
        "details": e.errors(),
        "validation_passed": False
    }
```

### Phase 5: Advanced Features

#### 5.1 Streaming Support
For long-running operations:

```python
from instructor import Partial

# Stream partial results
for partial_result in client.stream_extract(
    prompt=long_prompt,
    response_model=Partial[DatasetAnalysisResponse]
):
    # Update UI with partial progress
    update_progress(partial_result)
```

#### 5.2 Batch Processing
For multiple metrics:

```python
class BatchMetricResponse(BaseModel):
    metrics: List[EvaluationMetric]
    
batch_response = client.extract(
    prompt=batch_prompt,
    response_model=BatchMetricResponse
)
```

## Implementation Timeline

### Week 1: Foundation
- [ ] Install dependencies
- [ ] Create Pydantic models
- [ ] Build InstructorClient wrapper
- [ ] Test basic functionality

### Week 2: Core Integration
- [ ] Replace dataset analysis calls
- [ ] Replace metric code generation
- [ ] Update error handling
- [ ] Test with existing datasets

### Week 3: Enhancement
- [ ] Add semantic validation
- [ ] Implement custom retry logic
- [ ] Update UI integration
- [ ] Performance testing

### Week 4: Advanced Features
- [ ] Add streaming support
- [ ] Implement batch processing
- [ ] Documentation updates
- [ ] Production deployment

## Benefits Expected

### Immediate Benefits
1. **Reduced JSON Errors**: Automatic parsing and validation
2. **Type Safety**: Compile-time checking with Pydantic
3. **Automatic Retries**: Built-in retry logic for failed validations
4. **Better Error Messages**: Detailed validation error reporting

### Long-term Benefits
1. **Improved Reliability**: Consistent, validated outputs
2. **Easier Maintenance**: Structured data models
3. **Better Testing**: Mockable, testable components
4. **Scalability**: Batch processing and streaming support

## Risk Mitigation

### Potential Risks
1. **Performance Impact**: Additional validation overhead
2. **Model Compatibility**: Bedrock Nova integration complexity
3. **Breaking Changes**: Existing code modifications needed

### Mitigation Strategies
1. **Gradual Rollout**: Implement feature flags for A/B testing
2. **Fallback Mechanism**: Keep existing JSON parsing as backup
3. **Comprehensive Testing**: Unit and integration tests
4. **Monitoring**: Track success rates and performance metrics

## Success Metrics

1. **Error Reduction**: 90% reduction in JSON parsing errors
2. **Validation Success**: 95% first-attempt validation success rate
3. **Response Quality**: Improved metric relevance scores
4. **Development Velocity**: Faster feature development with type safety

## Conclusion

Implementing Instructor will significantly improve the reliability and maintainability of our LLM integrations in the Nova Prompt Optimizer. The structured approach with Pydantic models, automatic validation, and retry logic will reduce errors and improve user experience.

The phased implementation approach allows for gradual adoption while maintaining system stability and provides clear rollback options if issues arise.
