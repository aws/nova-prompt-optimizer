"""
Optimized Prompt Builder Service
Leverages Nova SDK best practices for declarative prompt construction
"""

import re
import json
from typing import Dict, List, Set, Any, Optional
from dataclasses import dataclass, field

# Import Nova SDK components (assuming they're available in the environment)
try:
    from amzn_nova_prompt_optimizer.core.input_adapters.prompt_adapter import PromptAdapter as BasePromptAdapter
    
    class PromptAdapter(BasePromptAdapter):
        """Concrete implementation of PromptAdapter for the builder"""
        
        def get_file_extension(self) -> str:
            return ".txt"
        
        def get_format(self) -> str:
            return "text"
            
except ImportError:
    # Fallback for testing without SDK
    class PromptAdapter:
        def __init__(self):
            self.system_prompt = ""
            self.user_prompt = ""
            self.system_variables = set()
            self.user_variables = set()
        
        def set_system_prompt(self, content: str, variables: Optional[Set[str]] = None):
            self.system_prompt = content
            if variables:
                self.system_variables = variables
            return self
        
        def set_user_prompt(self, content: str, variables: Optional[Set[str]] = None):
            self.user_prompt = content
            if variables:
                self.user_variables = variables
            return self
        
        def adapt(self):
            return self


@dataclass
class ValidationResult:
    """Result of prompt validation"""
    is_valid: bool
    issues: List[str] = field(default_factory=list)
    suggestions: List[str] = field(default_factory=list)
    best_practices: Dict[str, bool] = field(default_factory=dict)


class NovaPromptTemplate:
    """Nova SDK template integration with best practices"""
    
    # Nova's proven prompt structure template
    NOVA_TEMPLATE = """Task: {task}

Context:
{context}

Instructions:
{instructions}

Response Format:
{response_format}"""

    USER_TEMPLATE = """{user_content}

{variables_section}"""

    @staticmethod
    def apply_best_practices(builder: 'OptimizedPromptBuilder') -> Dict[str, str]:
        """Apply Nova best practices to generate system and user prompts"""
        
        # Format context items
        context_text = "\n".join([f"- {item}" for item in builder.context])
        
        # Format instructions with strong directive language
        instructions_text = "\n".join([
            f"- {instruction}" if not instruction.upper().startswith(('MUST', 'DO NOT', 'NEVER'))
            else f"- {instruction}"
            for instruction in builder.instructions
        ])
        
        # Format response format requirements
        format_text = "\n".join([f"- {fmt}" for fmt in builder.response_format])
        
        # Generate system prompt
        system_prompt = NovaPromptTemplate.NOVA_TEMPLATE.format(
            task=builder.task,
            context=context_text,
            instructions=instructions_text,
            response_format=format_text
        )
        
        # Generate user prompt with variables
        variables_section = ""
        if builder.variables:
            variables_section = "\n\nInputs:\n" + "\n".join([
                f"{var}: {{{{{var}}}}}" for var in sorted(builder.variables)
            ])
        
        user_prompt = NovaPromptTemplate.USER_TEMPLATE.format(
            user_content="Please analyze the following:",
            variables_section=variables_section
        ).strip()
        
        return {
            "system_prompt": system_prompt,
            "user_prompt": user_prompt
        }
    
    @staticmethod
    def validate_structure(prompt_dict: Dict[str, str]) -> List[str]:
        """Validate prompt structure against Nova best practices"""
        issues = []
        
        system_prompt = prompt_dict.get("system_prompt", "")
        user_prompt = prompt_dict.get("user_prompt", "")
        
        # Check system prompt structure
        required_sections = ["Task:", "Context:", "Instructions:", "Response Format:"]
        for section in required_sections:
            if section not in system_prompt:
                issues.append(f"Missing required section: {section}")
        
        # Check for strong directive language
        if not any(word in system_prompt.upper() for word in ["MUST", "DO NOT", "NEVER"]):
            issues.append("Consider using stronger directive language (MUST, DO NOT)")
        
        # Check user prompt has content
        if not user_prompt.strip():
            issues.append("User prompt cannot be empty")
        
        return issues


class OptimizedPromptBuilder:
    """Declarative prompt builder using Nova best practices"""
    
    def __init__(self):
        self.task: str = ""
        self.context: List[str] = []
        self.instructions: List[str] = []
        self.response_format: List[str] = []
        self.variables: Set[str] = set()
        self.metadata: Dict[str, Any] = {}
    
    def set_task(self, description: str) -> 'OptimizedPromptBuilder':
        """Set the main task description"""
        self.task = description.strip()
        return self
    
    def add_context(self, context: str) -> 'OptimizedPromptBuilder':
        """Add context information"""
        if context.strip():
            self.context.append(context.strip())
        return self
    
    def add_instruction(self, instruction: str) -> 'OptimizedPromptBuilder':
        """Add instruction with automatic best practice enhancement"""
        if instruction.strip():
            # Enhance with strong directive language if needed
            enhanced = self._enhance_instruction(instruction.strip())
            self.instructions.append(enhanced)
        return self
    
    def set_response_format(self, format_spec: str) -> 'OptimizedPromptBuilder':
        """Set response format requirements"""
        if format_spec.strip():
            self.response_format = [format_spec.strip()]
        return self
    
    def add_response_format(self, format_spec: str) -> 'OptimizedPromptBuilder':
        """Add additional response format requirement"""
        if format_spec.strip():
            self.response_format.append(format_spec.strip())
        return self
    
    def add_variable(self, name: str) -> 'OptimizedPromptBuilder':
        """Add template variable"""
        if name.strip():
            # Clean variable name (alphanumeric and underscore only)
            clean_name = re.sub(r'[^a-zA-Z0-9_]', '', name.strip())
            if clean_name:
                self.variables.add(clean_name)
        return self
    
    def set_metadata(self, key: str, value: Any) -> 'OptimizedPromptBuilder':
        """Set metadata for the prompt"""
        self.metadata[key] = value
        return self
    
    def validate(self) -> ValidationResult:
        """Validate the current prompt configuration"""
        issues = []
        suggestions = []
        best_practices = {}
        
        # Check required fields
        if not self.task:
            issues.append("Task description is required")
        else:
            best_practices["has_task"] = True
        
        if not self.context:
            issues.append("At least one context item is required")
        else:
            best_practices["has_context"] = True
        
        if not self.instructions:
            issues.append("At least one instruction is required")
        else:
            best_practices["has_instructions"] = True
        
        if not self.response_format:
            suggestions.append("Consider adding response format requirements")
            best_practices["has_response_format"] = False
        else:
            best_practices["has_response_format"] = True
        
        # Check instruction quality
        strong_directives = any(
            any(word in instruction.upper() for word in ["MUST", "DO NOT", "NEVER"])
            for instruction in self.instructions
        )
        best_practices["uses_strong_directives"] = strong_directives
        if not strong_directives:
            suggestions.append("Use strong directive language (MUST, DO NOT) for clarity")
        
        # Check variable usage
        if self.variables:
            best_practices["has_variables"] = True
        
        return ValidationResult(
            is_valid=len(issues) == 0,
            issues=issues,
            suggestions=suggestions,
            best_practices=best_practices
        )
    
    def preview(self) -> Dict[str, str]:
        """Generate preview of system and user prompts"""
        return NovaPromptTemplate.apply_best_practices(self)
    
    def build(self) -> PromptAdapter:
        """Build PromptAdapter from current configuration"""
        validation = self.validate()
        if not validation.is_valid:
            raise ValueError(f"Cannot build invalid prompt: {', '.join(validation.issues)}")
        
        prompts = self.preview()
        
        # Create PromptAdapter
        adapter = PromptAdapter()
        adapter.set_system_prompt(
            content=prompts["system_prompt"],
            variables=set()  # System prompt shouldn't have variables
        )
        adapter.set_user_prompt(
            content=prompts["user_prompt"],
            variables=self.variables
        )
        adapter.adapt()
        
        return adapter
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for storage"""
        return {
            "task": self.task,
            "context": self.context,
            "instructions": self.instructions,
            "response_format": self.response_format,
            "variables": list(self.variables),
            "metadata": self.metadata
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'OptimizedPromptBuilder':
        """Create builder from dictionary"""
        builder = cls()
        builder.task = data.get("task", "")
        builder.context = data.get("context", [])
        builder.instructions = data.get("instructions", [])
        builder.response_format = data.get("response_format", [])
        builder.variables = set(data.get("variables", []))
        builder.metadata = data.get("metadata", {})
        return builder
    
    def _enhance_instruction(self, instruction: str) -> str:
        """Enhance instruction with strong directive language if needed"""
        # If already has strong directive, return as-is
        if any(word in instruction.upper() for word in ["MUST", "DO NOT", "NEVER", "ALWAYS"]):
            return instruction
        
        # Add MUST for positive instructions
        if instruction.lower().startswith(("use", "include", "provide", "ensure", "follow")):
            return f"MUST {instruction.lower()}"
        
        # Add DO NOT for negative instructions  
        if instruction.lower().startswith(("avoid", "don't", "do not", "never")):
            cleaned = instruction.lower().replace('avoid', '').replace("don't", '').replace('do not', '').replace('never', '').strip()
            return f"DO NOT {cleaned}"
        
        return instruction
