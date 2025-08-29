"""
Centralized Prompt Templates for Nova Prompt Optimizer Frontend
"""

class PromptTemplates:
    """Centralized storage for all AI prompt templates used in the frontend"""
    
    @staticmethod
    def dataset_analysis(dataset_content: str, focus_areas: list, analysis_depth: str, prompt_content: str = None) -> str:
        """
        SIMPLIFIED DATASET ANALYSIS PROMPT
        
        Purpose: Analyzes dataset and prompt to understand intent and create appropriate metrics
        Focus: Dataset structure + Prompt intent = Simple, effective metrics
        """
        
        # Add prompt analysis if provided
        prompt_analysis_text = ""
        if prompt_content:
            prompt_analysis_text = f"""

PROMPT INTENT ANALYSIS:
The following is the original prompt that will be used with this dataset:
---
{prompt_content}
---

Analyze the prompt to understand:
1. What task is the AI being asked to perform?
2. What format should the output be in (JSON, text, classification, etc.)?
3. What are the key success criteria implied by the prompt?
4. How should responses be evaluated for quality?"""
        
        return f"""You are an expert in AI evaluation metrics. Analyze the dataset and prompt to create simple, effective evaluation metrics.

Dataset Content ({analysis_depth} analysis):
```
{dataset_content}
```

{prompt_analysis_text}

IMPORTANT CLARIFICATIONS:
- The dataset format (JSONL, CSV, etc.) is just how the data is stored - ignore this format
- Focus ONLY on the actual input/output content within each example
- The dataset format does NOT determine what output format the prompt expects
- Base your metrics on what the prompt asks for, not how the dataset is formatted

ANALYSIS REQUIREMENTS:
1. FIRST: Analyze what the prompt is asking the AI to do and what output format is expected
2. Examine the ACTUAL data content and field names (ignore storage format)
3. Create metrics that measure success for this specific task

CRITICAL: Start your analysis by clearly stating what you understand the prompt's intent to be.

Based on this analysis, suggest 2-3 simple evaluation metrics. For each metric, provide:

1. **Metric Name**: Clear, descriptive name
2. **Intent Understanding**: What the prompt is asking for and how this metric measures success
3. **Data Fields Used**: Exactly which fields from the dataset this metric will access
4. **Evaluation Logic**: Simple logic for comparing predicted vs expected values
5. **Example**: How it would evaluate a sample from this dataset

Focus on metrics that are:
- Simple and focused on the core task
- Use the exact field names from the dataset
- Measure what the prompt is actually asking for
- Avoid overfitting or complex scoring
- Independent of dataset storage format (JSONL, CSV, etc.)

Format your response as JSON:
{{
  "intent_analysis": "REQUIRED: Clear description of the task based on the dataset structure and expected output format. Focus on what evaluation metrics should measure based on the data patterns.",
  "metrics": [
    {{
      "name": "Metric Name",
      "intent_understanding": "How this metric measures success for the data classification task",
      "data_fields": ["field1", "field2"],
      "evaluation_logic": "Simple comparison logic using actual field names",
      "example": "Example using actual data structure"
    }}
  ],
  "reasoning": "Why these simple metrics effectively measure the data classification task (focus on data structure and evaluation requirements)"
}}"""
        """
        DATASET ANALYSIS PROMPT
        
        Purpose: Analyzes user datasets to automatically infer appropriate evaluation metrics
        Used in: /metrics page -> "Infer from Dataset" tab -> form submission
        Called by: app.py -> infer_metrics_from_dataset() -> get_dataset_analysis_prompt()
        API Call: Bedrock Nova (Premier/Pro/Lite) via call_ai_for_metric_inference()
        
        Input: Raw dataset content (JSON samples), focus areas (accuracy, format, etc.), analysis depth
        Output: JSON with suggested metrics, descriptions, criteria, and reasoning
        
        Flow: User selects dataset -> AI analyzes structure/content -> Suggests relevant metrics -> 
              Feeds into metric_code_generation() to create executable Python code
        """
        # Build detailed focus areas text with new granular options
        focus_mapping = {
            # Accuracy & Correctness
            'exact_match': 'exact string matching between predicted and expected outputs',
            'semantic_equiv': 'semantic equivalence even when wording differs',
            'factual_accuracy': 'factual correctness and truthfulness of information',
            'numerical_precision': 'accuracy of numerical values and calculations',
            'classification_accuracy': 'correct classification or categorization',
            
            # Format & Structure
            'valid_json': 'valid JSON, XML, or YAML format compliance',
            'required_fields': 'presence of all required fields or elements',
            'correct_types': 'correct data types for each field',
            'schema_compliance': 'adherence to predefined schemas or structures',
            'length_constraints': 'appropriate length limits and constraints',
            
            # Completeness
            'all_requirements': 'addressing all specified requirements',
            'sufficient_detail': 'providing adequate level of detail',
            'topic_coverage': 'comprehensive coverage of relevant topics',
            'edge_cases': 'handling of edge cases and exceptions',
            'context_preservation': 'maintaining important contextual information',
            
            # Relevance
            'query_alignment': 'alignment with the specific query or request',
            'context_awareness': 'understanding and using provided context',
            'topic_relevance': 'relevance to the main topic or subject',
            'intent_understanding': 'understanding user intent and purpose',
            'appropriate_scope': 'maintaining appropriate scope and boundaries'
        }
        
        if focus_areas:
            focus_descriptions = [focus_mapping.get(area, area) for area in focus_areas]
            focus_text = f"\nPay special attention to: {', '.join(focus_descriptions)}"
        else:
            focus_text = ""
        
        # Add prompt analysis if provided
        prompt_analysis_text = ""
        if prompt_content:
            prompt_analysis_text = f"""

ORIGINAL PROMPT ANALYSIS:
The following is the original prompt that will be used with this dataset:
---
{prompt_content}
---

CRITICAL PROMPT INTENT ANALYSIS:
1. Analyze the prompt's specific task and expected behavior
2. Identify what the prompt is asking the AI to do (classify, generate, transform, etc.)
3. Determine the expected output format based on the prompt instructions
4. Understand the success criteria implied by the prompt
5. Validate that the dataset examples align with the prompt's intended use case

The metrics MUST evaluate how well responses fulfill the prompt's specific requirements and intended behavior. Consider:
- Does the prompt ask for classification? → Metrics should measure classification accuracy
- Does the prompt ask for JSON output? → Metrics should validate JSON structure
- Does the prompt specify certain fields? → Metrics should check those exact fields
- Does the prompt have quality criteria? → Metrics should measure those criteria"""
        
        return f"""You are an expert in AI evaluation metrics. Analyze the following dataset and suggest appropriate evaluation metrics.

Dataset Content ({analysis_depth} analysis):
```
{dataset_content}
```

{focus_text}{prompt_analysis_text}

CRITICAL: Analyze the ACTUAL data structure in the dataset above. Look at:
- What fields are present in the data (e.g., "categories", "sentiment", "urgency", etc.)
- What data types are used (strings, numbers, booleans, objects)
- What the expected output format appears to be
- How the input and expected output relate to each other

{f"VALIDATE AGAINST ORIGINAL INTENT: Ensure the evaluation criteria aligns with the original prompt's task and expected behavior. The metrics must measure success for the specific tasks the prompt is designed to perform." if prompt_content else ""}

Based on this SPECIFIC dataset structure{" and original prompt intent" if prompt_content else ""}, suggest up to 10 evaluation metrics that work with the entire output. For each metric, provide:

1. **Metric Name**: Clear, descriptive name
2. **Description**: What it measures and why it's important for THIS specific data
3. **Data Fields Used**: Exactly which fields from the dataset this metric will access
4. **Evaluation Logic**: Specific logic for comparing predicted vs expected values using the actual field names
5. **Example**: How it would evaluate a sample from THIS dataset using the actual field structure

Focus on metrics that are:
- Specific to the ACTUAL data structure shown above
- Use the EXACT field names present in the dataset
- Handle the ACTUAL data types (strings, numbers, booleans, objects)
- Relevant for the apparent use case based on the data content

Format your response as JSON:
{{
  "metrics": [
    {{
      "name": "Metric Name",
      "description": "What this metric measures for this specific data",
      "data_fields": ["field1", "field2"],
      "evaluation_logic": "How to compare using actual field names",
      "example": "Example using actual data structure"
    }}
  ],
  "data_structure_analysis": "Analysis of the actual data structure and field types",
  "prompt_intent_validation": "How these metrics align with the original prompt's intended task and success criteria",
  "reasoning": "Why these metrics are appropriate for this specific dataset structure and prompt intent"
}}"""

    @staticmethod
    def metric_code_generation(name: str, criteria: dict) -> str:
        """
        METRIC CODE GENERATION PROMPT
        
        Purpose: Converts metric descriptions/criteria into executable Python MetricAdapter classes
        Used in: Multiple places where metrics need executable code
        Called by: 
          - metric_service.py -> generate_metric_code() (for inferred metrics)
          - Natural language metric creation
          - Manual metric code generation
        API Call: Bedrock Nova via MetricService.generate_metric_code()
        
        Input: Metric name, evaluation criteria (from dataset analysis or user input)
        Output: Complete Python class inheriting from MetricAdapter with apply() method
        
        Flow: Metric criteria -> AI generates Python code -> Code saved to database -> 
              Used by sdk_worker.py during optimization to score prompt candidates
        """
        return f"""Generate a Python MetricAdapter subclass for evaluating AI outputs with ROBUST JSON PARSING and DETAILED SCORING.

Requirements:
- Metric Name: {name}
- Evaluation Criteria: {criteria.get('natural_language', '')}
- Dataset Format: {criteria.get('dataset_format', 'json')}

CRITICAL: ANALYZE THE ACTUAL DATA STRUCTURE FROM THESE EXAMPLES:
{criteria.get('metrics_description', 'No data samples provided')}

IMPORTANT PATTERNS TO FOLLOW:

1. **Robust JSON Parsing**: Include a parse_json method that handles both direct JSON and markdown code blocks:
   
   def parse_json(self, input_string: str):
       try:
           return json.loads(input_string)
       except json.JSONDecodeError as err:
           # Try extracting from markdown code blocks
           patterns = [
               re.compile(r"```json\s*(.*?)\s*```", re.DOTALL | re.IGNORECASE),
               re.compile(r"```(.*?)```", re.DOTALL)
           ]
           for pattern in patterns:
               match = pattern.search(input_string)
               if match:
                   try:
                       return json.loads(match.group(1).strip())
                   except json.JSONDecodeError:
                       continue
           raise err

2. **Detailed Return Structure**: Return a Dict with component breakdown for debugging:
   - Include "is_valid_json" field
   - Include individual field accuracy scores
   - Include "total" field with overall score
   - Use field names from YOUR ACTUAL DATA

3. **Direct Field Access**: Analyze the data samples to determine the correct structure:
   - Use direct access like y_pred.get("field_name") 
   - Don't use complex fallback logic unless absolutely necessary
   - Base field names on the actual data structure shown above

4. **Component Scoring**: Calculate individual scores for each field being evaluated, then average them

5. **Error Handling**: Return meaningful error information when JSON parsing fails

{f'''6. **Output Format Validation**: Include "is_valid_json" field in your detailed return structure to validate that outputs match the expected JSON format from the dataset.''' if criteria.get('include_format_validation', True) else ''}

CRITICAL: Adapt the field names and scoring logic to match YOUR SPECIFIC DATA STRUCTURE from the examples above. Don't hardcode generic field names.

Required imports:
from amzn_nova_prompt_optimizer.core.input_adapters.metric_adapter import MetricAdapter
from typing import List, Any, Dict
import json
import re
import math

Generate a complete Python class that inherits from MetricAdapter.

AVAILABLE LIBRARIES (use for advanced metrics):
- Standard: json, re, math, typing (built-in)
- Scientific: numpy (efficient arrays, statistics, linear algebra)
- Data: pandas (dataframes, data manipulation) 
- ML: sklearn.metrics (F1, precision, recall, kappa, ROC-AUC, etc.)

CRITICAL REQUIREMENTS:
1. Use appropriate libraries for the metric complexity
2. Prefer sklearn.metrics for standard ML metrics (F1, precision, recall)
3. Use numpy for numerical operations and array handling
4. Implement robust error handling for edge cases
5. End your code with: metric_adapter = GeneratedMetric()

AVAILABLE IMPORTS:
from typing import List, Any, Dict
import json
import re
import math
import numpy as np
import pandas as pd
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, cohen_kappa_score

class GeneratedMetric(MetricAdapter):
    def apply(self, y_pred: Any, y_true: Any):
        # Handle both JSON and plain text inputs safely
        try:
            # Try to parse as JSON if it looks like JSON
            if isinstance(y_pred, str) and y_pred.strip().startswith('{{'):
                y_pred = json.loads(y_pred)
            if isinstance(y_true, str) and y_true.strip().startswith('{{'):
                y_true = json.loads(y_true)
        except:
            pass
        
        # Your evaluation logic here - return precise decimal score between 0.0 and 1.0
        score = 0.0
        # Add your granular scoring logic here
        
        return round(score, 3)

    def batch_apply(self, y_preds: List[Any], y_trues: List[Any]):
        scores = [self.apply(pred, true) for pred, true in zip(y_preds, y_trues)]
        return sum(scores) / len(scores) if scores else 0.0

Return only the Python class code, no explanations or markdown formatting."""
        """
        METRIC CODE GENERATION PROMPT
        
        Purpose: Converts metric descriptions/criteria into executable Python MetricAdapter classes
        Used in: Multiple places where metrics need executable code
        Called by: 
          - metric_service.py -> generate_metric_code() (for inferred metrics)
          - Natural language metric creation
          - Manual metric code generation
        API Call: Bedrock Nova via MetricService.generate_metric_code()
        
        Input: Metric name, evaluation criteria (from dataset analysis or user input)
        Output: Complete Python class inheriting from MetricAdapter with evaluate_single() method
        
        Flow: Metric criteria -> AI generates Python code -> Code saved to database -> 
              Used by sdk_worker.py during optimization to score prompt candidates
        """
        return f"""Generate a Python MetricAdapter subclass for evaluating AI outputs with GRANULAR SCORING.

Requirements:
- Metric Name: {name}
- Evaluation Criteria: {criteria.get('natural_language', '')}
- Dataset Format: {criteria.get('dataset_format', 'json')}

Available imports (ONLY use these - no other imports allowed):
- import json
- import re
- import math
- from typing import Any, List, Dict

Generate a complete Python class that inherits from MetricAdapter (DO NOT define MetricAdapter):

class GeneratedMetric(MetricAdapter):
    def evaluate_single(self, prediction, ground_truth=None, **kwargs):
        # Handle both JSON and plain text inputs safely
        try:
            # Try to parse as JSON if it looks like JSON
            if isinstance(prediction, str) and prediction.strip().startswith('{{'):
                prediction = json.loads(prediction)
            if isinstance(ground_truth, str) and ground_truth.strip().startswith('{{'):
                ground_truth = json.loads(ground_truth)
        except:
            # If JSON parsing fails, use as plain text
            pass
        
        # CRITICAL: Use granular scoring with decimal precision
        # Examples of good granular scores:
        # Perfect match: 1.0
        # Excellent (minor issues): 0.85-0.95
        # Good (some issues): 0.65-0.84
        # Fair (significant issues): 0.35-0.64
        # Poor (major issues): 0.15-0.34
        # Very poor: 0.01-0.14
        # Complete failure: 0.0
        
        # Your evaluation logic here using only basic Python + json/re/math
        # Use math functions for precise scoring: math.exp, math.log, etc.
        # Calculate partial credit for near-matches
        # Consider multiple quality dimensions
        
        score = 0.0
        # Add your granular scoring logic here
        
        # IMPORTANT: Always return precise decimal score between 0.0 and 1.0
        return round(score, 3)  # Round to 3 decimal places for precision

    def batch_evaluate(self, predictions, ground_truths=None, **kwargs):
        if ground_truths is None:
            ground_truths = [None] * len(predictions)
        scores = [self.evaluate_single(pred, gt, **kwargs) for pred, gt in zip(predictions, ground_truths)]
        return scores

    def apply(self, y_pred, y_true):
        # Legacy method - delegate to evaluate_single
        return self.evaluate_single(y_pred, y_true)

    def batch_apply(self, y_preds, y_trues):
        # Legacy method - delegate to batch_evaluate
        return self.batch_evaluate(y_preds, y_trues)

Requirements:
1. Must inherit from MetricAdapter
2. Must implement evaluate_single(prediction, ground_truth=None, **kwargs) method
3. Must implement batch_evaluate(predictions, ground_truths=None, **kwargs) method
4. Handle both JSON and plain text inputs safely
5. Use ONLY these imports: json, re, math, typing
6. Return precise decimal scores between 0-1 (avoid 0, 0.5, 1 only)
7. Use granular scoring with at least 10+ possible score values
8. Consider partial credit and multiple quality dimensions

Return only the Python class code, no explanations or markdown formatting."""

    @staticmethod
    def natural_language_metric(name: str, description: str, natural_language: str, model_id: str) -> str:
        """
        NATURAL LANGUAGE METRIC CREATION PROMPT
        
        Purpose: Creates metrics from user's natural language descriptions (manual metric creation)
        Used in: /metrics page -> "Natural Language" tab -> form submission
        Called by: components/metrics_page.py -> natural language metric creation flow
        API Call: Bedrock Nova via direct API call in metric creation
        
        Input: User-provided metric name, description, natural language evaluation criteria
        Output: Complete Python MetricAdapter class based on natural language requirements
        
        Flow: User describes evaluation criteria in plain English -> AI converts to Python code ->
              Code preview -> User saves -> Used in optimizations
        
        Example: "Score based on sentiment accuracy and response completeness" -> 
                 Python class that evaluates sentiment and completeness
        """
        return f"""Create a Python MetricAdapter subclass for evaluating AI outputs with GRANULAR SCORING based on natural language criteria.

Metric Details:
- Name: {name}
- Description: {description}
- Model: {model_id}

Natural Language Evaluation Criteria:
{natural_language}

Generate clean Python code that:
1. Inherits from MetricAdapter
2. Implements evaluate_single(self, output, reference) method
3. Returns GRANULAR scores between 0.0 and 1.0 with decimal precision
4. Evaluates based on the natural language criteria provided
5. Handles edge cases gracefully

CRITICAL SCORING GUIDELINES:
- Perfect match: 1.0
- Excellent (minor issues): 0.85-0.95
- Good (some issues): 0.65-0.84
- Fair (significant issues): 0.35-0.64
- Poor (major issues): 0.15-0.34
- Very poor: 0.01-0.14
- Complete failure: 0.0

The evaluate_single method should:
- Take 'output' (AI-generated response) and 'reference' (expected/ground truth)
- Apply the evaluation logic described in the natural language criteria
- Calculate partial credit for near-matches and quality dimensions
- Return a precise decimal score between 0.0 (worst) and 1.0 (best)
- Use at least 10+ different possible score values (avoid binary 0/1 scoring)

Return only the Python class code, no explanations or markdown formatting."""
    
    @staticmethod
    def get_composite_metric_prompt(metrics: list, weights: list = None, dataset_structure: dict = None, original_prompt: str = None) -> str:
        """Generate prompt for creating a composite metric from multiple metric descriptions"""
        if weights is None:
            if metrics and len(metrics) > 0:
                weights = [1.0 / len(metrics)] * len(metrics)
            else:
                weights = [1.0]  # Default fallback
        
        return f"""You must generate EXACTLY this code structure. Analyze the dataset structure first, then optionally use prompt context for validation:

DATASET STRUCTURE (PRIMARY):
{dataset_structure if dataset_structure else "Generic structure - use basic field comparisons"}

{f"PROMPT CONTEXT (OPTIONAL - for validation only): {original_prompt}" if original_prompt else ""}

METRICS TO IMPLEMENT:
{chr(10).join([f"Metric {i+1} (Weight: {weight:.2f}): {metric.get('name', f'Metric {i+1}')} - {metric.get('description', 'Evaluates specific aspects')}" for i, (metric, weight) in enumerate(zip(metrics, weights))])}

from amzn_nova_prompt_optimizer.core.input_adapters.metric_adapter import MetricAdapter
from typing import List, Any, Dict
import re
import json

class CompositeMetric(MetricAdapter):
    def parse_json(self, input_string: str):
        \"\"\"
        Attempts to parse the given string as JSON. If direct parsing fails,
        it tries to extract a JSON snippet from code blocks formatted as:
            ```json
            ... JSON content ...
            ```
        or any code block delimited by triple backticks and then parses that content. 
        \"\"\"
        try:
            return json.loads(input_string)
        except json.JSONDecodeError as err:
            error = err

        patterns = [
            re.compile(r"```json\\s*(.*?)\\s*```", re.DOTALL | re.IGNORECASE),
            re.compile(r"```(.*?)```", re.DOTALL)
        ]

        for pattern in patterns:
            match = pattern.search(input_string)
            if match:
                json_candidate = match.group(1).strip()
                try:
                    return json.loads(json_candidate)
                except json.JSONDecodeError:
                    continue

        raise error

    def _calculate_metrics(self, y_pred: Any, y_true: Any) -> Dict:
        strict_json = False
        result = {{
            "is_valid_json": False,
{chr(10).join([f'            "metric_{i+1}_score": 0.0,'for i, metric in enumerate(metrics)])}
        }}

        try:
            y_true = y_true if isinstance(y_true, dict) else (json.loads(y_true) if strict_json else self.parse_json(y_true))
            y_pred = y_pred if isinstance(y_pred, dict) else (json.loads(y_pred) if strict_json else self.parse_json(y_pred))
        except json.JSONDecodeError:
            result["total"] = 0.0
            return result
        else:
            if isinstance(y_pred, str):
                result["total"] = 0.0
                return result
            result["is_valid_json"] = True

            # TODO: Implement metric calculations based on dataset structure analysis
            # Primary: Use dataset structure fields and types from analysis above
            # Secondary: Cross-reference with original prompt context if available
            # Generate appropriate comparisons for each detected field type

        # Compute weighted composite score
        weighted_scores = [
{chr(10).join([f'            result["metric_{i+1}_score"] * {weight},'for i, weight in enumerate(weights)])}
        ]
        result["total"] = sum(weighted_scores)

        return result

    def apply(self, y_pred: Any, y_true: Any):
        return self._calculate_metrics(y_pred, y_true)

    def batch_apply(self, y_preds: List[Any], y_trues: List[Any]):
        evals = [self.apply(y_pred, y_true) for y_pred, y_true in zip(y_preds, y_trues)]
        float_keys = [k for k, v in evals[0].items() if isinstance(v, (int, float, bool))]
        return {{k: sum(e[k] for e in evals) / len(evals) for k in float_keys}}

metric_adapter = CompositeMetric()

CRITICAL: Replace the TODO comment with actual metric implementations. Use only basic Python operations. Do not change anything else.

FORBIDDEN IMPORTS: sklearn, numpy, pandas, statsmodels, scipy
ALLOWED IMPORTS: json, re, typing (already included above)"""
        """Generate prompt for creating a composite metric from multiple metric descriptions"""
        if weights is None:
            if metrics and len(metrics) > 0:
                weights = [1.0 / len(metrics)] * len(metrics)
            else:
                weights = [1.0]  # Default fallback
        
        # Build metric descriptions
        metric_descriptions = []
        for i, (metric, weight) in enumerate(zip(metrics, weights)):
            metric_descriptions.append(f"""
Metric {i+1} (Weight: {weight:.2f}):
- Name: {metric.get('name', f'Metric {i+1}')}
- Description: {metric.get('description', 'Evaluates specific aspects of the data')}
- Type: {metric.get('type', 'accuracy')}
- Complexity: {metric.get('complexity', 'moderate')}
""")
        
        return f"""You must generate code that follows this EXACT structure. Do not deviate from this pattern:

```python
from amzn_nova_prompt_optimizer.core.input_adapters.metric_adapter import MetricAdapter
from typing import List, Any, Dict
import re
import json

class CompositeMetric(MetricAdapter):
    def parse_json(self, input_string: str):
        \"\"\"
        Attempts to parse the given string as JSON. If direct parsing fails,
        it tries to extract a JSON snippet from code blocks formatted as:
            ```json
            ... JSON content ...
            ```
        or any code block delimited by triple backticks and then parses that content. 
        \"\"\"
        try:
            return json.loads(input_string)
        except json.JSONDecodeError as err:
            error = err

        patterns = [
            re.compile(r"```json\\s*(.*?)\\s*```", re.DOTALL | re.IGNORECASE),
            re.compile(r"```(.*?)```", re.DOTALL)
        ]

        for pattern in patterns:
            match = pattern.search(input_string)
            if match:
                json_candidate = match.group(1).strip()
                try:
                    return json.loads(json_candidate)
                except json.JSONDecodeError:
                    continue

        raise error

    def _calculate_metrics(self, y_pred: Any, y_true: Any) -> Dict:
        strict_json = False
        result = {{
            "is_valid_json": False,
            # Add specific metric fields based on the {len(metrics)} metrics:
{chr(10).join([f'            "metric_{i+1}_score": 0.0,  # {metric.get("name", f"Metric {i+1}")}'for i, metric in enumerate(metrics)])}
        }}

        try:
            y_true = y_true if isinstance(y_true, dict) else (json.loads(y_true) if strict_json else self.parse_json(y_true))
            y_pred = y_pred if isinstance(y_pred, dict) else (json.loads(y_pred) if strict_json else self.parse_json(y_pred))
        except json.JSONDecodeError:
            result["total"] = 0
            return result
        else:
            if isinstance(y_pred, str):
                result["total"] = 0
                return result
            result["is_valid_json"] = True

            # Implement the {len(metrics)} specific metrics here:
            # Metric 1: {metrics[0].get('name', 'Metric 1')} - {metrics[0].get('description', '')}
            # Metric 2: {metrics[1].get('name', 'Metric 2') if len(metrics) > 1 else 'N/A'}
            # ... implement each metric calculation ...

        # Compute weighted composite score using weights: {weights}
        weighted_scores = [
{chr(10).join([f'            result["metric_{i+1}_score"] * {weight},'for i, weight in enumerate(weights)])}
        ]
        result["total"] = sum(weighted_scores)

        return result

    def apply(self, y_pred: Any, y_true: Any):
        return self._calculate_metrics(y_pred, y_true)

    def batch_apply(self, y_preds: List[Any], y_trues: List[Any]):
        evals = [self.apply(y_pred, y_true) for y_pred, y_true in zip(y_preds, y_trues)]
        float_keys = [k for k, v in evals[0].items() if isinstance(v, (int, float, bool))]
        return {{k: sum(e[k] for e in evals) / len(evals) for k in float_keys}}

class CompositeNovaMetric(CompositeMetric):
    def apply(self, y_pred: Any, y_true: Any):
        # Requires to return a value and not a JSON payload
        return self._calculate_metrics(y_pred, y_true)["total"]
        
    def batch_apply(self, y_preds: List[Any], y_trues: List[Any]):
        pass
```

METRICS TO IMPLEMENT:
{chr(10).join(metric_descriptions)}

CRITICAL: Follow the exact structure above. Implement the specific metric calculations in _calculate_metrics method. Use the exact same method names, class structure, and return patterns.

IMPORTANT: Only use the imports provided above (re, json, typing). Do NOT import sklearn, numpy, or other libraries that may not be available. Implement all calculations using basic Python operations.

REQUIRED ENDING:
End your code with these exact lines:
```
metric_adapter = CompositeMetric()
nova_metric_adapter = CompositeNovaMetric()
```"""

# Convenience functions for easy access
def get_dataset_analysis_prompt(dataset_content: str, focus_areas: list = None, analysis_depth: str = "standard", prompt_content: str = None) -> str:
    """Get the dataset analysis prompt"""
    return PromptTemplates.dataset_analysis(dataset_content, focus_areas or [], analysis_depth, prompt_content)

def get_metric_code_prompt(name: str, criteria: dict) -> str:
    """Get the metric code generation prompt"""
    return PromptTemplates.metric_code_generation(name, criteria)

def get_natural_language_metric_prompt(name: str, description: str, natural_language: str, model_id: str) -> str:
    """Get the natural language metric creation prompt"""
    return PromptTemplates.natural_language_metric(name, description, natural_language, model_id)
