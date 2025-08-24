"""
Simple dataset generator - no complexity, just works
"""

import json
import boto3
from typing import Dict, Any


class SimpleDatasetGenerator:
    def __init__(self, region_name: str = "us-east-1"):
        self.bedrock = boto3.client('bedrock-runtime', region_name=region_name)
        self.model_id = "us.amazon.nova-pro-v1:0"
    
    def generate_sample(self, prompt_content: str, sample_number: int = 1) -> Dict[str, Any]:
        """Generate a single training sample using the exact prompt format"""
        
        # Simple prompt - just ask for what we want
        generation_prompt = f"""
        You are following this exact prompt:
        
        {prompt_content}
        
        Generate 1 realistic training example. Create a user question and respond exactly as specified in the prompt above.
        
        Return only JSON in this format:
        {{"input": "user question here", "output": "your response in the exact format specified in the prompt"}}
        """
        
        try:
            response = self.bedrock.invoke_model(
                modelId=self.model_id,
                body=json.dumps({
                    "messages": [{"role": "user", "content": [{"text": generation_prompt}]}],
                    "inferenceConfig": {
                        "maxTokens": 2000,
                        "temperature": 0.7
                    }
                })
            )
            
            result = json.loads(response['body'].read())
            content = result['output']['message']['content'][0]['text']
            
            # Extract JSON from response
            content = content.strip()
            if content.startswith('```json'):
                content = content[7:]
            if content.endswith('```'):
                content = content[:-3]
            content = content.strip()
            
            # Parse the JSON
            sample_data = json.loads(content)
            
            return {
                "success": True,
                "sample": sample_data
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def generate_dataset(self, prompt_content: str, num_samples: int = 5) -> Dict[str, Any]:
        """Generate multiple samples"""
        samples = []
        errors = []
        
        for i in range(num_samples):
            result = self.generate_sample(prompt_content, i + 1)
            
            if result["success"]:
                samples.append(result["sample"])
            else:
                errors.append(f"Sample {i+1}: {result['error']}")
        
        return {
            "success": len(samples) > 0,
            "samples": samples,
            "errors": errors,
            "total_generated": len(samples)
        }
