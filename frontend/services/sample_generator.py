"""
Sample generation service for AI dataset creation.
Generates initial samples, processes annotations, and handles iterative refinement.
"""

import json
import boto3
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from botocore.exceptions import ClientError
from pydantic import BaseModel, Field

class GeneratedSample(BaseModel):
    """Flexible model for LLM-generated sample records"""
    input: str = Field(..., description="The user's input/question")
    output: Any = Field(..., description="The AI's response in the specified format (can be string, dict, or list)")
    
    def get_output_as_string(self) -> str:
        """Convert output to string format for consistency"""
        if isinstance(self.output, str):
            return self.output
        elif isinstance(self.output, (dict, list)):
            return json.dumps(self.output, indent=2, ensure_ascii=False)
        else:
            return str(self.output)
    
    @classmethod
    def from_llm_response(cls, response_data: Dict[str, Any]) -> 'GeneratedSample':
        """Create GeneratedSample from LLM response with flexible output handling"""
        input_text = response_data.get('input', '')
        output_data = response_data.get('output', '')
        
        # Handle cases where output might be nested or formatted differently
        if isinstance(output_data, dict):
            # If output is a dict, keep it as is (our model now supports this)
            return cls(input=input_text, output=output_data)
        elif isinstance(output_data, str):
            # If output is already a string, use it directly
            return cls(input=input_text, output=output_data)
        else:
            # Convert other types to string
            return cls(input=input_text, output=str(output_data))


@dataclass
class SampleRecord:
    """Individual sample record with annotation support"""
    id: str
    input_text: str
    answer_text: str
    annotations: List[str] = None
    quality_score: float = 0.0
    
    def __post_init__(self):
        if self.annotations is None:
            self.annotations = []


@dataclass
class GenerationSession:
    """Tracks sample generation and iteration state"""
    session_id: str
    samples: List[SampleRecord]
    generation_prompt: str
    iteration_count: int = 0
    feedback_summary: str = ""


class SampleGeneratorService:
    """Service for generating and refining dataset samples"""
    
    def __init__(self, region_name: str = "us-east-1"):
        self.bedrock = boto3.client('bedrock-runtime', region_name=region_name)
        self.model_id = "us.amazon.nova-premier-v1:0"
        self.sessions: Dict[str, GenerationSession] = {}
    
    def generate_unique_questions(self, checklist, model_id: str) -> Dict[str, Any]:
        """Generate 5 unique questions for the dataset"""
        try:
            prompt = f"""
            Generate 5 unique, varied technology support questions from senior citizens.
            
            Context:
            - Role: {checklist.role_persona}
            - Domain: {checklist.domain_expertise}
            - Input Type: {checklist.input_format}
            
            Create 5 different questions covering various tech issues:
            1. WiFi/Internet connectivity
            2. Email problems
            3. Printing issues
            4. Software/application troubles
            5. Computer hardware concerns
            
            Make each question realistic and varied in:
            - Problem type
            - Language style
            - Level of detail
            - Emotional tone
            
            Return JSON array: ["question 1", "question 2", "question 3", "question 4", "question 5"]
            """
            
            response = self._call_bedrock_with_model(prompt, model_id)
            
            try:
                # Remove markdown if present
                response_text = response.strip()
                if response_text.startswith('```json'):
                    response_text = response_text[7:]
                if response_text.endswith('```'):
                    response_text = response_text[:-3]
                response_text = response_text.strip()
                
                questions = json.loads(response_text, strict=False)
                
                if isinstance(questions, list) and len(questions) == 5:
                    return {
                        "success": True,
                        "questions": questions
                    }
                else:
                    return {"success": False, "error": "Invalid questions format"}
                    
            except json.JSONDecodeError as e:
                print(f"JSON decode error: {e}")
                return {"success": False, "error": f"Invalid JSON response: {str(e)}"}
                
        except Exception as e:
            print(f"Error generating questions: {e}")
            return {"success": False, "error": str(e)}
    
    def process_question_to_sample(self, checklist, question: str, model_id: str, sample_number: int) -> Dict[str, Any]:
        """Process a single question to generate the complete XML response"""
        try:
            print(f"🔍 DEBUG - Processing question: {repr(question)} (type: {type(question)})")
            
            # Ensure question is a string
            question_str = str(question) if question else "No question provided"
            
            prompt = f"""
            You are a {checklist.role_persona} responding to this user question:
            
            USER QUESTION: {question_str}
            
            Analyze this question and respond using the exact format specified in the requirements:
            
            {output_format_text}
            
            Return JSON: {{"input": "{question_str}", "output": "complete response in the exact format specified above"}}
            """
            
            response = self._call_bedrock_with_model(prompt, model_id)
            
            try:
                # Remove markdown if present
                response_text = response.strip()
                if response_text.startswith('```json'):
                    response_text = response_text[7:]
                if response_text.endswith('```'):
                    response_text = response_text[:-3]
                response_text = response_text.strip()
                
                sample_data = json.loads(response_text, strict=False)
                validated_sample = GeneratedSample(**sample_data)
                
                return {
                    "success": True,
                    "sample": validated_sample.model_dump()
                }
                
            except json.JSONDecodeError as e:
                print(f"JSON decode error: {e}")
                return {"success": False, "error": f"Invalid JSON response: {str(e)}"}
            except Exception as e:
                print(f"Validation error: {e}")
                return {"success": False, "error": f"Invalid sample format: {str(e)}"}
                
        except Exception as e:
            print(f"Error processing question: {e}")
            return {"success": False, "error": str(e)}
    
    def generate_single_sample_from_checklist(self, checklist, model_id: str, sample_number: int) -> Dict[str, Any]:
        """Generate a single sample record from checklist"""
        try:
            # Extract actual format from the output format description
            output_format_text = str(checklist.output_format)
            print(f"🔍 DEBUG - Output format text: {output_format_text}")
            
            prompt = f"""
            Generate a training sample for IT support evaluation.
            
            Context: {checklist.role_persona}
            Task: {checklist.task_goal}
            Domain: {checklist.domain_expertise}
            
            Output format required: {output_format_text}
            
            Create 1 unique tech support question and respond using the EXACT format specified above.
            
            Return JSON: {{"input": "realistic user tech question", "output": "complete response in the exact format specified"}}
            
            IMPORTANT:
            - Generate varied questions: WiFi, email, printing, software, hardware
            - Use the EXACT output format structure from the requirements
            - Include all required fields and reasoning elements
            - Make each question unique (sample #{sample_number})
            """
            
            # Call Bedrock with specified model
            response = self._call_bedrock_with_model(prompt, model_id)
            print(f"🔍 DEBUG - Raw LLM response: '{response}'")
            
            # Parse the response using Pydantic model
            try:
                response_text = response.strip()
                if not response_text:
                    return {"success": False, "error": "Empty response from LLM"}
                
                # Remove markdown code blocks if present
                if '```json' in response_text:
                    # Extract JSON from between ```json and ```
                    start = response_text.find('```json') + 7
                    end = response_text.find('```', start)
                    if end != -1:
                        response_text = response_text[start:end].strip()
                    else:
                        response_text = response_text[start:].strip()
                elif response_text.startswith('```json'):
                    response_text = response_text[7:]  # Remove ```json
                    if response_text.endswith('```'):
                        response_text = response_text[:-3]  # Remove ```
                
                response_text = response_text.strip()
                
                # Parse JSON with proper handling of control characters
                sample_data = json.loads(response_text, strict=False)
                
                # Use the flexible factory method to handle complex output structures
                validated_sample = GeneratedSample.from_llm_response(sample_data)
                
                # Convert to dict with proper output handling
                sample_dict = validated_sample.model_dump()
                
                # Always provide a string version for compatibility
                sample_dict['output_string'] = validated_sample.get_output_as_string()
                
                return {
                    "success": True,
                    "sample": sample_dict
                }
            except json.JSONDecodeError as e:
                print(f"JSON decode error: {e}")
                print(f"Raw response was: '{response}'")
                return {"success": False, "error": f"Invalid JSON response: {str(e)}"}
            except Exception as e:
                print(f"Validation error: {e}")
                return {"success": False, "error": f"Invalid sample format: {str(e)}"}
            
        except Exception as e:
            print(f"Error generating single sample: {e}")
            return {"success": False, "error": str(e)}
    
    def generate_single_sample(self, session_id: str, model_id: str, sample_number: int) -> Dict[str, Any]:
        """Generate a single sample record"""
        try:
            # Get session data
            session_data = self.sessions.get(session_id)
            if not session_data:
                return {"success": False, "error": "Session not found"}
            
            # Create a simple prompt for single sample generation
            prompt = f"""
            Generate 1 sample record for this dataset:
            
            Role: {session_data.checklist.role_persona}
            Task: {session_data.checklist.task_goal}
            Input Format: {session_data.checklist.input_format}
            Output Format: {session_data.checklist.output_format}
            Domain: {session_data.checklist.domain_expertise}
            
            Generate exactly 1 realistic sample with:
            - input: [realistic input example]
            - output: [expected output following the specified format]
            
            Return as JSON: {{"input": "...", "output": "..."}}
            """
            
            # Call Bedrock with specified model
            response = self._call_bedrock_with_model(prompt, model_id)
            
            # Parse the response
            import json
            try:
                sample_data = json.loads(response.strip())
                return {
                    "success": True,
                    "sample": sample_data
                }
            except json.JSONDecodeError:
                # Fallback parsing
                return {
                    "success": True,
                    "sample": {
                        "input": f"Sample input {sample_number}",
                        "output": response.strip()
                    }
                }
            
        except Exception as e:
            print(f"Error generating single sample: {e}")
            return {"success": False, "error": str(e)}
    
    def _call_bedrock_with_model(self, prompt: str, model_id: str) -> str:
        """Call Bedrock with specific model"""
        try:
            response = self.bedrock.invoke_model(
                modelId=model_id,
                body=json.dumps({
                    "messages": [{"role": "user", "content": [{"text": prompt}]}],
                    "inferenceConfig": {
                        "maxTokens": 2000,
                        "temperature": 0.7
                    }
                })
            )
            
            result = json.loads(response['body'].read())
            content = result['output']['message']['content'][0]['text']
            
            # Check if response is empty or too short
            if not content or len(content.strip()) < 10:
                print(f"Warning: Short or empty response: '{content}'")
                return ""
            
            return content
            
        except Exception as e:
            print(f"Error calling Bedrock: {e}")
            return ""
    
    def generate_initial_samples(self, generation_config: Dict[str, Any], session_id: str) -> Dict[str, Any]:
        """Generate initial 5 samples based on requirements"""
        
        generation_prompt = generation_config.get('generation_prompt', '')
        
        try:
            # Generate samples using AI
            samples_text = self._call_bedrock(generation_prompt)
            
            # Parse generated samples
            samples = self._parse_generated_samples(samples_text, session_id)
            
            # Create generation session
            session = GenerationSession(
                session_id=session_id,
                samples=samples,
                generation_prompt=generation_prompt
            )
            self.sessions[session_id] = session
            
            return {
                "success": True,
                "session_id": session_id,
                "samples": [self._sample_to_dict(sample) for sample in samples],
                "generation_prompt": generation_prompt
            }
            
        except Exception as e:
            print(f"Error generating samples: {e}")
            return {
                "success": False,
                "error": str(e),
                "samples": []
            }
    
    def process_annotations(self, session_id: str, sample_annotations: Dict[str, List[str]]) -> Dict[str, Any]:
        """Process user annotations and generate improved samples"""
        
        if session_id not in self.sessions:
            return {"success": False, "error": "Session not found"}
        
        session = self.sessions[session_id]
        
        # Update samples with annotations
        for sample in session.samples:
            if sample.id in sample_annotations:
                sample.annotations = sample_annotations[sample.id]
        
        # Generate feedback summary
        feedback_summary = self._analyze_annotations(session.samples)
        session.feedback_summary = feedback_summary
        
        # Generate improved prompt
        improved_prompt = self._create_improved_prompt(session)
        
        try:
            # Generate new samples with improvements
            improved_samples_text = self._call_bedrock(improved_prompt)
            improved_samples = self._parse_generated_samples(improved_samples_text, session_id, iteration=session.iteration_count + 1)
            
            # Update session
            session.samples = improved_samples
            session.iteration_count += 1
            session.generation_prompt = improved_prompt
            
            return {
                "success": True,
                "session_id": session_id,
                "samples": [self._sample_to_dict(sample) for sample in improved_samples],
                "feedback_summary": feedback_summary,
                "iteration": session.iteration_count
            }
            
        except Exception as e:
            print(f"Error processing annotations: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def generate_full_dataset(self, session_id: str, num_records: int, output_format: str) -> Dict[str, Any]:
        """Generate full dataset based on refined samples"""
        
        if session_id not in self.sessions:
            return {"success": False, "error": "Session not found"}
        
        session = self.sessions[session_id]
        
        # Create batch generation prompt
        batch_prompt = self._create_batch_generation_prompt(session, num_records)
        
        try:
            # Generate full dataset
            dataset_text = self._call_bedrock(batch_prompt)
            
            # Parse and format dataset
            dataset_records = self._parse_dataset_batch(dataset_text)
            
            # Format according to requested output format
            if output_format.lower() == 'csv':
                formatted_data = self._format_as_csv(dataset_records)
                file_extension = 'csv'
            else:
                formatted_data = self._format_as_jsonl(dataset_records)
                file_extension = 'jsonl'
            
            return {
                "success": True,
                "dataset": formatted_data,
                "format": output_format,
                "file_extension": file_extension,
                "record_count": len(dataset_records),
                "session_id": session_id
            }
            
        except Exception as e:
            print(f"Error generating full dataset: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def _parse_generated_samples(self, samples_text: str, session_id: str, iteration: int = 0) -> List[SampleRecord]:
        """Parse AI-generated samples into SampleRecord objects"""
        
        samples = []
        
        try:
            # Try to parse as JSON array first
            if samples_text.strip().startswith('['):
                json_samples = json.loads(samples_text)
                for i, sample in enumerate(json_samples):
                    samples.append(SampleRecord(
                        id=f"{session_id}_sample_{iteration}_{i}",
                        input_text=sample.get('input', ''),
                        answer_text=sample.get('answer', '')
                    ))
            else:
                # Parse individual JSON objects
                lines = samples_text.strip().split('\n')
                sample_count = 0
                
                for line in lines:
                    line = line.strip()
                    if line and (line.startswith('{') or '"input"' in line):
                        try:
                            sample_data = json.loads(line)
                            samples.append(SampleRecord(
                                id=f"{session_id}_sample_{iteration}_{sample_count}",
                                input_text=sample_data.get('input', ''),
                                answer_text=sample_data.get('answer', '')
                            ))
                            sample_count += 1
                        except json.JSONDecodeError:
                            continue
                
                # If no JSON found, try to extract from text
                if not samples:
                    samples = self._extract_samples_from_text(samples_text, session_id, iteration)
        
        except Exception as e:
            print(f"Error parsing samples: {e}")
            # Fallback: create placeholder samples
            for i in range(5):
                samples.append(SampleRecord(
                    id=f"{session_id}_sample_{iteration}_{i}",
                    input_text=f"Sample input {i+1}",
                    answer_text=f"Sample answer {i+1}"
                ))
        
        return samples[:5]  # Ensure exactly 5 samples
    
    def _extract_samples_from_text(self, text: str, session_id: str, iteration: int) -> List[SampleRecord]:
        """Extract samples from unstructured text"""
        
        samples = []
        
        # Look for input/answer patterns
        import re
        
        # Pattern 1: "Input: ... Answer: ..."
        pattern1 = r'Input:\s*(.+?)\s*Answer:\s*(.+?)(?=Input:|$)'
        matches = re.findall(pattern1, text, re.DOTALL | re.IGNORECASE)
        
        for i, (input_text, answer_text) in enumerate(matches[:5]):
            samples.append(SampleRecord(
                id=f"{session_id}_sample_{iteration}_{i}",
                input_text=input_text.strip(),
                answer_text=answer_text.strip()
            ))
        
        return samples
    
    def _analyze_annotations(self, samples: List[SampleRecord]) -> str:
        """Analyze user annotations to create feedback summary"""
        
        all_annotations = []
        for sample in samples:
            all_annotations.extend(sample.annotations)
        
        if not all_annotations:
            return "No specific feedback provided."
        
        # Use AI to analyze annotations
        analysis_prompt = f"""
        Analyze these user annotations about generated dataset samples:
        
        ANNOTATIONS:
        {json.dumps(all_annotations, indent=2)}
        
        Summarize the key feedback themes and improvement areas:
        - What quality issues were identified?
        - What improvements are needed?
        - What patterns should be adjusted?
        
        Provide a concise summary for improving the next generation.
        """
        
        try:
            return self._call_bedrock(analysis_prompt)
        except:
            return "Feedback received: " + "; ".join(all_annotations[:3])
    
    def _create_improved_prompt(self, session: GenerationSession) -> str:
        """Create improved generation prompt based on feedback"""
        
        base_prompt = session.generation_prompt
        feedback = session.feedback_summary
        
        improved_prompt = f"""
        {base_prompt}
        
        IMPORTANT IMPROVEMENTS NEEDED:
        Based on user feedback: {feedback}
        
        Please address these specific issues in the new examples:
        - Improve quality based on the feedback above
        - Ensure more realistic and varied scenarios
        - Fix any format or content issues mentioned
        - Maintain consistency with the original requirements
        
        Generate exactly 5 improved examples.
        """
        
        return improved_prompt
    
    def _create_batch_generation_prompt(self, session: GenerationSession, num_records: int) -> str:
        """Create prompt for generating full dataset"""
        
        base_prompt = session.generation_prompt
        feedback = session.feedback_summary
        
        batch_prompt = f"""
        {base_prompt}
        
        QUALITY REQUIREMENTS:
        {feedback}
        
        Generate exactly {num_records} high-quality examples following the established pattern.
        
        Requirements:
        - Each example must have "input" and "answer" fields
        - Ensure maximum diversity in scenarios and language
        - Include edge cases and challenging examples (20% of total)
        - Maintain consistent quality and format
        - Use realistic, natural language
        
        Output format: One JSON object per line (JSONL format)
        {{"input": "example input", "answer": "expected answer"}}
        """
        
        return batch_prompt
    
    def _parse_dataset_batch(self, dataset_text: str) -> List[Dict[str, str]]:
        """Parse batch-generated dataset"""
        
        records = []
        lines = dataset_text.strip().split('\n')
        
        for line in lines:
            line = line.strip()
            if line and (line.startswith('{') or '"input"' in line):
                try:
                    record = json.loads(line)
                    if 'input' in record and 'answer' in record:
                        records.append({
                            'input': record['input'],
                            'answer': record['answer']
                        })
                except json.JSONDecodeError:
                    continue
        
        return records
    
    def _format_as_jsonl(self, records: List[Dict[str, str]]) -> str:
        """Format records as JSONL"""
        return '\n'.join(json.dumps(record) for record in records)
    
    def _format_as_csv(self, records: List[Dict[str, str]]) -> str:
        """Format records as CSV"""
        import csv
        import io
        
        output = io.StringIO()
        writer = csv.DictWriter(output, fieldnames=['input', 'answer'])
        writer.writeheader()
        writer.writerows(records)
        
        return output.getvalue()
    
    def _sample_to_dict(self, sample: SampleRecord) -> Dict[str, Any]:
        """Convert SampleRecord to dictionary"""
        return {
            "id": sample.id,
            "input": sample.input_text,
            "answer": sample.answer_text,
            "annotations": sample.annotations,
            "quality_score": sample.quality_score
        }
    
    def _call_bedrock(self, prompt: str) -> str:
        """Call Bedrock API with the given prompt"""
        
        try:
            response = self.bedrock.invoke_model(
                modelId=self.model_id,
                body=json.dumps({
                    "messages": [{"role": "user", "content": [{"text": prompt}]}],
                    "inferenceConfig": {
                        "maxTokens": 4000,
                        "temperature": 0.8
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
