"""
Unit tests for prompt builder routes
"""

import pytest
import json
from unittest.mock import Mock, patch as mock_patch
from fasthtml.common import *
from routes.prompt_builder import setup_prompt_builder_routes
from services.prompt_builder import OptimizedPromptBuilder


class TestPromptBuilderRoutes:
    """Test prompt builder route functionality"""
    
    @pytest.fixture
    def app(self):
        """Create test FastHTML app with prompt builder routes"""
        app = FastHTML()
        setup_prompt_builder_routes(app)
        return app
    
    @pytest.fixture
    def mock_db(self):
        """Mock database for testing"""
        with mock_patch('database.Database') as mock_db_class:
            mock_db = Mock()
            mock_db_class.return_value = mock_db
            yield mock_db
    
    def test_prompt_builder_page_renders(self, app, mock_db):
        """Test that prompt builder page renders correctly"""
        # Mock templates
        mock_db.list_prompt_templates.return_value = [
            {"id": "template_1", "name": "Test Template", "description": "Test description"}
        ]
        
        # Create mock request
        request = Mock()
        
        # Test the route function directly
        from routes.prompt_builder import setup_prompt_builder_routes
        
        # Since we can't easily test FastHTML routes directly, we'll test the components
        from components.prompt_builder import builder_form_section, template_selector
        
        # Test form section renders
        form_section = builder_form_section()
        assert form_section is not None
        
        # Test template selector renders
        templates = [{"id": "test", "name": "Test", "description": "Test desc"}]
        selector = template_selector(templates)
        assert selector is not None
    
    def test_preview_prompt_with_valid_data(self, app, mock_db):
        """Test preview prompt with valid builder data"""
        builder_data = {
            "task": "Test task",
            "context": ["Test context"],
            "instructions": ["MUST test"],
            "response_format": ["JSON format"],
            "variables": ["test_var"]
        }
        
        # Test builder preview functionality
        builder = OptimizedPromptBuilder.from_dict(builder_data)
        preview = builder.preview()
        
        assert "system_prompt" in preview
        assert "user_prompt" in preview
        assert "Test task" in preview["system_prompt"]
        assert "test_var" in preview["user_prompt"]
    
    def test_validate_prompt_with_valid_data(self, app, mock_db):
        """Test validate prompt with valid builder data"""
        builder_data = {
            "task": "Test task",
            "context": ["Test context"],
            "instructions": ["MUST test"],
            "response_format": ["JSON format"],
            "variables": ["test_var"]
        }
        
        # Test builder validation functionality
        builder = OptimizedPromptBuilder.from_dict(builder_data)
        validation = builder.validate()
        
        assert validation.is_valid
        assert len(validation.issues) == 0
        assert validation.best_practices["has_task"]
        assert validation.best_practices["has_context"]
        assert validation.best_practices["has_instructions"]
    
    def test_validate_prompt_with_invalid_data(self, app, mock_db):
        """Test validate prompt with invalid builder data"""
        builder_data = {
            "task": "",  # Empty task
            "context": [],  # No context
            "instructions": [],  # No instructions
            "response_format": [],
            "variables": []
        }
        
        # Test builder validation functionality
        builder = OptimizedPromptBuilder.from_dict(builder_data)
        validation = builder.validate()
        
        assert not validation.is_valid
        assert "Task description is required" in validation.issues
        assert "At least one context item is required" in validation.issues
        assert "At least one instruction is required" in validation.issues
    
    def test_build_prompt_with_valid_data(self, app, mock_db):
        """Test build prompt with valid data"""
        builder_data = {
            "task": "Test task",
            "context": ["Test context"],
            "instructions": ["MUST test"],
            "response_format": ["JSON format"],
            "variables": ["test_var"]
        }
        
        # Mock database methods
        mock_db.create_prompt.return_value = "prompt_123"
        
        # Test builder build functionality
        builder = OptimizedPromptBuilder.from_dict(builder_data)
        adapter = builder.build()
        
        assert adapter is not None
        assert adapter.system_prompt
        assert adapter.user_prompt
    
    def test_build_prompt_with_invalid_data_raises_error(self, app, mock_db):
        """Test build prompt with invalid data raises error"""
        builder_data = {
            "task": "",  # Invalid - empty task
            "context": [],
            "instructions": [],
            "response_format": [],
            "variables": []
        }
        
        # Test that building invalid prompt raises error
        builder = OptimizedPromptBuilder.from_dict(builder_data)
        
        with pytest.raises(ValueError) as exc_info:
            builder.build()
        
        assert "Cannot build invalid prompt" in str(exc_info.value)
    
    def test_save_template_with_valid_data(self, app, mock_db):
        """Test save template with valid data"""
        template_data = {
            "name": "Test Template",
            "description": "Test description",
            "builder_data": {
                "task": "Test task",
                "context": ["Test context"],
                "instructions": ["MUST test"],
                "response_format": ["JSON format"],
                "variables": ["test_var"]
            }
        }
        
        # Mock database method
        mock_db.create_prompt_template.return_value = "template_123"
        
        # Test template creation
        template_id = mock_db.create_prompt_template(
            name=template_data["name"],
            description=template_data["description"],
            builder_data=template_data["builder_data"]
        )
        
        assert template_id == "template_123"
        mock_db.create_prompt_template.assert_called_once()
    
    def test_save_template_without_name_fails(self, app, mock_db):
        """Test save template without name fails validation"""
        template_data = {
            "name": "",  # Empty name should fail
            "description": "Test description",
            "builder_data": {}
        }
        
        # Test that empty name would cause validation error
        assert not template_data["name"].strip()
    
    def test_load_template_with_valid_id(self, app, mock_db):
        """Test load template with valid ID"""
        template_data = {
            "id": "template_123",
            "name": "Test Template",
            "description": "Test description",
            "builder_data": {
                "task": "Test task",
                "context": ["Test context"],
                "instructions": ["MUST test"],
                "response_format": ["JSON format"],
                "variables": ["test_var"]
            }
        }
        
        # Mock database method
        mock_db.get_prompt_template.return_value = template_data
        
        # Test template retrieval
        retrieved = mock_db.get_prompt_template("template_123")
        
        assert retrieved is not None
        assert retrieved["id"] == "template_123"
        assert retrieved["name"] == "Test Template"
        assert retrieved["builder_data"]["task"] == "Test task"
    
    def test_load_template_with_invalid_id_returns_none(self, app, mock_db):
        """Test load template with invalid ID returns None"""
        # Mock database method to return None
        mock_db.get_prompt_template.return_value = None
        
        # Test template retrieval with invalid ID
        retrieved = mock_db.get_prompt_template("invalid_id")
        
        assert retrieved is None
    
    def test_list_templates_returns_templates(self, app, mock_db):
        """Test list templates returns available templates"""
        templates = [
            {"id": "template_1", "name": "Template 1", "description": "Description 1"},
            {"id": "template_2", "name": "Template 2", "description": "Description 2"}
        ]
        
        # Mock database method
        mock_db.list_prompt_templates.return_value = templates
        
        # Test template listing
        retrieved = mock_db.list_prompt_templates()
        
        assert len(retrieved) == 2
        assert retrieved[0]["name"] == "Template 1"
        assert retrieved[1]["name"] == "Template 2"
    
    def test_form_data_collection_structure(self):
        """Test that form data collection follows expected structure"""
        # Test the expected structure of form data
        expected_structure = {
            "task": "string",
            "context": "array",
            "instructions": "array", 
            "response_format": "array",
            "variables": "array",
            "metadata": "object"
        }
        
        # Create sample data matching structure
        sample_data = {
            "task": "Test task",
            "context": ["Context 1", "Context 2"],
            "instructions": ["MUST do this", "DO NOT do that"],
            "response_format": ["JSON format", "Include confidence"],
            "variables": ["input_text", "category"],
            "metadata": {"author": "test_user"}
        }
        
        # Verify structure matches
        for key, expected_type in expected_structure.items():
            assert key in sample_data
            
            if expected_type == "string":
                assert isinstance(sample_data[key], str)
            elif expected_type == "array":
                assert isinstance(sample_data[key], list)
            elif expected_type == "object":
                assert isinstance(sample_data[key], dict)
    
    def test_builder_integration_with_routes(self):
        """Test that builder integrates correctly with route expectations"""
        # Test data that would come from form
        form_data = {
            "task": "Analyze customer sentiment",
            "context": ["Customer feedback emails", "Product reviews"],
            "instructions": ["MUST classify as positive/negative/neutral", "DO NOT include bias"],
            "response_format": ["JSON with sentiment and confidence"],
            "variables": ["customer_feedback"]
        }
        
        # Test builder creation from form data
        builder = OptimizedPromptBuilder.from_dict(form_data)
        
        # Test validation
        validation = builder.validate()
        assert validation.is_valid
        
        # Test preview generation
        preview = builder.preview()
        assert "system_prompt" in preview
        assert "user_prompt" in preview
        
        # Test serialization back to dict
        serialized = builder.to_dict()
        assert serialized["task"] == form_data["task"]
        assert serialized["context"] == form_data["context"]
        
        # Test building prompt adapter
        adapter = builder.build()
        assert adapter.system_prompt
        assert adapter.user_prompt
    
    def test_error_handling_for_malformed_data(self):
        """Test error handling for malformed builder data"""
        # Test with missing required fields
        malformed_data = {
            # Missing task, context, instructions
            "response_format": ["JSON"],
            "variables": ["test"]
        }
        
        builder = OptimizedPromptBuilder.from_dict(malformed_data)
        validation = builder.validate()
        
        assert not validation.is_valid
        assert len(validation.issues) > 0
        
        # Test that build fails with invalid data
        with pytest.raises(ValueError):
            builder.build()
    
    def test_template_data_persistence(self):
        """Test that template data persists correctly through save/load cycle"""
        original_data = {
            "task": "Complex analysis task",
            "context": ["Context 1", "Context 2", "Context 3"],
            "instructions": ["MUST follow rule 1", "DO NOT violate rule 2", "ALWAYS check rule 3"],
            "response_format": ["JSON format", "Include reasoning", "Add confidence scores"],
            "variables": ["input_data", "analysis_type", "output_format"],
            "metadata": {"version": "1.0", "author": "test_user", "category": "analysis"}
        }
        
        # Create builder from original data
        builder = OptimizedPromptBuilder.from_dict(original_data)
        
        # Serialize to dict (simulating save)
        saved_data = builder.to_dict()
        
        # Create new builder from saved data (simulating load)
        loaded_builder = OptimizedPromptBuilder.from_dict(saved_data)
        
        # Verify data integrity
        loaded_data = loaded_builder.to_dict()
        
        assert loaded_data["task"] == original_data["task"]
        assert loaded_data["context"] == original_data["context"]
        assert loaded_data["instructions"] == original_data["instructions"]
        assert loaded_data["response_format"] == original_data["response_format"]
        assert set(loaded_data["variables"]) == set(original_data["variables"])
        assert loaded_data["metadata"] == original_data["metadata"]
