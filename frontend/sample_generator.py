"""
Sample generation service for AI dataset creation.
Generates initial samples, processes annotations, and handles iterative refinement.
"""

import json
import time
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
            Generate 5 unique, varied {checklist.domain_expertise or 'customer service'} questions from {checklist.role_persona or 'customers'}.
            
            Context:
            - Role: {checklist.role_persona}
            - Domain: {checklist.domain_expertise}
            - Input Type: {checklist.input_format}
            
            Create 5 different questions covering various {checklist.domain_expertise or 'customer service'} scenarios:
            1. Common {checklist.domain_expertise or 'service'} inquiries
            2. Complex problem resolution
            3. Account or process issues
            4. Information requests
            5. Complaint or feedback scenarios
            
            Make each question realistic and varied in:
            - Problem type relevant to {checklist.domain_expertise or 'the domain'}
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
    
    def generate_single_sample_with_annotations(self, checklist, model_id: str, sample_number: int, annotations: list) -> Dict[str, Any]:
        """Generate a single sample using annotations as few-shot examples"""
        try:
            # Extract actual format from the output format description
            output_format_text = str(checklist.output_format)
            
            # Build few-shot examples from annotations
            few_shot_examples = ""
            if annotations:
                few_shot_examples = "\n\nFew-shot examples based on previous annotations:\n"
                for i, annotation in enumerate(annotations[:3]):  # Use up to 3 examples
                    few_shot_examples += f"\nExample {i+1} (based on feedback: '{annotation['annotation']}'):\n"
                    few_shot_examples += "- Apply this feedback to improve quality\n"
            
            prompt = f"""
            Generate a training sample for {checklist.domain_expertise or 'customer service'} evaluation.
            
            Context: {checklist.role_persona}
            Task: {checklist.task_goal}
            Domain: {checklist.domain_expertise}
            Use Case: {checklist.use_case}
            
            Output format required: {output_format_text}
            {few_shot_examples}
            
            Create 1 unique {checklist.domain_expertise or 'customer service'} question and respond using the EXACT format specified above.
            
            Return JSON: {{"input": "realistic {checklist.domain_expertise or 'customer service'} question", "output": "complete response in the exact format specified"}}
            
            IMPORTANT:
            - Generate questions relevant to {checklist.domain_expertise or 'the specified domain'}
            - Use the EXACT output format structure from the requirements
            - Include all required fields and reasoning elements
            - Make each question unique (sample #{sample_number})
            - Focus on {checklist.use_case or 'the specified use case'}
            - Apply insights from the annotation feedback above
            """
            
            # Call Bedrock with specified model
            response = self._call_bedrock_with_model(prompt, model_id)
            
            if not response:
                return {"success": False, "error": "No response from model"}
            
            try:
                # Clean response
                response_text = response.strip()
                
                # Handle code blocks
                if response_text.startswith('```json'):
                    response_text = response_text[7:]
                elif response_text.startswith('```'):
                    response_text = response_text[3:]
                    
                if response_text.endswith('```'):
                    response_text = response_text[:-3]
                
                # Parse JSON with proper handling of control characters
                response_text = response_text.replace('\n', '\\n').replace('\r', '\\r').replace('\t', '\\t')
                sample_data = json.loads(response_text)
                
                # Convert to dict with proper output handling
                sample = GeneratedSample.from_llm_response(sample_data)
                
                # Always provide a string version for compatibility
                return {
                    "success": True,
                    "sample": {
                        "input": sample.input,
                        "output": sample.output,
                        "output_string": sample.get_output_as_string()
                    }
                }
                
            except json.JSONDecodeError as e:
                print(f"JSON decode error: {e}")
                print(f"Response text: {response_text}")
                return {"success": False, "error": f"Invalid JSON response: {str(e)}"}
                
        except Exception as e:
            print(f"Error generating sample with annotations: {e}")
            return {"success": False, "error": str(e)}

    def generate_single_sample_from_checklist(self, checklist, model_id: str, sample_number: int) -> Dict[str, Any]:
        """Generate a single sample record from checklist"""
        try:
            # Extract actual format from the output format description
            output_format_text = str(checklist.output_format)
            print(f"🔍 DEBUG - Output format text: {output_format_text}")
            
            prompt = f"""
            Generate a training sample for {checklist.domain_expertise or 'customer service'} evaluation.
            
            Context: {checklist.role_persona}
            Task: {checklist.task_goal}
            Domain: {checklist.domain_expertise}
            Use Case: {checklist.use_case}
            
            Output format required: {output_format_text}
            
            Create 1 unique {checklist.domain_expertise or 'customer service'} question and respond using the EXACT format specified above.
            
            Return JSON: {{"input": "realistic {checklist.domain_expertise or 'customer service'} question", "output": "complete response in the exact format specified"}}
            
            IMPORTANT:
            - Generate questions relevant to {checklist.domain_expertise or 'the specified domain'}
            - Use the EXACT output format structure from the requirements
            - Include all required fields and reasoning elements
            - Make each question unique (sample #{sample_number})
            - Focus on {checklist.use_case or 'the specified use case'}
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
        print(f"🔍 DEBUG - Generation prompt: {generation_prompt[:200]}...")
        
        try:
            # Generate samples using AI
            print(f"🔍 DEBUG - Calling Bedrock with model: {self.model_id}")
            samples_text = self._call_bedrock(generation_prompt)
            print(f"🔍 DEBUG - Raw Bedrock response: {samples_text[:500]}...")
            
            # Parse generated samples
            print(f"🔍 DEBUG - Parsing generated samples...")
            samples = self._parse_generated_samples(samples_text, session_id)
            print(f"🔍 DEBUG - Parsed {len(samples)} samples")
            
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
            print(f"❌ ERROR in generate_initial_samples: {e}")
            import traceback
            traceback.print_exc()
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
        
        # Initialize progress tracking
        self._update_progress(session_id, 0, num_records, "starting")
        
        # Create batch generation prompt
        batch_prompt = self._create_batch_generation_prompt(session, num_records)
        
        try:
            # Update progress - generation started
            self._update_progress(session_id, 0, num_records, "generating")
            
            # Generate full dataset
            dataset_text = self._call_bedrock(batch_prompt)
            
            # Update progress - parsing
            self._update_progress(session_id, num_records // 2, num_records, "parsing")
            
            # Parse and format dataset
            dataset_records = self._parse_dataset_batch(dataset_text)
            
            # Update progress - formatting
            self._update_progress(session_id, num_records * 3 // 4, num_records, "formatting")
            
            # Format according to requested output format
            if output_format.lower() == 'csv':
                formatted_data = self._format_as_csv(dataset_records)
                file_extension = 'csv'
            else:
                formatted_data = self._format_as_jsonl(dataset_records)
                file_extension = 'jsonl'
            
            # Update progress - completed
            self._update_progress(session_id, num_records, num_records, "completed")
            
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
        
        CRITICAL DIVERSITY REQUIREMENTS:
        - Each example MUST be completely different from all others
        - Vary the language style, tone, and complexity significantly
        - Include different scenarios, contexts, and use cases
        - Mix formal and informal language styles
        - Include different user types (new customers, experienced users, etc.)
        - Vary the length and detail level of inputs
        - Include edge cases and challenging examples (20% of total)
        - Use different sentence structures and vocabulary
        - Avoid repetitive patterns or similar phrasings
        - Each input should represent a unique situation or problem
        
        FORMAT REQUIREMENTS:
        - Each example must have "input" and "answer" fields
        - Maintain consistent quality and format
        - Use realistic, natural language
        
        Output format: One JSON object per line (JSONL format)
        {{"input": "example input", "answer": "expected answer"}}
        
        IMPORTANT: Make each example distinctly different. No repetitive content or similar scenarios.
        """
        
        return batch_prompt
    
    def _parse_dataset_batch(self, dataset_text: str) -> List[Dict[str, str]]:
        """Parse batch-generated dataset with diversity filtering"""
        
        records = []
        seen_inputs = set()
        lines = dataset_text.strip().split('\n')
        
        for line in lines:
            line = line.strip()
            if line and (line.startswith('{') or '"input"' in line):
                try:
                    record = json.loads(line)
                    if 'input' in record and 'answer' in record:
                        input_text = record['input'].strip()
                        
                        # Check for diversity - reject if too similar to existing
                        is_duplicate = False
                        for seen_input in seen_inputs:
                            if self._is_too_similar(input_text, seen_input):
                                print(f"🔍 DEBUG - Rejecting similar input: {input_text[:50]}...")
                                is_duplicate = True
                                break
                        
                        if not is_duplicate:
                            records.append({
                                'input': input_text,
                                'answer': record['answer']
                            })
                            seen_inputs.add(input_text)
                        
                except json.JSONDecodeError:
                    continue
        
        return records
    
    def _update_progress(self, session_id: str, current: int, total: int, status: str):
        """Update progress for a session"""
        import os
        import json
        
        os.makedirs("data", exist_ok=True)
        progress_file = f"data/generation_progress_{session_id}.json"
        
        progress_data = {
            "current": current,
            "total": total,
            "status": status,
            "timestamp": time.time()
        }
        
        try:
            with open(progress_file, 'w') as f:
                json.dump(progress_data, f)
        except Exception as e:
            print(f"Error updating progress: {e}")

    def _is_too_similar(self, text1: str, text2: str) -> bool:
        """Check if two texts are too similar (basic similarity check)"""
        # Simple similarity check - can be enhanced with more sophisticated methods
        words1 = set(text1.lower().split())
        words2 = set(text2.lower().split())
        
        if len(words1) == 0 or len(words2) == 0:
            return False
            
        intersection = len(words1.intersection(words2))
        union = len(words1.union(words2))
        
        # If more than 70% of words are the same, consider it too similar
        similarity = intersection / union if union > 0 else 0
        return similarity > 0.7
    
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
