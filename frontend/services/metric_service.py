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
        
        
        from prompt_templates import get_metric_code_prompt
        prompt = get_metric_code_prompt(name, criteria)


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
            return cleaned_code
            
        except Exception as e:
            raise Exception(f"Nova Premier API call failed: {str(e)}")
        
        # Removed fallback code - only use AI-generated metrics
    
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
            print("  categories_true: " + str(categories_true) + " (type: " + str(type(categories_true)) + ")")
            print("  categories_pred: " + str(categories_pred) + " (type: " + str(type(categories_pred)) + ")")
            if isinstance(categories_true, dict) and isinstance(categories_pred, dict):
                correct = sum(
                    categories_true.get(k, False) == categories_pred.get(k, False)
                    for k in categories_true
                )
                {field_name}_score = correct / len(categories_true) if categories_true else 0.0
                print("  correct matches: " + str(correct) + " / " + str(len(categories_true)))
            else:
                {field_name}_score = 0.0
                print("  ❌ Type mismatch or missing data - score: 0.0")
            result["{field_name}_score"] = {field_name}_score
            weighted_scores.append({field_name}_score * {weight})""")
        
        field_validation = '\n'.join(field_checks)
        
        return f'''import json
import re
import numpy as np
import pandas as pd
from typing import Any, List, Dict
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score
from amzn_nova_prompt_optimizer.core.input_adapters.metric_adapter import MetricAdapter

class {class_name}(MetricAdapter):
    def parse_json(self, input_string: str):
        """Parse JSON directly without fallback logic"""
        return json.loads(input_string)

    def _calculate_metrics(self, y_pred: Any, y_true: Any) -> Dict:
        result = {{"is_valid_json": False}}
        weighted_scores = []


        try:
            y_true = y_true if isinstance(y_true, dict) else self.parse_json(y_true)
            y_pred = y_pred if isinstance(y_pred, dict) else self.parse_json(y_pred)
        except json.JSONDecodeError as e:
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
import numpy as np
import pandas as pd
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score
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
import numpy as np
import pandas as pd
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, cohen_kappa_score
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
        """Parse natural language description to scoring criteria - now fully dynamic"""
        
        criteria = {
            'dataset_format': 'json',  # Default - will be determined dynamically
            'scoring_fields': []
        }
        
        # Remove hardcoded patterns - let AI determine everything dynamically
        # The AI will analyze the description and determine appropriate format and fields
        
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
            
            for i, sample in enumerate(sample_data[:3]):  # Test first 3 samples
                try:
                    pred = sample.get('prediction', '')
                    truth = sample.get('ground_truth', '')
                    
                    
                    score = metric.apply(pred, truth)
                    
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
    
    def analyze_dataset_for_metrics(self, dataset_path: str, prompt_data: dict, sample_size: int = 100, focus_description: str = "") -> dict:
        """Analyze dataset and suggest appropriate metrics"""
        import pandas as pd
        import random
        
        try:
            # Sample dataset
            if dataset_path.endswith('.jsonl'):
                with open(dataset_path, 'r') as f:
                    data = [json.loads(line) for line in f]
                if len(data) > sample_size:
                    data = random.sample(data, sample_size)
                df = pd.DataFrame(data)
            else:
                df = pd.read_csv(dataset_path)
                if len(df) > sample_size:
                    df = df.sample(n=sample_size)
            
            # Analyze dataset structure
            dataset_analysis = f"""
Dataset Structure:
- Rows analyzed: {len(df)}
- Columns: {list(df.columns)}
- Data types: {df.dtypes.to_dict()}
- Sample data: {df.head(3).to_dict('records')}
"""
            
            # Create analysis prompt
            prompt_info = "No prompt provided - analyzing dataset only"
            if prompt_data:
                prompt_info = f"""
- Name: {prompt_data.get('name', 'N/A')}
- System Prompt: {prompt_data.get('system_prompt', 'N/A')}
- User Prompt: {prompt_data.get('user_prompt', 'N/A')}"""
            
            analysis_prompt = f"""
You are an expert in evaluation metrics for AI systems. Analyze the dataset and prompt to suggest multiple appropriate evaluation metrics.

DATASET ANALYSIS:
{dataset_analysis}

PROMPT INFORMATION:
{prompt_info}

FOCUS: {focus_description if focus_description else 'General evaluation'}

Based on this analysis, suggest 3-5 different evaluation metrics that would be appropriate. Consider:
- Data structure and types
- Task complexity (classification, generation, structured output, etc.)
- Output format requirements (JSON, XML, text, numeric)
- Evaluation granularity (field-level, overall, weighted)

AVAILABLE LIBRARIES (use these for advanced metrics):
- Standard: json, re, math, typing (built-in)
- Scientific: numpy (arrays, statistics, linear algebra)
- Data: pandas (dataframes, data manipulation)
- ML: sklearn.metrics (F1, precision, recall, kappa, etc.)

Prefer advanced implementations when appropriate for better accuracy and performance.

For each metric, provide:
1. Name
2. Description (technical explanation)
3. Plain_explanation (simple explanation of what it measures in THIS specific dataset)
4. Type (accuracy, similarity, classification, structured_validation, etc.)
5. Complexity (simple, moderate, complex)
6. Why it's suitable for this data/task

Return your response in this JSON format:
{{
    "dataset_summary": "Brief summary of the dataset and task",
    "task_type": "classification/regression/generation/structured_output/etc",
    "output_format_detected": "json/xml/text/numeric/mixed",
    "suggested_metrics": [
        {{
            "name": "Metric Name",
            "description": "Technical description of the metric",
            "plain_explanation": "Simple explanation of what this measures in your specific data (e.g., 'Checks if the AI correctly identified urgent vs non-urgent customer emails in your dataset')",
            "type": "accuracy/similarity/structured_validation/etc",
            "complexity": "simple/moderate/complex",
            "rationale": "Why this metric is suitable",
            "handles_format": "json/xml/text/numeric"
        }}
    ]
}}
"""
            
            # Generate analysis using AI
            response = self.bedrock.invoke_model(
                modelId="us.amazon.nova-premier-v1:0",
                body=json.dumps({
                    "messages": [{"role": "user", "content": [{"text": analysis_prompt}]}],
                    "inferenceConfig": {
                        "maxTokens": 1500,
                        "temperature": 0.1
                    }
                })
            )
            
            result = json.loads(response['body'].read())
            response_text = result['output']['message']['content'][0]['text']
            
            # Parse response
            try:
                analysis_result = json.loads(response_text.strip())
            except json.JSONDecodeError:
                json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
                if json_match:
                    analysis_result = json.loads(json_match.group())
                else:
                    return {"success": False, "error": "Could not parse AI analysis response"}
            
            return {
                "success": True,
                **analysis_result
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def generate_composite_metric_code(self, metrics: list, weights: list = None, original_prompt: str = None) -> str:
        """Generate composite metric using AI to create self-contained implementation"""
        print(f"🔍 DEBUG - Starting composite metric generation")
        print(f"🔍 DEBUG - metrics type: {type(metrics)}, value: {metrics}")
        print(f"🔍 DEBUG - weights type: {type(weights)}, value: {weights}")
        
        if not metrics:
            raise ValueError("At least one metric required for composite")
        
        if weights is None:
            weights = [1.0 / len(metrics)] * len(metrics)
            print(f"🔍 DEBUG - Generated default weights: {weights}")
        
        # Use AI to generate a proper composite metric
        from prompt_templates import PromptTemplates
        prompt_templates = PromptTemplates()
        
        print(f"🔍 DEBUG - About to analyze dataset structure")
        # Analyze dataset structure from a sample
        dataset_structure = self._analyze_dataset_structure(metrics)
        print(f"🔍 DEBUG - Dataset structure: {dataset_structure}")
        
        print(f"🔍 DEBUG - About to create composite prompt")
        # Create composite prompt
        composite_prompt = prompt_templates.get_composite_metric_prompt(metrics, weights, dataset_structure, original_prompt)
        print(f"🔍 DEBUG - Composite prompt created, length: {len(composite_prompt)}")
        
        try:
            # Generate composite metric code using Nova
            print(f"🔍 DEBUG - Calling Bedrock for composite metric generation")
            response = self.bedrock.invoke_model(
                modelId="us.amazon.nova-pro-v1:0",
                body=json.dumps({
                    "messages": [
                        {
                            "role": "user", 
                            "content": [{"text": composite_prompt}]
                        }
                    ],
                    "inferenceConfig": {
                        "maxTokens": 4000,
                        "temperature": 0.1
                    }
                })
            )
            
            response_body = json.loads(response['body'].read())
            generated_code = response_body['output']['message']['content'][0]['text']
            print(f"🔍 DEBUG - Generated code length: {len(generated_code)}")
            print(f"🔍 DEBUG - RAW BEDROCK OUTPUT:")
            print("=" * 80)
            print(generated_code)
            print("=" * 80)
            
            # Parse and clean the code before storing
            cleaned_code = self._parse_and_clean_code(generated_code)
            print(f"🔍 DEBUG - Cleaned code length: {len(cleaned_code)}")
            print(f"🔍 DEBUG - About to save to database")
            
            # Save the generated composite metric to database
            try:
                from database import Database
                db = Database()
                
                print(f"🔍 DEBUG - Database imported successfully")
                print(f"🔍 DEBUG - metrics type: {type(metrics)}, metrics: {metrics}")
                
                # Create a descriptive name for the composite metric
                if metrics and len(metrics) > 0:
                    print(f"🔍 DEBUG - Processing {len(metrics)} metrics")
                    metric_names = [m.get('name', f'Metric {i+1}') for i, m in enumerate(metrics)]
                    composite_name = f"Composite Metric: {', '.join(metric_names[:3])}"
                    if len(metric_names) > 3:
                        composite_name += f" (+{len(metric_names)-3} more)"
                    num_metrics = len(metrics)
                else:
                    print(f"🔍 DEBUG - No metrics or empty metrics")
                    composite_name = "Composite Metric"
                    num_metrics = 0
                
                print(f"🔍 DEBUG - About to save metric: {composite_name}")
                
                # Save to database
                metric_id = db.create_metric(
                    name=composite_name,
                    description=f"AI-generated composite metric combining {num_metrics} evaluation criteria",
                    dataset_format="JSON",
                    scoring_criteria="Composite scoring based on multiple weighted metrics",
                    generated_code=cleaned_code,
                    natural_language_input="Generated from multiple metric specifications"
                )
                
                print(f"✅ DEBUG - Saved composite metric to database with ID: {metric_id}")
                
            except Exception as db_error:
                print(f"❌ DEBUG - Database save error: {type(db_error).__name__}: {db_error}")
                import traceback
                traceback.print_exc()
                # Continue anyway since the code generation worked
            
            return cleaned_code
            
        except Exception as e:
            # Let the full traceback show
            raise e
            
    def _parse_and_clean_code(self, raw_code: str) -> str:
        """Parse and clean generated code, extracting only valid Python code"""
        
        # Simple approach - just clean the raw code
        extracted_code = raw_code
        
        # Remove markdown code block markers
        extracted_code = extracted_code.replace('```python', '').replace('```', '')
        
        # Clean up any extra text before/after the code
        lines = extracted_code.split('\n')
        code_lines = []
        in_code = False
        
        for line in lines:
            # Start collecting when we see imports or class definition
            if line.strip().startswith(('from ', 'import ', 'class CompositeMetric')):
                in_code = True
            
            if in_code:
                code_lines.append(line)
                
            # Stop after the instantiation line
            if 'metric_adapter = CompositeMetric()' in line:
                break
        
        extracted_code = '\n'.join(code_lines).strip()
        print(f"🔍 DEBUG - Extracted code using simple cleanup approach")
        
        print(f"🔍 DEBUG - EXTRACTED CODE:")
        print("=" * 40)
        print(extracted_code)
        print("=" * 40)
        
        # Validate the code has required components
        required_components = [
            'class CompositeMetric',
            'def parse_json',
            'def _calculate_metrics',
            'def apply',
            'def batch_apply',
            'metric_adapter = CompositeMetric()'
        ]
        
        missing_components = []
        for component in required_components:
            if component not in extracted_code:
                missing_components.append(component)
        
        if missing_components:
            error_msg = f"Generated code is missing required components: {missing_components}"
            print(f"❌ DEBUG - {error_msg}")
            raise ValueError(error_msg)
        
        # Check for forbidden imports
        forbidden_imports = ['sklearn', 'numpy', 'pandas', 'statsmodels', 'scipy']
        for forbidden in forbidden_imports:
            if f'import {forbidden}' in extracted_code or f'from {forbidden}' in extracted_code:
                error_msg = f"Generated code contains forbidden import: {forbidden}"
                print(f"❌ DEBUG - {error_msg}")
                raise ValueError(error_msg)
        
        # Final validation - try to compile the code
        try:
            compile(extracted_code, '<string>', 'exec')
            print(f"✅ DEBUG - Code compiles successfully")
        except SyntaxError as e:
            error_msg = f"Generated code has syntax errors: {e}. Line {e.lineno}: {e.text}"
            print(f"❌ DEBUG - {error_msg}")
            raise ValueError(error_msg)
        
        return extracted_code
        
    def _analyze_dataset_structure(self, metrics: list) -> dict:
        """Analyze dataset structure from actual uploaded data"""
        
        # Safety check for None metrics
        if not metrics:
            raise ValueError("No metrics provided for dataset structure analysis")
        
        # Get actual dataset from database/uploads
        try:
            from database import Database
            db = Database()
            
            # Try to find uploaded dataset file
            import os
            import json
            
            uploads_dir = "uploads"
            dataset_file = None
            
            # Look for uploaded dataset files
            if os.path.exists(uploads_dir):
                for filename in os.listdir(uploads_dir):
                    if filename.endswith('.jsonl') or filename.endswith('.json'):
                        dataset_file = os.path.join(uploads_dir, filename)
                        break
            
            if dataset_file and os.path.exists(dataset_file):
                print(f"🔍 DEBUG - Analyzing dataset structure from: {dataset_file}")
                
                # Read first few lines to analyze structure
                sample_data = []
                with open(dataset_file, 'r') as f:
                    for i, line in enumerate(f):
                        if i >= 3:  # Just need a few samples
                            break
                        try:
                            data = json.loads(line.strip())
                            sample_data.append(data)
                        except json.JSONDecodeError:
                            continue
                
                if sample_data:
                    # Analyze the actual data structure
                    first_sample = sample_data[0]
                    print(f"🔍 DEBUG - Sample data keys: {list(first_sample.keys())}")
                    
                    structure = {
                        "fields": list(first_sample.keys()),
                        "field_types": {},
                        "sample_structure": first_sample
                    }
                    
                    # Determine field types from actual data
                    for key, value in first_sample.items():
                        if isinstance(value, dict):
                            structure["field_types"][key] = "dict"
                        elif isinstance(value, list):
                            structure["field_types"][key] = "list"
                        elif isinstance(value, bool):
                            structure["field_types"][key] = "boolean"
                        elif isinstance(value, (int, float)):
                            structure["field_types"][key] = "number"
                        else:
                            structure["field_types"][key] = "string"
                    
                    print(f"🔍 DEBUG - Detected fields: {structure['fields']}")
                    print(f"🔍 DEBUG - Field types: {structure['field_types']}")
                    
                    return structure
            
            # Fallback to old method if no dataset file found
            print(f"🔍 DEBUG - No dataset file found, using metric-based analysis")
            
        except Exception as e:
            print(f"🔍 DEBUG - Dataset analysis failed: {e}, using metric-based analysis")
        
        # Original metric-based analysis as fallback
        structure = {
            "fields": [],
            "field_types": {},
            "sample_structure": {}
        }
        
        # Try to infer structure from metric names and descriptions
        for metric in metrics:
            name = metric.get('name', '')
            description = metric.get('description', '')
            
            # Look for common field patterns
            if 'categor' in name.lower() or 'categor' in description.lower():
                structure["fields"].append("categories")
                structure["field_types"]["categories"] = "dict"
                structure["sample_structure"]["categories"] = {"field1": True, "field2": False}
            
            if 'sentiment' in name.lower() or 'sentiment' in description.lower():
                structure["fields"].append("sentiment") 
                structure["field_types"]["sentiment"] = "string"
                structure["sample_structure"]["sentiment"] = "positive"
                
            if 'urgency' in name.lower() or 'urgency' in description.lower():
                structure["fields"].append("urgency")
                structure["field_types"]["urgency"] = "string" 
                structure["sample_structure"]["urgency"] = "high"
        
        # If no specific fields detected, fail with clear error
        if not structure["fields"]:
            raise ValueError("Could not detect dataset structure from metrics. Please provide more descriptive metric names/descriptions that indicate the data fields (e.g., 'sentiment', 'categories', 'urgency').")
        
        return structure
    
    def _generate_simple_composite(self, metrics: list, weights: list = None) -> str:
        """Fallback: Generate simple averaging composite metric"""
        if weights is None:
            weights = [1.0] * len(metrics)
        
        total_weight = sum(weights)
        normalized_weights = [w / total_weight for w in weights]
        
        return f'''import json
import re
import math
from typing import Any, List, Dict
from amzn_nova_prompt_optimizer.core.input_adapters.metric_adapter import MetricAdapter

# CompositeMetric class will be dynamically generated here when needed
'''

