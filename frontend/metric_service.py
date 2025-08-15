"""
Metric Service - Code generation using Amazon Nova Premier for custom metrics
"""

import json
import re
import boto3
from typing import Dict, List, Any


class MetricService:
    """Service for generating custom MetricAdapter implementations using Nova Premier"""
    
    def __init__(self):
        import botocore.config
        config = botocore.config.Config(
            read_timeout=30,
            connect_timeout=10,
            retries={'max_attempts': 2}
        )
        self.bedrock = boto3.client('bedrock-runtime', config=config)
    
    def generate_metric_code(self, name: str, criteria: Dict, model_id: str = "us.amazon.nova-premier-v1:0", rate_limit: int = 60) -> str:
        """Generate MetricAdapter subclass code using Amazon Nova Premier"""
        
        print(f"🛠️ MetricService - Generating code for: {name}")
        print(f"🤖 Using model: {model_id}, Rate limit: {rate_limit} RPM")
        
        from prompt_templates import get_metric_code_prompt
        prompt = get_metric_code_prompt(name, criteria)

        print(f"📝 Prompt created: {len(prompt)} characters")

        try:
            print("📤 Sending request to Bedrock for code generation...")
            
            response = self.bedrock.invoke_model(
                modelId=model_id,
                body=json.dumps({
                    "messages": [{"role": "user", "content": [{"text": prompt}]}],
                    "inferenceConfig": {
                        "maxTokens": 1000,
                        "temperature": 0.1
                    }
                })
            )
            
            print("📥 Received response from Bedrock")
            result = json.loads(response['body'].read())
            generated_code = result['output']['message']['content'][0]['text']
            
            # Clean the generated code by removing markdown formatting
            cleaned_code = self._clean_generated_code(generated_code)
            print(f"✅ Code generation successful: {len(cleaned_code)} characters")
            return cleaned_code
            
        except Exception as e:
            print(f"❌ MetricService error: {str(e)}")
            print(f"❌ Error type: {type(e)}")
            raise Exception(f"Nova Premier API call failed: {str(e)}")
        
        class_name = f"Generated{name.replace(' ', '')}Metric"
        dataset_format = criteria.get('dataset_format', 'json')
        scoring_fields = criteria.get('scoring_fields', [])
        
        if dataset_format == 'json':
            return self._generate_json_metric(class_name, scoring_fields)
        elif dataset_format == 'text':
            return self._generate_text_metric(class_name, criteria)
        else:
            return self._generate_basic_metric(class_name)
    
    def _clean_generated_code(self, raw_code: str) -> str:
        """Clean generated code by removing markdown formatting"""
        # Remove markdown code blocks
        code = re.sub(r'```python\s*\n?', '', raw_code)
        code = re.sub(r'```\s*$', '', code)
        code = re.sub(r'^```\s*\n?', '', code)
        
        # Remove any remaining markdown artifacts
        code = re.sub(r'^\s*```.*?\n', '', code, flags=re.MULTILINE)
        code = re.sub(r'\n\s*```\s*$', '', code)
        
        # Remove dummy MetricAdapter class definition if present
        code = re.sub(r'class MetricAdapter:\s*\n\s*pass\s*\n\s*', '', code)
        
        return code.strip()
    
    def _generate_json_metric(self, class_name: str, scoring_fields: List[Dict]) -> str:
        """Generate JSON-based metric adapter"""
        
        # Build field validation logic
        field_checks = []
        for field in scoring_fields:
            field_name = field['name']
            field_type = field.get('type', 'exact_match')
            weight = field.get('weight', 1.0)
            
            if field_type == 'exact_match':
                field_checks.append(f"""
            # {field_name} field validation
            {field_name}_correct = y_pred.get("{field_name}", "") == y_true.get("{field_name}", "")
            result["{field_name}_correct"] = {field_name}_correct
            weighted_scores.append(float({field_name}_correct) * {weight})""")
            
            elif field_type == 'categories':
                field_checks.append(f"""
            # {field_name} categories validation
            categories_true = y_true.get("{field_name}", {{}})
            categories_pred = y_pred.get("{field_name}", {{}})
            if isinstance(categories_true, dict) and isinstance(categories_pred, dict):
                correct = sum(
                    categories_true.get(k, False) == categories_pred.get(k, False)
                    for k in categories_true
                )
                {field_name}_score = correct / len(categories_true) if categories_true else 0.0
            else:
                {field_name}_score = 0.0
            result["{field_name}_score"] = {field_name}_score
            weighted_scores.append({field_name}_score * {weight})""")
        
        field_validation = '\n'.join(field_checks)
        
        return f'''import json
import re
from typing import Any, List, Dict
from amzn_nova_prompt_optimizer.core.input_adapters.metric_adapter import MetricAdapter

class {class_name}(MetricAdapter):
    def parse_json(self, input_string: str):
        """Parse JSON with fallback to code block extraction"""
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
        result = {{"is_valid_json": False}}
        weighted_scores = []

        try:
            y_true = y_true if isinstance(y_true, dict) else self.parse_json(y_true)
            y_pred = y_pred if isinstance(y_pred, dict) else self.parse_json(y_pred)
        except json.JSONDecodeError:
            result["total"] = 0.0
            return result

        if isinstance(y_pred, str):
            result["total"] = 0.0
            return result

        result["is_valid_json"] = True
        {field_validation}
        
        # Calculate total weighted score
        result["total"] = sum(weighted_scores) / len(weighted_scores) if weighted_scores else 0.0
        return result

    def apply(self, y_pred: Any, y_true: Any):
        metrics = self._calculate_metrics(y_pred, y_true)
        return metrics["total"]

    def batch_apply(self, y_preds: List[Any], y_trues: List[Any]):
        evals = [self.apply(y_pred, y_true) for y_pred, y_true in zip(y_preds, y_trues)]
        return sum(evals) / len(evals) if evals else 0.0
'''
    
    def _generate_text_metric(self, class_name: str, criteria: Dict) -> str:
        """Generate text-based metric adapter with granular scoring"""
        
        return f'''from typing import Any, List
import re
import math
from amzn_nova_prompt_optimizer.core.input_adapters.metric_adapter import MetricAdapter

class {class_name}(MetricAdapter):
    def apply(self, y_pred: Any, y_true: Any):
        """Granular text matching metric"""
        pred_str = str(y_pred).strip().lower()
        true_str = str(y_true).strip().lower()
        
        if pred_str == true_str:
            return 1.0
        
        # Calculate similarity for partial credit
        if not pred_str or not true_str:
            return 0.0
            
        # Jaccard similarity for word overlap
        pred_words = set(pred_str.split())
        true_words = set(true_str.split())
        
        if not pred_words and not true_words:
            return 1.0
        if not pred_words or not true_words:
            return 0.0
            
        intersection = len(pred_words.intersection(true_words))
        union = len(pred_words.union(true_words))
        jaccard = intersection / union if union > 0 else 0.0
        
        # Length penalty for very different lengths
        len_ratio = min(len(pred_str), len(true_str)) / max(len(pred_str), len(true_str))
        length_penalty = math.sqrt(len_ratio)
        
        # Combine scores with granular precision
        final_score = (jaccard * 0.7 + length_penalty * 0.3)
        return round(final_score, 3)

    def batch_apply(self, y_preds: List[Any], y_trues: List[Any]):
        evals = [self.apply(y_pred, y_true) for y_pred, y_true in zip(y_preds, y_trues)]
        return sum(evals) / len(evals) if evals else 0.0
'''
    
    def _generate_basic_metric(self, class_name: str) -> str:
        """Generate basic fallback metric with granular scoring"""
        
        return f'''from typing import Any, List
import json
import math
from amzn_nova_prompt_optimizer.core.input_adapters.metric_adapter import MetricAdapter

class {class_name}(MetricAdapter):
    def apply(self, y_pred: Any, y_true: Any):
        """Basic metric with granular scoring"""
        if y_pred == y_true:
            return 1.0
            
        # Try string comparison with similarity
        pred_str = str(y_pred).strip()
        true_str = str(y_true).strip()
        
        if pred_str == true_str:
            return 1.0
        
        if not pred_str or not true_str:
            return 0.0
            
        # Calculate character-level similarity
        max_len = max(len(pred_str), len(true_str))
        if max_len == 0:
            return 1.0
            
        # Simple edit distance approximation
        common_chars = sum(1 for a, b in zip(pred_str, true_str) if a == b)
        similarity = common_chars / max_len
        
        # Apply exponential scaling for more granular scores
        granular_score = math.pow(similarity, 2)
        return round(granular_score, 3)

    def batch_apply(self, y_preds: List[Any], y_trues: List[Any]):
        evals = [self.apply(y_pred, y_true) for y_pred, y_true in zip(y_preds, y_trues)]
        return sum(evals) / len(evals) if evals else 0.0
'''
    
    def parse_natural_language(self, description: str) -> Dict:
        """Parse natural language description to scoring criteria"""
        
        criteria = {
            'dataset_format': 'json',  # Default
            'scoring_fields': []
        }
        
        description_lower = description.lower()
        
        # Detect format
        if 'json' in description_lower:
            criteria['dataset_format'] = 'json'
        elif 'text' in description_lower or 'classification' in description_lower:
            criteria['dataset_format'] = 'text'
        
        # Extract field names and types
        field_patterns = [
            (r'sentiment.*?(?:accuracy|correct)', {'name': 'sentiment', 'type': 'exact_match', 'weight': 1.0}),
            (r'urgency.*?(?:accuracy|correct)', {'name': 'urgency', 'type': 'exact_match', 'weight': 1.0}),
            (r'categor(?:y|ies).*?(?:accuracy|correct)', {'name': 'categories', 'type': 'categories', 'weight': 1.0}),
            (r'format.*?validation', {'name': 'format', 'type': 'json_validation', 'weight': 0.3}),
        ]
        
        for pattern, field_config in field_patterns:
            if re.search(pattern, description_lower):
                criteria['scoring_fields'].append(field_config)
        
        # If no specific fields found, create a generic one
        if not criteria['scoring_fields']:
            criteria['scoring_fields'] = [
                {'name': 'output', 'type': 'exact_match', 'weight': 1.0}
            ]
        
        return criteria
    
    def validate_metric_code(self, code: str) -> bool:
        """Validate generated metric code"""
        try:
            # Basic syntax check
            compile(code, '<string>', 'exec')
            
            # Check for required methods
            required_methods = ['apply', 'batch_apply']
            for method in required_methods:
                if f'def {method}(' not in code:
                    return False
            
            return True
        except SyntaxError:
            return False
    
    def test_metric(self, code: str, sample_data: List[Dict]) -> Dict:
        """Test metric with sample data"""
        try:
            # Execute the generated code
            namespace = {}
            exec(code, namespace)
            
            # Find the metric class
            metric_class = None
            for name, obj in namespace.items():
                if name.startswith('Generated') and name.endswith('Metric'):
                    metric_class = obj
                    break
            
            if not metric_class:
                return {'error': 'No metric class found in generated code'}
            
            # Test with sample data
            metric = metric_class()
            results = []
            
            for sample in sample_data[:3]:  # Test first 3 samples
                try:
                    score = metric.apply(sample.get('prediction', ''), sample.get('ground_truth', ''))
                    results.append({
                        'input': sample,
                        'score': score,
                        'success': True
                    })
                except Exception as e:
                    results.append({
                        'input': sample,
                        'error': str(e),
                        'success': False
                    })
            
            return {
                'success': True,
                'results': results,
                'class_name': metric_class.__name__
            }
            
        except Exception as e:
            return {'error': f'Failed to test metric: {str(e)}'}
