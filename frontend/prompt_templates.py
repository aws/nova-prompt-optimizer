"""
Centralized Prompt Templates for Nova Prompt Optimizer Frontend
"""

class PromptTemplates:
    """Centralized storage for all AI prompt templates used in the frontend"""
    
    @staticmethod
    def dataset_analysis(dataset_content: str, focus_areas: list, analysis_depth: str) -> str:
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
        focus_text = ""
        if focus_areas:
            focus_text = f"\nPay special attention to: {', '.join(focus_areas)}"
        
        return f"""You are an expert in AI evaluation metrics. Analyze the following dataset and suggest appropriate evaluation metrics.

Dataset Content ({analysis_depth} analysis):
```
{dataset_content}
```

{focus_text}

Based on this dataset, suggest 3-5 specific evaluation metrics that would be most appropriate. For each metric, provide:

1. **Metric Name**: Clear, descriptive name
2. **Description**: What it measures and why it's important
3. **Evaluation Criteria**: Specific criteria for scoring (1-5 scale)
4. **Example**: How it would evaluate a sample from the dataset

Focus on metrics that are:
- Specific to this data type and structure
- Measurable and objective
- Relevant for the apparent use case
- Practical to implement

Format your response as JSON:
{{
  "metrics": [
    {{
      "name": "Metric Name",
      "description": "What this metric measures",
      "criteria": "Scoring criteria (1-5 scale)",
      "example": "Example evaluation"
    }}
  ],
  "reasoning": "Why these metrics are appropriate for this dataset"
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

Generate a complete Python class that inherits from MetricAdapter:

class GeneratedMetric(MetricAdapter):
    def apply(self, y_pred, y_true):
        # Handle both JSON and plain text inputs safely
        try:
            # Try to parse as JSON if it looks like JSON
            if isinstance(y_pred, str) and y_pred.strip().startswith('{{'):
                y_pred = json.loads(y_pred)
            if isinstance(y_true, str) and y_true.strip().startswith('{{'):
                y_true = json.loads(y_true)
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

    def batch_apply(self, y_preds, y_trues):
        scores = [self.apply(pred, true) for pred, true in zip(y_preds, y_trues)]
        return sum(scores) / len(scores) if scores else 0.0

Requirements:
1. Must inherit from MetricAdapter
2. Must implement both apply() and batch_apply() methods
3. Handle both JSON and plain text inputs safely
4. Use ONLY these imports: json, re, math, typing
5. Return precise decimal scores between 0-1 (avoid 0, 0.5, 1 only)
6. Use granular scoring with at least 10+ possible score values
7. Consider partial credit and multiple quality dimensions

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

# Convenience functions for easy access
def get_dataset_analysis_prompt(dataset_content: str, focus_areas: list = None, analysis_depth: str = "standard") -> str:
    """Get the dataset analysis prompt"""
    return PromptTemplates.dataset_analysis(dataset_content, focus_areas or [], analysis_depth)

def get_metric_code_prompt(name: str, criteria: dict) -> str:
    """Get the metric code generation prompt"""
    return PromptTemplates.metric_code_generation(name, criteria)

def get_natural_language_metric_prompt(name: str, description: str, natural_language: str, model_id: str) -> str:
    """Get the natural language metric creation prompt"""
    return PromptTemplates.natural_language_metric(name, description, natural_language, model_id)
