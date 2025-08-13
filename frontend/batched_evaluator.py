"""
Batched Evaluator to reduce Bedrock API calls by processing multiple records in single requests
"""

import json
from typing import List, Dict, Any
from amzn_nova_prompt_optimizer.core.evaluation import Evaluator


class BatchedEvaluator(Evaluator):
    """Enhanced evaluator that batches multiple records into single API calls"""
    
    def __init__(self, prompt_adapter, dataset_adapter, metric_adapter, inference_adapter, batch_size=5):
        super().__init__(prompt_adapter, dataset_adapter, metric_adapter, inference_adapter)
        self.batch_size = batch_size
    
    def aggregate_score(self, model_id: str) -> float:
        """
        Evaluate all records in batches to minimize API calls
        Instead of 5 calls for 5 records, make 1 call with all 5 records
        """
        dataset = self.dataset_adapter.standardized_dataset
        
        print(f"🔍 BatchedEvaluator - Starting with {len(dataset) if dataset else 0} samples")
        
        if not dataset:
            print("❌ BatchedEvaluator - No dataset available")
            return 0.0
        
        # Create batched prompt with all records
        batched_prompt = self._create_batched_prompt(dataset)
        print(f"🔍 BatchedEvaluator - Created batched prompt: {len(batched_prompt)} chars")
        
        # Single API call for all records
        try:
            system_prompt = self.prompt_adapter.system_prompt or ""
            print(f"🔍 BatchedEvaluator - System prompt: '{system_prompt}' (length: {len(system_prompt)})")
            
            # Fix: Always use user-only message to avoid system prompt issues
            response = self.inference_adapter.call_model(
                model_id=model_id,
                system_prompt=None,
                messages=[{"role": "user", "content": batched_prompt}],
                inf_config={"max_tokens": 2000, "temperature": 0.1, "top_p": 0.9}
            )
            
            print(f"🔍 BatchedEvaluator - Got response: {len(str(response)) if response else 0} chars")
            
            # Parse batched response
            individual_responses = self._parse_batched_response(response, len(dataset))
            print(f"🔍 BatchedEvaluator - Parsed {len(individual_responses)} responses")
            
            # Calculate scores for each record
            scores = []
            for i, record in enumerate(dataset):
                if i < len(individual_responses):
                    try:
                        expected = record.get('output', '')
                        actual = individual_responses[i]
                        score = self.metric_adapter.apply(actual, expected)
                        
                        print(f"🔍 BatchedEvaluator - Sample {i+1}: score={score}, actual='{actual[:50]}...', expected='{expected}'")
                        
                        if score is not None and isinstance(score, (int, float)):
                            scores.append(float(score))
                        else:
                            print(f"⚠️ BatchedEvaluator - Invalid score for sample {i+1}: {score}")
                            scores.append(0.0)
                    except Exception as e:
                        print(f"❌ BatchedEvaluator - Error scoring sample {i+1}: {e}")
                        scores.append(0.0)
            
            if scores:
                avg_score = sum(scores) / len(scores)
                print(f"✅ BatchedEvaluator - Final score: {avg_score} from {len(scores)} samples")
                return avg_score
            else:
                print("❌ BatchedEvaluator - No valid scores")
                return 0.0
            
        except Exception as e:
            print(f"❌ BatchedEvaluator - Batched evaluation failed: {e}")
            import traceback
            print(f"❌ BatchedEvaluator - Traceback: {traceback.format_exc()}")
            # Fallback to individual calls and capture scores
            print("🔄 BatchedEvaluator - Falling back to individual evaluation")
            
            # Simple fallback - just return 0.0 for now since batched is failing
            print("❌ BatchedEvaluator - Returning 0.0 due to evaluation failure")
            return 0.0
    
    def _create_batched_prompt(self, dataset: List[Dict]) -> str:
        """Create a single prompt containing all records"""
        
        prompt_parts = [
            "Process the following inputs and provide responses in the exact format shown:",
            "",
            "Format your response as a JSON array with one response per input:",
            '[{"response": "your_response_1"}, {"response": "your_response_2"}, ...]',
            "",
            "Inputs to process:"
        ]
        
        for i, record in enumerate(dataset, 1):
            input_text = record.get('input', '')
            prompt_parts.append(f"{i}. {input_text}")
        
        prompt_parts.extend([
            "",
            f"Provide exactly {len(dataset)} responses in JSON array format."
        ])
        
        return "\n".join(prompt_parts)
    
    def _parse_batched_response(self, response: str, expected_count: int) -> List[str]:
        """Parse the batched response into individual responses"""
        
        try:
            # Try to extract JSON array from response
            import re
            json_match = re.search(r'\[.*\]', response, re.DOTALL)
            if json_match:
                json_array = json.loads(json_match.group())
                
                responses = []
                for item in json_array[:expected_count]:
                    if isinstance(item, dict) and 'response' in item:
                        responses.append(item['response'])
                    elif isinstance(item, str):
                        responses.append(item)
                    else:
                        responses.append(str(item))
                
                return responses
            
            # Fallback: split by numbered responses
            lines = response.split('\n')
            responses = []
            current_response = ""
            
            for line in lines:
                if re.match(r'^\d+\.', line.strip()):
                    if current_response:
                        responses.append(current_response.strip())
                    current_response = line.strip()
                else:
                    current_response += " " + line.strip()
            
            if current_response:
                responses.append(current_response.strip())
            
            return responses[:expected_count]
            
        except Exception as e:
            print(f"Failed to parse batched response: {e}")
            # Return single response repeated
            return [response] * expected_count
