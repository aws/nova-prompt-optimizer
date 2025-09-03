"""
Flexible dataset generator that adapts to any output format
"""

import json
import boto3
import re
from typing import Dict, Any, List


class FlexibleGenerator:
    def __init__(self, region_name: str = "us-east-1", model_id: str = "us.amazon.nova-pro-v1:0"):
        self.bedrock = boto3.client('bedrock-runtime', region_name=region_name)
        self.model_id = model_id
    
    def get_format_description(self, format_content: str) -> str:
        """Get a concise description of the detected format"""
        if not format_content:
            return "Plain text"
        
        # Check if it's JSON
        if format_content.strip().startswith('{') and format_content.strip().endswith('}'):
            try:
                import json
                parsed = json.loads(format_content)
                keys = list(parsed.keys()) if isinstance(parsed, dict) else []
                if keys:
                    return f"JSON with fields: {', '.join(keys[:3])}{'...' if len(keys) > 3 else ''}"
                else:
                    return "JSON object"
            except:
                return "JSON-like structure"
        
        # Check if it's XML
        if '<' in format_content and '>' in format_content:
            return "XML structure"
        
        # Check length and provide appropriate description
        if len(format_content) > 100:
            return f"Structured format ({len(format_content)} chars)"
        else:
            return format_content
    
    def extract_output_format(self, prompt_content: str) -> str:
        """Extract the expected output format from the prompt"""
        
        # Look for XML structure
        xml_match = re.search(r'```xml\s*(.*?)\s*```', prompt_content, re.DOTALL | re.IGNORECASE)
        if xml_match:
            return xml_match.group(1).strip()
        
        # Look for JSON structure
        json_match = re.search(r'```json\s*(.*?)\s*```', prompt_content, re.DOTALL | re.IGNORECASE)
        if json_match:
            return json_match.group(1).strip()
        
        # Look for other code blocks
        code_match = re.search(r'```\w*\s*(.*?)\s*```', prompt_content, re.DOTALL)
        if code_match:
            return code_match.group(1).strip()
        
        # Look for "OUTPUT FORMAT:" section
        format_match = re.search(r'OUTPUT FORMAT:?\s*(.*?)(?=\n\n|\nIMPORTANT|\nNote|\Z)', prompt_content, re.DOTALL | re.IGNORECASE)
        if format_match:
            return format_match.group(1).strip()
        
        # Look for "format" or "structure" mentions
        format_keywords = re.search(r'(?:format|structure|template|example).*?:\s*(.*?)(?=\n\n|\nIMPORTANT|\nNote|\Z)', prompt_content, re.DOTALL | re.IGNORECASE)
        if format_keywords:
            return format_keywords.group(1).strip()
        
        return "No specific format found - use natural response"
    
    def generate_sample(self, prompt_content: str, sample_number: int = 1) -> Dict[str, Any]:
        """Generate a single sample that follows the exact format from the prompt"""
        
        # Extract the expected output format
        expected_format = self.extract_output_format(prompt_content)
        
        # Create generation prompt that emphasizes format compliance
        generation_prompt = f"""
You must follow this prompt EXACTLY as written:

{prompt_content}

Your task:
1. Generate a realistic input/question that fits the prompt's context
2. Respond using the EXACT format specified in the prompt above
3. Do not modify, simplify, or change the format in any way
4. Include all fields, attributes, and structure elements shown

Expected output format to follow:
{expected_format}

DIVERSITY REQUIREMENTS:
- Generate COMPLETELY DIFFERENT examples each time
- Use UNIQUE scenarios: electronics, clothing, books, food, services, software, etc.
- Vary customer types: new customers, returning customers, business customers, etc.
- Include different issue types: billing, shipping, quality, technical, returns, etc.
- Mix positive, negative, and neutral feedback
- Use different writing styles: formal, casual, frustrated, happy, confused, etc.
- Sample {sample_number} should be DISTINCTLY DIFFERENT from all previous samples
- Be creative - avoid common patterns like "damaged product" or "customer service"

Generate ONE unique training example as JSON:
{{"input": "realistic user input/question", "output": "your complete response as a single string in the exact format from the prompt"}}

CRITICAL: 
- The "output" field must be a STRING, not an object
- Your output string must match the format structure exactly as shown in the original prompt
- Include all XML tags, attributes, reasoning fields, etc. as specified
- MAKE THIS EXAMPLE #{sample_number} COMPLETELY UNIQUE AND DIFFERENT
"""
        
        try:
            response = self.bedrock.invoke_model(
                modelId=self.model_id,
                body=json.dumps({
                    "messages": [{"role": "user", "content": [{"text": generation_prompt}]}],
                    "inferenceConfig": {
                        "maxTokens": 3000,
                        "temperature": 0.7
                    }
                })
            )
            
            result = json.loads(response['body'].read())
            content = result['output']['message']['content'][0]['text']
            
            # Clean up response and handle control characters
            content = content.strip()
            if content.startswith('```json'):
                content = content[7:]
            if content.endswith('```'):
                content = content[:-3]
            content = content.strip()
            
            # Remove control characters that break JSON parsing
            import re
            content = re.sub(r'[\x00-\x1f\x7f-\x9f]', '', content)
            
            # Debug: Print what we're trying to parse
            print(f"🔍 DEBUG - Raw LLM response: {content}")
            
            # Parse JSON
            sample_data = json.loads(content)
            
            # Debug: Print what we got
            print(f"🔍 DEBUG - Raw sample_data: {sample_data}")
            print(f"🔍 DEBUG - Output type: {type(sample_data.get('output'))}")
            print(f"🔍 DEBUG - Output content: {sample_data.get('output')}")
            
            # Ensure output is a string, not an object
            output_value = sample_data.get('output')
            if isinstance(output_value, dict):
                # If output is a dict, convert to JSON string
                sample_data['output'] = json.dumps(output_value, indent=2)
                print(f"🔍 DEBUG - Converted dict to JSON string")
            elif isinstance(output_value, list):
                # If output is a list, convert to JSON string
                sample_data['output'] = json.dumps(output_value, indent=2)
                print(f"🔍 DEBUG - Converted list to JSON string")
            elif output_value is not None:
                # Ensure it's a string and clean up XML formatting
                output_str = str(output_value)
                
                # Fix malformed XML tags like <Application>Application</request_type>
                import re
                output_str = re.sub(r'<([^>]+)>\1</', r'<\1></', output_str)
                
                # Fix malformed nested tags like <frustrated>frustrated</sentiment>
                output_str = re.sub(r'<([^>]+)>[^<]*</([^>]+)>', lambda m: f'<{m.group(2)}></{m.group(2)}>' if m.group(1) != m.group(2) else m.group(0), output_str)
                
                # Clean up extra whitespace while preserving structure
                output_str = re.sub(r'\n\s*\n', '\n', output_str)  # Remove empty lines
                output_str = output_str.strip()
                
                sample_data['output'] = output_str
                print(f"🔍 DEBUG - Cleaned response formatting: {len(output_str)} chars")
            else:
                sample_data['output'] = "No output generated"
                print(f"🔍 DEBUG - No output found, using fallback")
            
            return {
                "success": True,
                "sample": sample_data,
                "detected_format": self.get_format_description(expected_format)
            }
            
        except Exception as e:
            error_msg = str(e)
            
            # Check for AWS authentication errors
            if "ExpiredTokenException" in error_msg or "expired" in error_msg.lower():
                return {
                    "success": False,
                    "error": "AWS credentials have expired. Please refresh your AWS credentials and try again.",
                    "error_type": "auth_expired",
                    "detected_format": self.get_format_description(expected_format)
                }
            elif "UnauthorizedOperation" in error_msg or "AccessDenied" in error_msg:
                return {
                    "success": False,
                    "error": "AWS authentication failed. Please check your AWS credentials and permissions.",
                    "error_type": "auth_failed",
                    "detected_format": self.get_format_description(expected_format)
                }
            elif "NoCredentialsError" in error_msg or "Unable to locate credentials" in error_msg:
                return {
                    "success": False,
                    "error": "AWS credentials not found. Please configure your AWS credentials.",
                    "error_type": "no_credentials",
                    "detected_format": self.get_format_description(expected_format)
                }
            else:
                return {
                    "success": False,
                    "error": error_msg,
                    "error_type": "general",
                    "detected_format": self.get_format_description(expected_format)
                }
    
    def generate_dataset(self, prompt_content: str, num_samples: int = 5) -> Dict[str, Any]:
        """Generate multiple samples"""
        samples = []
        errors = []
        detected_format = None
        
        print(f"🔍 DEBUG - Starting generation of {num_samples} samples")
        
        for i in range(num_samples):
            print(f"🔍 DEBUG - Generating sample {i+1}/{num_samples}")
            result = self.generate_sample(prompt_content, i + 1)
            
            if result["success"]:
                print(f"🔍 DEBUG - Sample {i+1} SUCCESS: {type(result['sample'])}")
                samples.append(result["sample"])
                if not detected_format:
                    detected_format = result["detected_format"]
            else:
                print(f"🔍 DEBUG - Sample {i+1} FAILED: {result['error']}")
                errors.append(f"Sample {i+1}: {result['error']}")
                if not detected_format and "detected_format" in result:
                    detected_format = result["detected_format"]
        
        print(f"🔍 DEBUG - Final results: {len(samples)} successful, {len(errors)} errors")
        
        return {
            "success": len(samples) > 0,
            "samples": samples,
            "errors": errors,
            "total_generated": len(samples),
            "detected_format": detected_format or "Could not detect format"
        }
