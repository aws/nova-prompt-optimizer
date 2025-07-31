# Custom Metrics

Learn how to create and use custom evaluation metrics to measure prompt performance according to your specific requirements.

## Understanding Metrics

### What are Metrics?
Metrics are functions that evaluate how well your optimized prompts perform compared to your ground truth data. They provide quantitative measures of success that guide the optimization process.

### Built-in vs Custom Metrics
- **Built-in Metrics**: Standard metrics like accuracy, F1-score, BLEU score
- **Custom Metrics**: Domain-specific metrics you create for your use case
- **Composite Metrics**: Combinations of multiple metrics with weights

## When to Use Custom Metrics

### Domain-Specific Requirements
- **Medical**: Accuracy for critical vs. non-critical information
- **Legal**: Compliance with specific regulations or standards
- **Customer Service**: Tone, empathy, and resolution effectiveness
- **Creative Writing**: Style, creativity, and adherence to guidelines

### Business Objectives
- **Cost Optimization**: Shorter responses to reduce API costs
- **User Experience**: Response time and clarity
- **Brand Consistency**: Tone and messaging alignment
- **Compliance**: Adherence to company policies

## Creating Custom Metrics

### Step 1: Access Metric Workbench
1. Navigate to **Metric Workbench** in the main navigation
2. Click **Create New Metric**
3. You'll see the metric editor interface

### Step 2: Basic Information
1. **Metric Name**: Enter a descriptive name
   - Examples: "Medical Accuracy", "Brand Tone Compliance"
2. **Description**: Explain what the metric measures
3. **Category**: Choose or create a category for organization

### Step 3: Write Metric Code
The metric editor provides a Python code environment where you implement your evaluation logic.

#### Required Interface
Your metric must implement these methods:
```python
def apply(self, prediction: str, ground_truth: str, **kwargs) -> float:
    """
    Evaluate a single prediction against ground truth.
    
    Args:
        prediction: The model's output
        ground_truth: The expected/correct output
        **kwargs: Additional context (input, metadata, etc.)
    
    Returns:
        float: Score between 0.0 and 1.0 (higher is better)
    """
    pass

def batch_apply(self, predictions: List[str], ground_truths: List[str], **kwargs) -> List[float]:
    """
    Evaluate multiple predictions at once (optional, for efficiency).
    
    Args:
        predictions: List of model outputs
        ground_truths: List of expected outputs
        **kwargs: Additional context
    
    Returns:
        List[float]: List of scores between 0.0 and 1.0
    """
    # Default implementation calls apply() for each item
    return [self.apply(pred, gt, **kwargs) for pred, gt in zip(predictions, ground_truths)]
```

### Step 4: Example Implementations

#### Simple Exact Match
```python
def apply(self, prediction: str, ground_truth: str, **kwargs) -> float:
    """Check if prediction exactly matches ground truth."""
    return 1.0 if prediction.strip().lower() == ground_truth.strip().lower() else 0.0
```

#### Keyword Presence
```python
def apply(self, prediction: str, ground_truth: str, **kwargs) -> float:
    """Check if prediction contains required keywords from ground truth."""
    required_keywords = ground_truth.lower().split()
    prediction_lower = prediction.lower()
    
    matches = sum(1 for keyword in required_keywords if keyword in prediction_lower)
    return matches / len(required_keywords) if required_keywords else 0.0
```

#### Sentiment Alignment
```python
import re

def apply(self, prediction: str, ground_truth: str, **kwargs) -> float:
    """Evaluate sentiment alignment between prediction and ground truth."""
    
    def get_sentiment_score(text):
        positive_words = ['good', 'great', 'excellent', 'positive', 'happy']
        negative_words = ['bad', 'terrible', 'awful', 'negative', 'sad']
        
        text_lower = text.lower()
        pos_count = sum(1 for word in positive_words if word in text_lower)
        neg_count = sum(1 for word in negative_words if word in text_lower)
        
        if pos_count > neg_count:
            return 1.0  # Positive
        elif neg_count > pos_count:
            return -1.0  # Negative
        else:
            return 0.0  # Neutral
    
    pred_sentiment = get_sentiment_score(prediction)
    truth_sentiment = get_sentiment_score(ground_truth)
    
    # Perfect match = 1.0, opposite = 0.0, neutral mismatch = 0.5
    if pred_sentiment == truth_sentiment:
        return 1.0
    elif (pred_sentiment > 0) != (truth_sentiment > 0) and pred_sentiment != 0 and truth_sentiment != 0:
        return 0.0  # Opposite sentiments
    else:
        return 0.5  # One neutral, one not
```

#### Length Penalty
```python
def apply(self, prediction: str, ground_truth: str, **kwargs) -> float:
    """Penalize predictions that are too long or too short."""
    target_length = len(ground_truth.split())
    pred_length = len(prediction.split())
    
    # Ideal length ratio
    if target_length == 0:
        return 1.0 if pred_length == 0 else 0.0
    
    ratio = pred_length / target_length
    
    # Penalty for being too long or too short
    if 0.8 <= ratio <= 1.2:
        return 1.0  # Within acceptable range
    elif 0.5 <= ratio <= 2.0:
        return 0.5  # Moderate penalty
    else:
        return 0.0  # Severe penalty
```

#### Composite Metric
```python
import json

def apply(self, prediction: str, ground_truth: str, **kwargs) -> float:
    """Combine multiple evaluation criteria."""
    
    # Accuracy component
    accuracy = 1.0 if prediction.strip().lower() == ground_truth.strip().lower() else 0.0
    
    # Length component
    target_length = len(ground_truth.split())
    pred_length = len(prediction.split())
    length_ratio = min(pred_length, target_length) / max(pred_length, target_length) if max(pred_length, target_length) > 0 else 1.0
    
    # Completeness component (contains key information)
    key_phrases = ["because", "therefore", "due to", "as a result"]
    completeness = 1.0 if any(phrase in prediction.lower() for phrase in key_phrases) else 0.5
    
    # Weighted combination
    weights = {"accuracy": 0.5, "length": 0.2, "completeness": 0.3}
    
    final_score = (
        weights["accuracy"] * accuracy +
        weights["length"] * length_ratio +
        weights["completeness"] * completeness
    )
    
    return final_score
```

### Step 5: Testing Your Metric
1. Click **Test Metric** in the editor
2. Provide sample prediction and ground truth
3. Review the score and any error messages
4. Iterate until the metric works as expected

### Step 6: Save and Deploy
1. Click **Save Metric** when satisfied
2. Your metric is added to the metric library
3. It's now available for optimization workflows

## Advanced Metric Patterns

### Using External Libraries
```python
# You can import standard Python libraries
import re
import json
import math
from collections import Counter

def apply(self, prediction: str, ground_truth: str, **kwargs) -> float:
    # Use imported libraries in your metric logic
    pass
```

### Accessing Additional Context
```python
def apply(self, prediction: str, ground_truth: str, **kwargs) -> float:
    # Access original input
    original_input = kwargs.get('input', '')
    
    # Access metadata
    metadata = kwargs.get('metadata', {})
    category = metadata.get('category', 'unknown')
    
    # Adjust scoring based on context
    if category == 'technical':
        # Apply stricter evaluation for technical content
        pass
    
    return score
```

### Handling Edge Cases
```python
def apply(self, prediction: str, ground_truth: str, **kwargs) -> float:
    # Handle empty inputs
    if not prediction.strip():
        return 0.0
    
    if not ground_truth.strip():
        return 1.0  # No ground truth to compare against
    
    # Handle very long texts
    if len(prediction) > 10000:
        prediction = prediction[:10000]  # Truncate for processing
    
    # Your evaluation logic here
    return score
```

### Multi-Criteria Evaluation
```python
def apply(self, prediction: str, ground_truth: str, **kwargs) -> float:
    scores = {}
    
    # Criterion 1: Factual accuracy
    scores['accuracy'] = self.evaluate_accuracy(prediction, ground_truth)
    
    # Criterion 2: Completeness
    scores['completeness'] = self.evaluate_completeness(prediction, ground_truth)
    
    # Criterion 3: Clarity
    scores['clarity'] = self.evaluate_clarity(prediction)
    
    # Weighted combination
    weights = {'accuracy': 0.5, 'completeness': 0.3, 'clarity': 0.2}
    
    return sum(weights[criterion] * score for criterion, score in scores.items())

def evaluate_accuracy(self, prediction: str, ground_truth: str) -> float:
    # Implementation for accuracy evaluation
    pass

def evaluate_completeness(self, prediction: str, ground_truth: str) -> float:
    # Implementation for completeness evaluation
    pass

def evaluate_clarity(self, prediction: str) -> float:
    # Implementation for clarity evaluation
    pass
```

## Metric Library Management

### Organizing Metrics
- **Categories**: Group related metrics together
- **Tags**: Add searchable tags for easy discovery
- **Descriptions**: Document what each metric measures and when to use it

### Sharing Metrics
- **Export**: Download metrics as Python files
- **Import**: Upload metrics from other environments
- **Templates**: Create reusable metric templates

### Version Control
- **Versioning**: Each save creates a new version
- **Rollback**: Revert to previous versions if needed
- **Comparison**: Compare different versions side by side

## Best Practices

### Metric Design Principles

#### Clear Objectives
- Define exactly what you want to measure
- Ensure the metric aligns with business goals
- Document the scoring rationale

#### Consistent Scoring
- Use 0.0 to 1.0 scale consistently
- Higher scores should always mean better performance
- Handle edge cases gracefully

#### Computational Efficiency
- Optimize for speed, especially for large datasets
- Use batch processing when possible
- Avoid expensive operations in tight loops

### Testing and Validation

#### Test with Real Data
```python
# Test with various scenarios
test_cases = [
    ("Perfect match", "Perfect match", 1.0),
    ("Close match", "Perfect match", 0.8),
    ("No match", "Perfect match", 0.0),
    ("", "Perfect match", 0.0),  # Empty prediction
    ("Something", "", 1.0),      # Empty ground truth
]

for prediction, ground_truth, expected in test_cases:
    score = apply(prediction, ground_truth)
    assert abs(score - expected) < 0.1, f"Failed for {prediction} vs {ground_truth}"
```

#### Edge Case Handling
- Empty strings
- Very long texts
- Special characters
- Non-English text (if applicable)
- Malformed input

### Performance Optimization

#### Batch Processing
```python
def batch_apply(self, predictions: List[str], ground_truths: List[str], **kwargs) -> List[float]:
    # Optimize for batch processing
    # Pre-compute expensive operations once
    
    preprocessed_truths = [self.preprocess(gt) for gt in ground_truths]
    
    scores = []
    for pred, preprocessed_gt in zip(predictions, preprocessed_truths):
        score = self.fast_evaluate(pred, preprocessed_gt)
        scores.append(score)
    
    return scores
```

#### Caching
```python
from functools import lru_cache

@lru_cache(maxsize=1000)
def expensive_computation(self, text: str) -> float:
    # Cache results of expensive computations
    pass
```

## Integration with Optimization

### Metric Selection
- Choose metrics that reflect your actual goals
- Consider using multiple metrics for comprehensive evaluation
- Weight metrics according to business importance

### Optimization Compatibility
- Some optimizers work better with certain metric types
- Smooth, differentiable metrics often work better
- Consider metric stability and noise

### Monitoring and Debugging
- Track metric scores during optimization
- Identify when metrics conflict with each other
- Debug unexpected metric behavior

## Troubleshooting

### Common Issues

#### Metric Returns Wrong Scores
1. Check the scoring scale (should be 0.0 to 1.0)
2. Verify the logic handles edge cases
3. Test with known examples

#### Performance Problems
1. Optimize expensive operations
2. Use batch processing
3. Add caching for repeated computations

#### Import/Export Errors
1. Check Python syntax
2. Verify required methods are implemented
3. Ensure dependencies are available

### Debugging Tips

#### Add Logging
```python
import logging

def apply(self, prediction: str, ground_truth: str, **kwargs) -> float:
    logging.debug(f"Evaluating: {prediction[:50]}... vs {ground_truth[:50]}...")
    
    score = self.compute_score(prediction, ground_truth)
    
    logging.debug(f"Score: {score}")
    return score
```

#### Validate Inputs
```python
def apply(self, prediction: str, ground_truth: str, **kwargs) -> float:
    assert isinstance(prediction, str), f"Prediction must be string, got {type(prediction)}"
    assert isinstance(ground_truth, str), f"Ground truth must be string, got {type(ground_truth)}"
    
    # Your metric logic here
    pass
```

For more help, see the [Troubleshooting Guide](./troubleshooting.md).