export interface CustomMetric {
  id: string
  name: string
  description: string
  code: string
  created_at: string
  updated_at: string
  author?: string
  tags?: string[]
  is_public?: boolean
}

export interface MetricValidationResult {
  is_valid: boolean
  errors: string[]
  warnings: string[]
  detected_methods: string[]
  has_apply_method: boolean
  has_batch_apply_method: boolean
}

export interface MetricTestResult {
  success: boolean
  result?: number | Record<string, number>
  error?: string
  execution_time?: number
  test_cases_passed?: number
  test_cases_total?: number
}

export interface MetricTestCase {
  id: string
  name: string
  predictions: any[]
  ground_truth: any[]
  expected_result?: number | Record<string, number>
}

export interface MetricLibraryItem {
  id: string
  name: string
  description: string
  category: string
  tags: string[]
  usage_count: number
  rating: number
  is_builtin: boolean
  created_at: string
  author?: string
}

export interface MetricCreateRequest {
  name: string
  description: string
  code: string
  tags?: string[]
  is_public?: boolean
}

export interface MetricUpdateRequest {
  name?: string
  description?: string
  code?: string
  tags?: string[]
  is_public?: boolean
}

export interface MetricTestRequest {
  metric_id?: string
  code?: string
  test_cases: MetricTestCase[]
}

// Built-in metric categories
export enum MetricCategory {
  ACCURACY = 'accuracy',
  CLASSIFICATION = 'classification',
  REGRESSION = 'regression',
  TEXT_SIMILARITY = 'text_similarity',
  CUSTOM = 'custom',
  NLP = 'nlp',
  SENTIMENT = 'sentiment',
  ENTITY_EXTRACTION = 'entity_extraction'
}

// Python code templates for common metric patterns
export const METRIC_TEMPLATES = {
  basic_accuracy: `from typing import List, Any, Union
import numpy as np

class CustomAccuracyMetric:
    """
    A custom accuracy metric that compares predictions to ground truth.
    """
    
    def __init__(self, case_sensitive: bool = False):
        self.case_sensitive = case_sensitive
    
    def apply(self, prediction: Any, ground_truth: Any) -> float:
        """
        Apply the metric to a single prediction-ground truth pair.
        
        Args:
            prediction: The model's prediction
            ground_truth: The expected/correct answer
            
        Returns:
            float: Score between 0.0 and 1.0
        """
        if not self.case_sensitive:
            pred_str = str(prediction).lower().strip()
            truth_str = str(ground_truth).lower().strip()
        else:
            pred_str = str(prediction).strip()
            truth_str = str(ground_truth).strip()
            
        return 1.0 if pred_str == truth_str else 0.0
    
    def batch_apply(self, predictions: List[Any], ground_truths: List[Any]) -> float:
        """
        Apply the metric to a batch of predictions.
        
        Args:
            predictions: List of model predictions
            ground_truths: List of expected/correct answers
            
        Returns:
            float: Average score across all examples
        """
        if len(predictions) != len(ground_truths):
            raise ValueError("Predictions and ground truths must have the same length")
        
        scores = [self.apply(pred, truth) for pred, truth in zip(predictions, ground_truths)]
        return np.mean(scores)
`,

  classification_f1: `from typing import List, Any, Dict, Union
from sklearn.metrics import f1_score, precision_score, recall_score
import numpy as np

class F1ScoreMetric:
    """
    F1 Score metric for classification tasks.
    """
    
    def __init__(self, average: str = 'weighted', labels: List[str] = None):
        self.average = average
        self.labels = labels
    
    def apply(self, prediction: Any, ground_truth: Any) -> Dict[str, float]:
        """
        Apply F1 score to a single prediction (returns dict for consistency).
        """
        # For single predictions, we can't compute F1, so return binary accuracy
        pred_str = str(prediction).strip()
        truth_str = str(ground_truth).strip()
        accuracy = 1.0 if pred_str == truth_str else 0.0
        
        return {
            'accuracy': accuracy,
            'f1': accuracy,  # Single sample F1 approximation
            'precision': accuracy,
            'recall': accuracy
        }
    
    def batch_apply(self, predictions: List[Any], ground_truths: List[Any]) -> Dict[str, float]:
        """
        Apply F1 score to a batch of predictions.
        """
        if len(predictions) != len(ground_truths):
            raise ValueError("Predictions and ground truths must have the same length")
        
        # Convert to strings and clean
        pred_labels = [str(p).strip() for p in predictions]
        true_labels = [str(t).strip() for t in ground_truths]
        
        # Get unique labels if not provided
        if self.labels is None:
            unique_labels = sorted(list(set(pred_labels + true_labels)))
        else:
            unique_labels = self.labels
        
        # Calculate metrics
        f1 = f1_score(true_labels, pred_labels, average=self.average, labels=unique_labels, zero_division=0)
        precision = precision_score(true_labels, pred_labels, average=self.average, labels=unique_labels, zero_division=0)
        recall = recall_score(true_labels, pred_labels, average=self.average, labels=unique_labels, zero_division=0)
        accuracy = np.mean([p == t for p, t in zip(pred_labels, true_labels)])
        
        return {
            'f1': float(f1),
            'precision': float(precision),
            'recall': float(recall),
            'accuracy': float(accuracy)
        }
`,

  text_similarity: `from typing import List, Any, Union
import re
from difflib import SequenceMatcher

class TextSimilarityMetric:
    """
    Text similarity metric using various similarity measures.
    """
    
    def __init__(self, method: str = 'sequence_matcher', normalize: bool = True):
        self.method = method
        self.normalize = normalize
    
    def _clean_text(self, text: str) -> str:
        """Clean and normalize text."""
        if not isinstance(text, str):
            text = str(text)
        
        if self.normalize:
            # Convert to lowercase and remove extra whitespace
            text = re.sub(r'\s+', ' ', text.lower().strip())
            # Remove punctuation for similarity comparison
            text = re.sub(r'[^\w\s]', '', text)
        
        return text
    
    def _sequence_similarity(self, text1: str, text2: str) -> float:
        """Calculate similarity using SequenceMatcher."""
        return SequenceMatcher(None, text1, text2).ratio()
    
    def _jaccard_similarity(self, text1: str, text2: str) -> float:
        """Calculate Jaccard similarity of word sets."""
        words1 = set(text1.split())
        words2 = set(text2.split())
        
        if not words1 and not words2:
            return 1.0
        
        intersection = words1.intersection(words2)
        union = words1.union(words2)
        
        return len(intersection) / len(union) if union else 0.0
    
    def apply(self, prediction: Any, ground_truth: Any) -> float:
        """
        Apply similarity metric to a single prediction-ground truth pair.
        """
        pred_text = self._clean_text(str(prediction))
        truth_text = self._clean_text(str(ground_truth))
        
        if self.method == 'sequence_matcher':
            return self._sequence_similarity(pred_text, truth_text)
        elif self.method == 'jaccard':
            return self._jaccard_similarity(pred_text, truth_text)
        else:
            raise ValueError(f"Unknown similarity method: {self.method}")
    
    def batch_apply(self, predictions: List[Any], ground_truths: List[Any]) -> float:
        """
        Apply similarity metric to a batch of predictions.
        """
        if len(predictions) != len(ground_truths):
            raise ValueError("Predictions and ground truths must have the same length")
        
        similarities = [self.apply(pred, truth) for pred, truth in zip(predictions, ground_truths)]
        return sum(similarities) / len(similarities) if similarities else 0.0
`
} as const

export type MetricTemplate = keyof typeof METRIC_TEMPLATES