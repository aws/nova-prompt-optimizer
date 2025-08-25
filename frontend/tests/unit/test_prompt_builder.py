"""
Unit tests for OptimizedPromptBuilder
"""

import pytest
from services.prompt_builder import OptimizedPromptBuilder, NovaPromptTemplate, ValidationResult


class TestOptimizedPromptBuilder:
    """Test the core OptimizedPromptBuilder functionality"""
    
    def test_set_task_updates_task_field(self):
        """Test that set_task properly updates the task field"""
        builder = OptimizedPromptBuilder()
        task = "Analyze customer feedback sentiment"
        
        result = builder.set_task(task)
        
        assert builder.task == task
        assert result is builder  # Should return self for chaining
    
    def test_set_task_strips_whitespace(self):
        """Test that set_task strips leading/trailing whitespace"""
        builder = OptimizedPromptBuilder()
        task = "  Analyze sentiment  "
        
        builder.set_task(task)
        
        assert builder.task == "Analyze sentiment"
    
    def test_add_context_appends_to_list(self):
        """Test that add_context appends items to context list"""
        builder = OptimizedPromptBuilder()
        
        builder.add_context("Customer support context")
        builder.add_context("Product feedback analysis")
        
        assert len(builder.context) == 2
        assert "Customer support context" in builder.context
        assert "Product feedback analysis" in builder.context
    
    def test_add_context_ignores_empty_strings(self):
        """Test that add_context ignores empty or whitespace-only strings"""
        builder = OptimizedPromptBuilder()
        
        builder.add_context("")
        builder.add_context("   ")
        builder.add_context("Valid context")
        
        assert len(builder.context) == 1
        assert builder.context[0] == "Valid context"
    
    def test_add_instruction_with_enhancement(self):
        """Test that add_instruction enhances instructions with strong directives"""
        builder = OptimizedPromptBuilder()
        
        builder.add_instruction("use positive sentiment classification")
        builder.add_instruction("avoid technical jargon")
        builder.add_instruction("MUST include confidence scores")  # Already strong
        
        assert len(builder.instructions) == 3
        assert "MUST use positive sentiment classification" in builder.instructions
        assert "DO NOT technical jargon" in builder.instructions
        assert "MUST include confidence scores" in builder.instructions
    
    def test_set_response_format_replaces_existing(self):
        """Test that set_response_format replaces existing format"""
        builder = OptimizedPromptBuilder()
        
        builder.set_response_format("JSON format")
        builder.set_response_format("XML format")
        
        assert len(builder.response_format) == 1
        assert builder.response_format[0] == "XML format"
    
    def test_add_response_format_appends_to_existing(self):
        """Test that add_response_format appends to existing formats"""
        builder = OptimizedPromptBuilder()
        
        builder.set_response_format("JSON format")
        builder.add_response_format("Include confidence scores")
        
        assert len(builder.response_format) == 2
        assert "JSON format" in builder.response_format
        assert "Include confidence scores" in builder.response_format
    
    def test_add_variable_updates_set(self):
        """Test that add_variable adds to variables set"""
        builder = OptimizedPromptBuilder()
        
        builder.add_variable("customer_feedback")
        builder.add_variable("product_name")
        builder.add_variable("customer_feedback")  # Duplicate should be ignored
        
        assert len(builder.variables) == 2
        assert "customer_feedback" in builder.variables
        assert "product_name" in builder.variables
    
    def test_add_variable_cleans_names(self):
        """Test that add_variable cleans variable names"""
        builder = OptimizedPromptBuilder()
        
        builder.add_variable("customer-feedback!")
        builder.add_variable("product name")
        builder.add_variable("123invalid")
        
        assert "customerfeedback" in builder.variables
        assert "productname" in builder.variables
        assert "123invalid" in builder.variables
    
    def test_validate_returns_issues_for_incomplete_prompt(self):
        """Test that validate returns issues for incomplete prompts"""
        builder = OptimizedPromptBuilder()
        
        result = builder.validate()
        
        assert not result.is_valid
        assert "Task description is required" in result.issues
        assert "At least one context item is required" in result.issues
        assert "At least one instruction is required" in result.issues
    
    def test_validate_passes_for_complete_prompt(self):
        """Test that validate passes for complete prompts"""
        builder = OptimizedPromptBuilder()
        builder.set_task("Analyze sentiment")
        builder.add_context("Customer feedback context")
        builder.add_instruction("MUST classify as positive/negative/neutral")
        builder.set_response_format("JSON with sentiment and confidence")
        
        result = builder.validate()
        
        assert result.is_valid
        assert len(result.issues) == 0
        assert result.best_practices["has_task"]
        assert result.best_practices["has_context"]
        assert result.best_practices["has_instructions"]
        assert result.best_practices["uses_strong_directives"]
    
    def test_validate_suggests_improvements(self):
        """Test that validate provides helpful suggestions"""
        builder = OptimizedPromptBuilder()
        builder.set_task("Analyze sentiment")
        builder.add_context("Customer feedback context")
        builder.add_instruction("classify sentiment")  # Weak directive
        
        result = builder.validate()
        
        assert "Consider adding response format requirements" in result.suggestions
        assert "Use strong directive language (MUST, DO NOT) for clarity" in result.suggestions
    
    def test_preview_generates_system_and_user_prompts(self):
        """Test that preview generates properly formatted prompts"""
        builder = OptimizedPromptBuilder()
        builder.set_task("Analyze customer feedback sentiment")
        builder.add_context("Customer support emails")
        builder.add_context("Product review comments")
        builder.add_instruction("MUST classify as positive, negative, or neutral")
        builder.add_instruction("DO NOT include personal opinions")
        builder.set_response_format("JSON format with sentiment and confidence score")
        builder.add_variable("customer_feedback")
        
        result = builder.preview()
        
        assert "system_prompt" in result
        assert "user_prompt" in result
        
        system_prompt = result["system_prompt"]
        assert "Task: Analyze customer feedback sentiment" in system_prompt
        assert "Context:" in system_prompt
        assert "Customer support emails" in system_prompt
        assert "Instructions:" in system_prompt
        assert "MUST classify as positive, negative, or neutral" in system_prompt
        assert "Response Format:" in system_prompt
        
        user_prompt = result["user_prompt"]
        assert "customer_feedback: {{customer_feedback}}" in user_prompt
    
    def test_build_creates_valid_prompt_adapter(self):
        """Test that build creates a valid PromptAdapter"""
        builder = OptimizedPromptBuilder()
        builder.set_task("Analyze sentiment")
        builder.add_context("Customer feedback context")
        builder.add_instruction("MUST classify sentiment")
        builder.set_response_format("JSON format")
        builder.add_variable("input_text")
        
        adapter = builder.build()
        
        assert adapter is not None
        assert hasattr(adapter, 'system_prompt')
        assert hasattr(adapter, 'user_prompt')
        assert adapter.system_prompt
        assert adapter.user_prompt
    
    def test_build_raises_error_for_invalid_prompt(self):
        """Test that build raises error for invalid prompts"""
        builder = OptimizedPromptBuilder()
        # Don't set required fields
        
        with pytest.raises(ValueError) as exc_info:
            builder.build()
        
        assert "Cannot build invalid prompt" in str(exc_info.value)
    
    def test_to_dict_serializes_correctly(self):
        """Test that to_dict properly serializes builder state"""
        builder = OptimizedPromptBuilder()
        builder.set_task("Test task")
        builder.add_context("Test context")
        builder.add_instruction("Test instruction")
        builder.set_response_format("Test format")
        builder.add_variable("test_var")
        builder.set_metadata("author", "test_user")
        
        result = builder.to_dict()
        
        assert result["task"] == "Test task"
        assert "Test context" in result["context"]
        assert "Test instruction" in result["instructions"]
        assert "Test format" in result["response_format"]
        assert "test_var" in result["variables"]
        assert result["metadata"]["author"] == "test_user"
    
    def test_from_dict_deserializes_correctly(self):
        """Test that from_dict properly deserializes builder state"""
        data = {
            "task": "Test task",
            "context": ["Test context"],
            "instructions": ["Test instruction"],
            "response_format": ["Test format"],
            "variables": ["test_var"],
            "metadata": {"author": "test_user"}
        }
        
        builder = OptimizedPromptBuilder.from_dict(data)
        
        assert builder.task == "Test task"
        assert "Test context" in builder.context
        assert "Test instruction" in builder.instructions
        assert "Test format" in builder.response_format
        assert "test_var" in builder.variables
        assert builder.metadata["author"] == "test_user"
    
    def test_method_chaining_works(self):
        """Test that all methods support method chaining"""
        builder = OptimizedPromptBuilder()
        
        result = (builder
                 .set_task("Test task")
                 .add_context("Test context")
                 .add_instruction("Test instruction")
                 .set_response_format("Test format")
                 .add_variable("test_var")
                 .set_metadata("key", "value"))
        
        assert result is builder
        assert builder.task == "Test task"
        assert len(builder.context) == 1
        assert len(builder.instructions) == 1
        assert len(builder.response_format) == 1
        assert len(builder.variables) == 1
        assert builder.metadata["key"] == "value"


class TestNovaPromptTemplate:
    """Test the NovaPromptTemplate functionality"""
    
    def test_apply_best_practices_formats_correctly(self):
        """Test that apply_best_practices formats prompts correctly"""
        builder = OptimizedPromptBuilder()
        builder.set_task("Analyze sentiment")
        builder.add_context("Customer feedback")
        builder.add_instruction("MUST classify sentiment")
        builder.set_response_format("JSON format")
        builder.add_variable("input_text")
        
        result = NovaPromptTemplate.apply_best_practices(builder)
        
        assert "Task: Analyze sentiment" in result["system_prompt"]
        assert "Context:\n- Customer feedback" in result["system_prompt"]
        assert "Instructions:\n- MUST classify sentiment" in result["system_prompt"]
        assert "Response Format:\n- JSON format" in result["system_prompt"]
        assert "input_text: {{input_text}}" in result["user_prompt"]
    
    def test_validate_structure_catches_missing_sections(self):
        """Test that validate_structure catches missing required sections"""
        incomplete_prompt = {
            "system_prompt": "Task: Test\nSome content",
            "user_prompt": "Test input"
        }
        
        issues = NovaPromptTemplate.validate_structure(incomplete_prompt)
        
        assert "Missing required section: Context:" in issues
        assert "Missing required section: Instructions:" in issues
        assert "Missing required section: Response Format:" in issues
    
    def test_validate_structure_suggests_strong_directives(self):
        """Test that validate_structure suggests strong directive language"""
        weak_prompt = {
            "system_prompt": "Task: Test\nContext: Test\nInstructions: Please classify\nResponse Format: JSON",
            "user_prompt": "Test input"
        }
        
        issues = NovaPromptTemplate.validate_structure(weak_prompt)
        
        assert any("stronger directive language" in issue for issue in issues)
    
    def test_validate_structure_passes_for_good_prompt(self):
        """Test that validate_structure passes for well-structured prompts"""
        good_prompt = {
            "system_prompt": "Task: Test\nContext: Test\nInstructions: MUST classify\nResponse Format: JSON",
            "user_prompt": "Test input"
        }
        
        issues = NovaPromptTemplate.validate_structure(good_prompt)
        
        assert len(issues) == 0


class TestValidationResult:
    """Test the ValidationResult dataclass"""
    
    def test_validation_result_creation(self):
        """Test ValidationResult creation and default values"""
        result = ValidationResult(is_valid=True)
        
        assert result.is_valid
        assert result.issues == []
        assert result.suggestions == []
        assert result.best_practices == {}
    
    def test_validation_result_with_data(self):
        """Test ValidationResult with actual data"""
        result = ValidationResult(
            is_valid=False,
            issues=["Missing task"],
            suggestions=["Add more context"],
            best_practices={"has_task": False}
        )
        
        assert not result.is_valid
        assert "Missing task" in result.issues
        assert "Add more context" in result.suggestions
        assert not result.best_practices["has_task"]
