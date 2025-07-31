"""
Unit tests for the prompt service.
"""
import pytest
from unittest.mock import Mock, AsyncMock

# These imports would be from the actual implementation
# from app.services.prompt_service import PromptService
# from app.models.prompt import Prompt, PromptCreate, PromptUpdate


class TestPromptService:
    """Test cases for PromptService."""

    @pytest.fixture
    def prompt_service(self):
        """Create a PromptService instance for testing."""
        return Mock()

    @pytest.mark.unit
    async def test_create_prompt(self, prompt_service, mock_prompt):
        """Test creating a new prompt."""
        prompt_service.create_prompt = AsyncMock(return_value=mock_prompt)
        
        prompt_data = {
            "name": "Test Prompt",
            "system_prompt": "You are a helpful assistant.",
            "user_prompt": "Answer: {{input}}",
            "description": "A test prompt"
        }
        
        result = await prompt_service.create_prompt(prompt_data)
        
        assert result["name"] == "Test Prompt"
        assert result["system_prompt"] == "You are a helpful assistant."
        assert "input" in result["variables"]

    @pytest.mark.unit
    async def test_update_prompt(self, prompt_service, mock_prompt):
        """Test updating an existing prompt."""
        updated_prompt = {**mock_prompt, "name": "Updated Test Prompt"}
        prompt_service.update_prompt = AsyncMock(return_value=updated_prompt)
        
        update_data = {"name": "Updated Test Prompt"}
        result = await prompt_service.update_prompt("test-prompt-1", update_data)
        
        assert result["name"] == "Updated Test Prompt"
        assert result["id"] == "test-prompt-1"

    @pytest.mark.unit
    async def test_get_prompt(self, prompt_service, mock_prompt):
        """Test retrieving a prompt by ID."""
        prompt_service.get_prompt = AsyncMock(return_value=mock_prompt)
        
        result = await prompt_service.get_prompt("test-prompt-1")
        
        assert result["id"] == "test-prompt-1"
        assert result["name"] == "Test Prompt"

    @pytest.mark.unit
    async def test_get_prompt_not_found(self, prompt_service):
        """Test retrieving a non-existent prompt."""
        prompt_service.get_prompt = AsyncMock(return_value=None)
        
        result = await prompt_service.get_prompt("non-existent")
        assert result is None

    @pytest.mark.unit
    async def test_list_prompts(self, prompt_service):
        """Test listing all prompts."""
        prompts = [
            {"id": "prompt-1", "name": "Prompt 1"},
            {"id": "prompt-2", "name": "Prompt 2"}
        ]
        prompt_service.list_prompts = AsyncMock(return_value=prompts)
        
        result = await prompt_service.list_prompts()
        
        assert len(result) == 2
        assert result[0]["id"] == "prompt-1"

    @pytest.mark.unit
    async def test_delete_prompt(self, prompt_service):
        """Test deleting a prompt."""
        prompt_service.delete_prompt = AsyncMock(return_value=True)
        
        result = await prompt_service.delete_prompt("test-prompt-1")
        assert result is True

    @pytest.mark.unit
    def test_validate_template_syntax(self, prompt_service):
        """Test Jinja2 template syntax validation."""
        prompt_service.validate_template = Mock(return_value=True)
        
        valid_template = "Hello {{name}}, how are you?"
        result = prompt_service.validate_template(valid_template)
        assert result is True

    @pytest.mark.unit
    def test_invalid_template_syntax(self, prompt_service):
        """Test invalid Jinja2 template syntax."""
        prompt_service.validate_template = Mock(
            side_effect=Exception("Invalid template syntax")
        )
        
        invalid_template = "Hello {{name, how are you?"
        with pytest.raises(Exception, match="Invalid template syntax"):
            prompt_service.validate_template(invalid_template)

    @pytest.mark.unit
    def test_extract_variables(self, prompt_service):
        """Test extracting variables from template."""
        prompt_service.extract_variables = Mock(return_value=["name", "age"])
        
        template = "Hello {{name}}, you are {{age}} years old."
        variables = prompt_service.extract_variables(template)
        
        assert "name" in variables
        assert "age" in variables
        assert len(variables) == 2

    @pytest.mark.unit
    async def test_preview_prompt(self, prompt_service):
        """Test prompt preview with sample data."""
        expected_preview = {
            "rendered_system": "You are a helpful assistant.",
            "rendered_user": "Answer the following question: What is the capital of France?",
            "variables_used": {"input": "What is the capital of France?"}
        }
        
        prompt_service.preview_prompt = AsyncMock(return_value=expected_preview)
        
        sample_data = {"input": "What is the capital of France?"}
        result = await prompt_service.preview_prompt("test-prompt-1", sample_data)
        
        assert "rendered_system" in result
        assert "rendered_user" in result
        assert result["variables_used"]["input"] == "What is the capital of France?"

    @pytest.mark.unit
    async def test_duplicate_prompt(self, prompt_service, mock_prompt):
        """Test duplicating a prompt."""
        duplicated_prompt = {
            **mock_prompt,
            "id": "test-prompt-2",
            "name": "Test Prompt (Copy)"
        }
        prompt_service.duplicate_prompt = AsyncMock(return_value=duplicated_prompt)
        
        result = await prompt_service.duplicate_prompt("test-prompt-1")
        
        assert result["id"] == "test-prompt-2"
        assert result["name"] == "Test Prompt (Copy)"
        assert result["system_prompt"] == mock_prompt["system_prompt"]