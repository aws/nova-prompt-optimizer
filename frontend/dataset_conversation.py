"""
Conversational AI service for dataset generation requirements gathering.
Walks users through comprehensive checklist to ensure high-quality dataset generation.
"""

import json
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
import boto3
from botocore.exceptions import ClientError


@dataclass
class RequirementsChecklist:
    """Comprehensive checklist for dataset generation requirements"""
    
    # Role and Persona
    role_persona: Optional[str] = None
    domain_expertise: Optional[str] = None
    
    # Task Description
    task_goal: Optional[str] = None
    use_case: Optional[str] = None
    interaction_type: Optional[str] = None
    
    # Data Characteristics
    diversity_requirements: Optional[Dict] = None
    realism_requirements: Optional[Dict] = None
    edge_cases: Optional[List[str]] = None
    constraints: Optional[Dict] = None
    
    # Format Requirements
    input_format: Optional[str] = None
    output_format: Optional[str] = None
    dataset_format: str = "jsonl"  # Default to JSONL
    
    def is_complete(self) -> bool:
        """Check if all required fields are filled"""
        required_fields = [
            'role_persona', 'task_goal', 'use_case', 
            'input_format', 'output_format'
        ]
        return all(getattr(self, field) is not None for field in required_fields)
    
    def get_missing_fields(self) -> List[str]:
        """Get list of missing required fields"""
        required_fields = [
            'role_persona', 'task_goal', 'use_case', 
            'input_format', 'output_format'
        ]
        return [field for field in required_fields if getattr(self, field) is None]


class DatasetConversationService:
    """AI-powered conversational service for dataset requirements gathering"""
    
    def __init__(self, region_name: str = "us-east-1"):
        self.bedrock = boto3.client('bedrock-runtime', region_name=region_name)
        self.model_id = "us.amazon.nova-premier-v1:0"
        self.conversation_history = []
        self.checklist = RequirementsChecklist()
        self.original_prompt = ""  # Store the original prompt
        
    def _clean_prompt_display(self, prompt_text: str) -> str:
        """Clean up prompt text for better display, handling malformed XML gracefully"""
        # Fix common XML syntax errors
        cleaned = prompt_text
        
        # Fix malformed closing tags like "</gender reasoning>" -> "</gender>"
        import re
        cleaned = re.sub(r'</(\w+)\s+[^>]*>', r'</\1>', cleaned)
        
        return cleaned
    
    def _extract_from_prompt(self, field_type: str) -> str:
        """Extract field directly from the original prompt"""
        text = self.original_prompt.lower()
        
        if field_type == "role":
            if 'you are a' in text:
                start = text.find('you are a') + 9
                end = self.original_prompt.find('.', start)
                if end == -1:
                    end = self.original_prompt.find('\n', start)
                if end != -1:
                    return self.original_prompt[start:end].strip()
        
        elif field_type == "task":
            if 'analyze each interaction' in text:
                return "Analyze interactions and provide classifications with confidence scores"
            elif 'must analyze' in text:
                return "Analyze interactions and provide classifications"
        
        elif field_type == "input":
            return "Not clearly specified in prompt"
        
        elif field_type == "output":
            if '<support_interaction>' in text:
                return "XML format with complete structure including reasoning fields"
            return "Not clearly specified in prompt"
        
        elif field_type == "domain":
            return "Not clearly specified in prompt"
        
        elif field_type == "use_case":
            return "Not clearly specified in prompt"
        
        return "Not clearly specified in prompt"
    
    def _extract_field(self, text: str, *keywords) -> str:
        """Extract field value from natural language response"""
        text_lower = text.lower()
        
        # For role/persona - look in the actual prompt content
        if any(k in ['role', 'persona'] for k in keywords):
            if 'you are a' in text_lower:
                start = text_lower.find('you are a') + 9
                end = text.find('.', start)
                if end == -1:
                    end = text.find('\n', start)
                if end == -1:
                    end = start + 100
                return text[start:end].strip()
        
        # For task/goal - look for analysis requirements
        if any(k in ['task', 'goal'] for k in keywords):
            if 'analyze each interaction' in text_lower:
                return "Analyze interactions and provide classifications with confidence scores"
            if 'must analyze' in text_lower:
                return "Analyze interactions and provide classifications"
        
        # For input - generic handling
        if 'input' in keywords:
            return "Not clearly specified in prompt"
        
        # For domain - generic handling  
        if any(k in ['domain', 'field'] for k in keywords):
            return "Not clearly specified in prompt"
        
        # For use case - generic handling
        if any(k in ['use case', 'evaluation'] for k in keywords):
            return "Not clearly specified in prompt"
        
        return "Not clearly specified in prompt"
    
    def analyze_prompt(self, prompt_text: str) -> Dict[str, Any]:
        """Analyze existing prompt to understand requirements"""
        print(f"🔍 DEBUG - Analyzing prompt: {prompt_text[:200]}...")
        
        # Store the original prompt
        self.original_prompt = prompt_text
        
        analysis_prompt = f"""
        Analyze this prompt and extract the requirements for dataset generation.
        
        PROMPT TO ANALYZE:
        {prompt_text}
        
        Extract and describe:
        - Role/persona the AI should play
        - Task/goal the AI should accomplish  
        - Input type expected
        - Output format (describe the structure and all fields/attributes)
        - Domain/field
        - Use case for evaluation
        """
        
        try:
            print(f"🔍 DEBUG - Calling Bedrock for prompt analysis")
            response = self._call_bedrock(analysis_prompt)
            print(f"🔍 DEBUG - Bedrock response: {response}")
            
            # Parse directly from the original prompt instead of AI response
            analysis = {
                "role_persona": self._extract_from_prompt("role"),
                "task_goal": self._extract_from_prompt("task"),
                "input_type": self._extract_from_prompt("input"),
                "output_format": self._extract_from_prompt("output"),
                "domain": self._extract_from_prompt("domain"),
                "use_case": self._extract_from_prompt("use_case")
            }
            
            print(f"🔍 DEBUG - Parsed analysis: {analysis}")
            
            # Pre-populate checklist based on analysis
            if analysis.get('role_persona'):
                self.checklist.role_persona = analysis['role_persona']
                print(f"🔍 DEBUG - Set role_persona: {analysis['role_persona']}")
            if analysis.get('task_goal'):
                self.checklist.task_goal = analysis['task_goal']
                print(f"🔍 DEBUG - Set task_goal: {analysis['task_goal']}")
            if analysis.get('use_case'):
                self.checklist.use_case = analysis['use_case']
                print(f"🔍 DEBUG - Set use_case: {analysis['use_case']}")
            if analysis.get('input_type'):
                self.checklist.input_format = analysis['input_type']
                print(f"🔍 DEBUG - Set input_format: {analysis['input_type']}")
            if analysis.get('output_format'):
                self.checklist.output_format = analysis['output_format']
                print(f"🔍 DEBUG - Set output_format: {analysis['output_format']}")
            if analysis.get('domain'):
                self.checklist.domain_expertise = analysis['domain']
                print(f"🔍 DEBUG - Set domain_expertise: {analysis['domain']}")
                
            print(f"🔍 DEBUG - Updated checklist: {asdict(self.checklist)}")
            return analysis
            
        except Exception as e:
            print(f"Error analyzing prompt: {e}")
            return {"error": "Failed to analyze prompt", "suggestions": []}
    
    def start_conversation(self, user_message: str = None) -> Dict[str, Any]:
        """Start or continue the requirements gathering conversation"""
        
        if not user_message:
            # Check if we already have some requirements from prompt analysis
            missing_fields = self.checklist.get_missing_fields()
            
            if len(missing_fields) < 5:  # Some fields were pre-filled
                filled_fields = []
                if self.checklist.role_persona and "Undefined" not in self.checklist.role_persona:
                    filled_fields.append(f"Role: {self.checklist.role_persona}")
                if self.checklist.task_goal:
                    filled_fields.append(f"Task: {self.checklist.task_goal}")
                if self.checklist.use_case:
                    filled_fields.append(f"Use Case: {self.checklist.use_case}")
                if self.checklist.input_format:
                    filled_fields.append(f"Input: {self.checklist.input_format}")
                if self.checklist.output_format:
                    # Extract and display the original XML structure from the prompt
                    xml_start = self.original_prompt.find('<support_interaction>')
                    xml_end = self.original_prompt.find('</support_interaction>') + len('</support_interaction>')
                    
                    if xml_start >= 0 and xml_end > xml_start:
                        xml_structure = self.original_prompt[xml_start:xml_end]
                        filled_fields.append(f"Output: XML format with complete structure including reasoning fields")
                    else:
                        filled_fields.append(f"Output: {self.checklist.output_format}")
                if self.checklist.domain_expertise:
                    filled_fields.append(f"Domain: {self.checklist.domain_expertise}")
                
                if filled_fields:
                    summary = "**Prompt Analysis Complete**\n\n"
                    
                    # Clean up the original prompt display for better readability
                    cleaned_prompt = self._clean_prompt_display(self.original_prompt)
                    summary += f"**Original Prompt:**\n```\n{cleaned_prompt}\n```\n\n"
                    
                    summary += "**Extracted Requirements:**\n"
                    for field in filled_fields:
                        summary += f"• {field}\n"
                    summary += f"\n**Please Review:**\n"
                    summary += f"• Are these requirements accurate?\n"
                    summary += f"• Would you like to modify anything?\n"
                    summary += f"• Any additional requirements to add?\n\n"
                else:
                    summary = "I analyzed your prompt but couldn't extract clear requirements. "
                
                if missing_fields:
                    next_field = missing_fields[0]
                    question = self._get_question_for_field(next_field)
                    summary += f"**Next Step:** {next_field.replace('_', ' ').title()}\n\n"
                    summary += f"**How to Respond:**\n"
                    summary += f"• *'Continue'* or *'Looks good'* → Proceed with current requirements\n"
                    summary += f"• *'Change [field] to [value]'* → Modify specific requirements\n"
                    summary += f"• *'Add [requirement]'* → Include additional details\n\n"
                    summary += f"What would you like to do?"
                    
                    return {
                        "message": summary,
                        "step": "review_analysis",
                        "checklist_status": self._get_checklist_status()
                    }
                else:
                    # All fields filled but show review with generate option
                    return {
                        "message": summary + "\n**Ready to generate sample records!**",
                        "step": "complete",
                        "checklist_status": self._get_checklist_status(),
                        "ready_for_generation": True
                    }
            else:
                # Initial greeting for fresh start
                return {
                    "message": "Hi! I'll help you create a high-quality dataset for prompt optimization. Let's start by understanding what you need.\n\nWhat type of task or use case do you want to create evaluation data for? (e.g., 'customer support email classification', 'document summarization', 'question answering')",
                    "step": "task_goal",
                    "checklist_status": self._get_checklist_status()
                }
        
        # Add user message to history
        self.conversation_history.append({"role": "user", "content": user_message})
        
        # Determine next question based on current state
        next_question = self._get_next_question(user_message)
        
        # Add AI response to history
        self.conversation_history.append({"role": "assistant", "content": next_question["message"]})
        
        return next_question
    
    def _get_next_question(self, user_response: str) -> Dict[str, Any]:
        """Determine next question based on user response and checklist state"""
        
        print(f"🔍 DEBUG - _get_next_question called with: '{user_response}'")
        print(f"🔍 DEBUG - Current checklist state: {asdict(self.checklist)}")
        
        # Check if user is asking for clarification or wants to continue
        continue_keywords = ['continue', 'looks good', 'proceed', 'next', 'done', 'ready']
        is_continue_request = any(keyword in user_response.lower() for keyword in continue_keywords)
        
        # Update checklist based on current conversation context
        self._update_checklist_from_response(user_response)
        
        print(f"🔍 DEBUG - Updated checklist state: {asdict(self.checklist)}")
        
        missing_fields = self.checklist.get_missing_fields()
        print(f"🔍 DEBUG - Missing fields: {missing_fields}")
        
        # If user explicitly wants to continue and no missing fields, complete
        if not missing_fields and is_continue_request:
            return {
                "message": "Perfect! I have all the information needed to generate your dataset. Here's what I understand:\n\n" + self._summarize_requirements(),
                "step": "complete",
                "checklist_status": self._get_checklist_status(),
                "ready_for_generation": True
            }
        
        # If no missing fields but user didn't explicitly continue, ask for confirmation
        if not missing_fields:
            return {
                "message": "I've updated the requirements based on your feedback. Here's the current summary:\n\n" + self._summarize_requirements() + "\n\nWould you like to continue with these requirements or make any other changes?",
                "step": "review_updated",
                "checklist_status": self._get_checklist_status()
            }
        
        # Ask about the next missing field
        next_field = missing_fields[0]
        question = self._get_question_for_field(next_field)
        
        return {
            "message": question,
            "step": next_field,
            "checklist_status": self._get_checklist_status()
        }
    
    def _update_checklist_from_response(self, response: str):
        """Update checklist based on user response using AI"""
        
        print(f"🔍 DEBUG - _update_checklist_from_response called with: '{response}'")
        
        current_step = self._get_current_step()
        print(f"🔍 DEBUG - Current step: {current_step}")
        
        update_prompt = f"""
        Based on this user response, extract relevant information for dataset generation:
        
        USER RESPONSE: {response}
        CURRENT STEP: {current_step}
        
        Current checklist state:
        {json.dumps(asdict(self.checklist), indent=2)}
        
        IMPORTANT: If the user is asking for clarification, more details, or to be "more explicit" about a field, 
        DO NOT mark that field as complete. Instead, provide a more detailed version of that field.
        
        For example:
        - "be more explicit on output" → update output_format with more detailed description
        - "tell me more about the role" → update role_persona with more details
        - "what exactly should the input be" → update input_format with specifics
        
        Update the checklist fields based on the user's response. Return JSON with only the fields that should be updated:
        {{
            "role_persona": "extracted role/persona if mentioned or more detailed if requested",
            "task_goal": "extracted task goal if mentioned or more detailed if requested", 
            "use_case": "extracted use case if mentioned or more detailed if requested",
            "input_format": "extracted input format if mentioned or more detailed if requested",
            "output_format": "extracted output format if mentioned or MORE DETAILED if user asks for clarification",
            "domain_expertise": "extracted domain if mentioned or more detailed if requested",
            "diversity_requirements": {{"variations": ["list of variations needed"]}},
            "constraints": {{"length": "any length constraints", "tone": "tone requirements"}}
        }}
        
        Only include fields that the user actually mentioned or requested more details about.
        """
        
        try:
            print(f"🔍 DEBUG - Calling Bedrock with update prompt")
            response_data = self._call_bedrock(update_prompt)
            print(f"🔍 DEBUG - Bedrock response: {response_data}")
            
            # Extract JSON from response (AI might include explanations)
            json_start = response_data.find('{')
            json_end = response_data.rfind('}') + 1
            
            if json_start >= 0 and json_end > json_start:
                json_str = response_data[json_start:json_end]
                print(f"🔍 DEBUG - Extracted JSON: {json_str}")
                updates = json.loads(json_str)
            else:
                print(f"🔍 DEBUG - No JSON found in response, skipping update")
                return
            
            print(f"🔍 DEBUG - Parsed updates: {updates}")
            
            # Update checklist fields
            for field, value in updates.items():
                if value and hasattr(self.checklist, field):
                    setattr(self.checklist, field, value)
                    print(f"🔍 DEBUG - Updated {field} = {value}")
                    
        except Exception as e:
            print(f"Error updating checklist: {e}")
    
    def _get_question_for_field(self, field: str) -> str:
        """Get appropriate question for a specific checklist field"""
        
        questions = {
            "role_persona": "What role or persona should the AI adopt when generating responses? (e.g., 'customer support agent', 'medical expert', 'technical writer')",
            
            "task_goal": "What is the main task or goal for this dataset? What should the AI be able to do with this data?",
            
            "use_case": "What specific use case or scenario will this dataset be used for? How will it help improve your prompts?",
            
            "input_format": "What type of input data should each record contain? (e.g., 'customer emails', 'product descriptions', 'questions', 'documents')",
            
            "output_format": "What type of output should the AI generate for each input? (e.g., 'classification labels', 'summaries', 'answers', 'JSON responses')"
        }
        
        return questions.get(field, f"Please provide information about: {field}")
    
    def _get_current_step(self) -> str:
        """Determine current conversation step"""
        missing_fields = self.checklist.get_missing_fields()
        return missing_fields[0] if missing_fields else "complete"
    
    def _get_checklist_status(self) -> Dict[str, Any]:
        """Get current checklist completion status"""
        return {
            "completed_fields": [field for field in ['role_persona', 'task_goal', 'use_case', 'input_format', 'output_format'] 
                               if getattr(self.checklist, field) is not None],
            "missing_fields": self.checklist.get_missing_fields(),
            "is_complete": self.checklist.is_complete(),
            "progress": f"{5 - len(self.checklist.get_missing_fields())}/5"
        }
    
    def _summarize_requirements(self) -> str:
        """Create a summary of gathered requirements"""
        return f"""
        📋 Dataset Requirements Summary:
        
        🎭 Role/Persona: {self.checklist.role_persona}
        🎯 Task Goal: {self.checklist.task_goal}
        💼 Use Case: {self.checklist.use_case}
        📥 Input Format: {self.checklist.input_format}
        📤 Output Format: {self.checklist.output_format}
        🏷️ Domain: {self.checklist.domain_expertise or 'General'}
        
        Ready to generate sample records for your review!
        """
    
    def get_generation_config(self) -> Dict[str, Any]:
        """Get configuration for dataset generation"""
        return {
            "checklist": asdict(self.checklist),
            "conversation_history": self.conversation_history,
            "generation_prompt": self._build_generation_prompt()
        }
    
    def _build_generation_prompt(self) -> str:
        """Build prompt for dataset generation based on gathered requirements"""
        
        return f"""
        You are a {self.checklist.role_persona} creating evaluation data for prompt optimization.
        
        TASK: {self.checklist.task_goal}
        USE CASE: {self.checklist.use_case}
        
        Generate diverse, realistic examples with:
        - INPUT: {self.checklist.input_format}
        - OUTPUT: {self.checklist.output_format}
        
        Requirements:
        - Create varied, realistic scenarios
        - Include edge cases and challenging examples
        - Ensure outputs are accurate and helpful
        - Use natural language and realistic contexts
        
        Format each example as:
        {{"input": "example input text", "answer": "expected output"}}
        
        Generate exactly 5 examples for initial review.
        """
    
    def _call_bedrock(self, prompt: str) -> str:
        """Call Bedrock API with the given prompt"""
        
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
