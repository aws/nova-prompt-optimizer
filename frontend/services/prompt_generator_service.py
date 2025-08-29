"""
Prompt Generator Service
Analyzes datasets and generates optimized prompts using Nova SDK best practices
"""

import json
import csv
import boto3
from typing import Dict, List, Any
from botocore.exceptions import ClientError


class PromptGeneratorService:
    """Service for generating optimized prompts from datasets"""
    
    def __init__(self, model_id: str = "us.amazon.nova-pro-v1:0"):
        self.model_id = model_id
        self.bedrock = boto3.client('bedrock-runtime')
    
    def generate_optimized_prompt(self, dataset_path: str, task_description: str, prompt_name: str) -> Dict[str, Any]:
        """Generate optimized prompt from dataset analysis"""
        
        try:
            # Analyze dataset
            dataset_analysis = self._analyze_dataset(dataset_path)
            
            # Generate optimized prompt using Nova SDK best practices
            prompt_result = self._generate_prompt_with_nova_practices(
                dataset_analysis, task_description, prompt_name
            )
            
            return {
                "success": True,
                "system_prompt": prompt_result["system_prompt"],
                "user_prompt": prompt_result["user_prompt"],
                "analysis": dataset_analysis
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def _analyze_dataset(self, dataset_path: str) -> Dict[str, Any]:
        """Analyze dataset structure and content"""
        
        analysis = {
            "columns": [],
            "sample_records": [],
            "patterns": {},
            "data_types": {}
        }
        
        try:
            with open(dataset_path, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                analysis["columns"] = reader.fieldnames or []
                
                # Get sample records (first 5)
                for i, row in enumerate(reader):
                    if i >= 5:
                        break
                    analysis["sample_records"].append(row)
                
                # Analyze patterns
                if analysis["sample_records"]:
                    for column in analysis["columns"]:
                        values = [row.get(column, "") for row in analysis["sample_records"]]
                        analysis["patterns"][column] = self._analyze_column_patterns(values)
                        
        except Exception as e:
            print(f"Error analyzing dataset: {e}")
            
        return analysis
    
    def _analyze_column_patterns(self, values: List[str]) -> Dict[str, Any]:
        """Analyze patterns in column values"""
        
        patterns = {
            "avg_length": sum(len(str(v)) for v in values) / len(values) if values else 0,
            "has_json": any(self._is_json(v) for v in values),
            "has_categories": len(set(values)) < len(values) * 0.8,
            "sample_values": values[:3]
        }
        
        return patterns
    
    def _is_json(self, value: str) -> bool:
        """Check if value is JSON"""
        try:
            json.loads(str(value))
            return True
        except:
            return False
    
    def _generate_prompt_with_nova_practices(self, analysis: Dict[str, Any], task_description: str, prompt_name: str) -> Dict[str, Any]:
        """Generate prompt using Nova SDK best practices"""
        
        generation_prompt = f"""
You are an expert prompt engineer specializing in Amazon Nova SDK optimization practices. 

Generate an optimized prompt for the following task:
TASK: {task_description}
PROMPT NAME: {prompt_name}

DATASET ANALYSIS:
- Columns: {', '.join(analysis.get('columns', []))}
- Sample Records: {json.dumps(analysis.get('sample_records', [])[:2], indent=2)}
- Data Patterns: {json.dumps(analysis.get('patterns', {}), indent=2)}

NOVA SDK BEST PRACTICES TO APPLY:
1. Use clear, specific instructions
2. Provide examples when beneficial
3. Structure output format explicitly
4. Use role-based prompting
5. Include error handling guidance
6. Optimize for consistency and accuracy

Generate a system prompt and user prompt that follows these practices:

REQUIREMENTS:
- System prompt should set context, role, and guidelines
- User prompt should include input variable placeholders like {{input}}
- Consider the data patterns and structure from the dataset
- Make it optimized for the specific task described
- Include output format specifications if needed

Return your response in this exact JSON format:
{{
    "system_prompt": "Your optimized system prompt here",
    "user_prompt": "Your optimized user prompt with {{input}} placeholder here",
    "reasoning": "Brief explanation of optimization choices"
}}
"""
        
        try:
            response_text = self._call_bedrock(generation_prompt)
            
            # Parse JSON response
            response_data = json.loads(response_text.strip())
            
            return {
                "system_prompt": response_data.get("system_prompt", ""),
                "user_prompt": response_data.get("user_prompt", ""),
                "reasoning": response_data.get("reasoning", "")
            }
            
        except Exception as e:
            # Fallback to basic prompt structure
            return {
                "system_prompt": f"You are an AI assistant specialized in {task_description}. Provide accurate, helpful responses based on the input provided.",
                "user_prompt": "Please analyze the following input and provide your response: {input}",
                "reasoning": f"Fallback prompt due to generation error: {str(e)}"
            }
    
    def _call_bedrock(self, prompt: str) -> str:
        """Call Bedrock API"""
        
        try:
            response = self.bedrock.invoke_model(
                modelId=self.model_id,
                body=json.dumps({
                    "messages": [{"role": "user", "content": [{"text": prompt}]}],
                    "inferenceConfig": {
                        "maxTokens": 2000,
                        "temperature": 0.7
                    }
                })
            )
            
            response_body = json.loads(response['body'].read())
            return response_body['output']['message']['content'][0]['text']
            
        except ClientError as e:
            print(f"Bedrock API error: {e}")
            raise
        except Exception as e:
            print(f"Unexpected error calling Bedrock: {e}")
            raise
