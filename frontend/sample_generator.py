"""
Sample generation service for AI dataset creation.
Generates initial samples, processes annotations, and handles iterative refinement.
"""

import json
import boto3
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from botocore.exceptions import ClientError


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
