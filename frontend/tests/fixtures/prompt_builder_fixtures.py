"""
Test fixtures for prompt builder tests
"""

import pytest
from services.prompt_builder import OptimizedPromptBuilder


@pytest.fixture
def sample_builder_data():
    """Sample valid builder data for testing"""
    return {
        "task": "Analyze customer feedback sentiment",
        "context": [
            "Customer support emails and chat logs",
            "Product review comments from e-commerce platform",
            "Social media mentions and feedback"
        ],
        "instructions": [
            "MUST classify sentiment as positive, negative, or neutral",
            "DO NOT include personal opinions or bias",
            "MUST provide confidence score between 0.0 and 1.0",
            "Include key phrases that influenced the classification"
        ],
        "response_format": [
            "JSON format with sentiment, confidence, and key_phrases fields",
            "Sentiment must be one of: positive, negative, neutral",
            "Confidence must be a float between 0.0 and 1.0"
        ],
        "variables": ["customer_feedback", "product_name"],
        "metadata": {
            "author": "test_user",
            "version": "1.0",
            "category": "sentiment_analysis"
        }
    }


@pytest.fixture
def minimal_builder_data():
    """Minimal valid builder data for testing"""
    return {
        "task": "Simple classification task",
        "context": ["Basic context"],
        "instructions": ["MUST classify input"],
        "response_format": ["Simple text response"],
        "variables": ["input"],
        "metadata": {}
    }


@pytest.fixture
def invalid_builder_data():
    """Invalid builder data for testing error cases"""
    return {
        "task": "",  # Empty task
        "context": [],  # No context
        "instructions": [],  # No instructions
        "response_format": [],
        "variables": [],
        "metadata": {}
    }


@pytest.fixture
def sample_builder():
    """Pre-configured OptimizedPromptBuilder for testing"""
    builder = OptimizedPromptBuilder()
    builder.set_task("Analyze customer feedback sentiment")
    builder.add_context("Customer support emails and chat logs")
    builder.add_context("Product review comments")
    builder.add_instruction("MUST classify sentiment as positive, negative, or neutral")
    builder.add_instruction("DO NOT include personal opinions")
    builder.set_response_format("JSON format with sentiment and confidence fields")
    builder.add_variable("customer_feedback")
    builder.add_variable("product_name")
    builder.set_metadata("author", "test_user")
    return builder


@pytest.fixture
def minimal_builder():
    """Minimal valid OptimizedPromptBuilder for testing"""
    builder = OptimizedPromptBuilder()
    builder.set_task("Simple task")
    builder.add_context("Basic context")
    builder.add_instruction("MUST process input")
    return builder


@pytest.fixture
def empty_builder():
    """Empty OptimizedPromptBuilder for testing"""
    return OptimizedPromptBuilder()


@pytest.fixture
def mock_prompt_adapter():
    """Mock PromptAdapter for testing without SDK dependencies"""
    class MockPromptAdapter:
        def __init__(self):
            self.system_prompt = ""
            self.user_prompt = ""
            self.adapted = False
        
        def set_system_prompt(self, content, variables=None):
            self.system_prompt = content
            return self
        
        def set_user_prompt(self, content, variables=None):
            self.user_prompt = content
            return self
        
        def adapt(self):
            self.adapted = True
            return self
    
    return MockPromptAdapter()


@pytest.fixture
def sample_validation_cases():
    """Sample validation test cases"""
    return {
        "valid_cases": [
            {
                "name": "complete_prompt",
                "data": {
                    "task": "Analyze sentiment",
                    "context": ["Customer feedback"],
                    "instructions": ["MUST classify sentiment"],
                    "response_format": ["JSON format"],
                    "variables": ["input_text"]
                },
                "expected_valid": True
            },
            {
                "name": "minimal_valid",
                "data": {
                    "task": "Simple task",
                    "context": ["Context"],
                    "instructions": ["DO NOT fail"],
                    "response_format": [],
                    "variables": []
                },
                "expected_valid": True
            }
        ],
        "invalid_cases": [
            {
                "name": "missing_task",
                "data": {
                    "task": "",
                    "context": ["Context"],
                    "instructions": ["Instruction"],
                    "response_format": [],
                    "variables": []
                },
                "expected_issues": ["Task description is required"]
            },
            {
                "name": "missing_context",
                "data": {
                    "task": "Task",
                    "context": [],
                    "instructions": ["Instruction"],
                    "response_format": [],
                    "variables": []
                },
                "expected_issues": ["At least one context item is required"]
            },
            {
                "name": "missing_instructions",
                "data": {
                    "task": "Task",
                    "context": ["Context"],
                    "instructions": [],
                    "response_format": [],
                    "variables": []
                },
                "expected_issues": ["At least one instruction is required"]
            }
        ]
    }


@pytest.fixture
def sample_prompt_templates():
    """Sample prompt templates for testing"""
    return {
        "sentiment_analysis": {
            "name": "Customer Sentiment Analysis",
            "description": "Analyze customer feedback sentiment",
            "builder_data": {
                "task": "Analyze customer feedback sentiment",
                "context": [
                    "Customer support interactions",
                    "Product reviews and ratings"
                ],
                "instructions": [
                    "MUST classify sentiment as positive, negative, or neutral",
                    "DO NOT include personal bias",
                    "MUST provide confidence score"
                ],
                "response_format": [
                    "JSON format with sentiment, confidence, and reasoning"
                ],
                "variables": ["customer_feedback"]
            }
        },
        "text_classification": {
            "name": "General Text Classification",
            "description": "Classify text into predefined categories",
            "builder_data": {
                "task": "Classify text into appropriate categories",
                "context": [
                    "Text classification requirements",
                    "Available category definitions"
                ],
                "instructions": [
                    "MUST select exactly one category",
                    "DO NOT create new categories",
                    "MUST explain reasoning"
                ],
                "response_format": [
                    "Category name and explanation"
                ],
                "variables": ["input_text", "categories"]
            }
        }
    }


@pytest.fixture
def mock_database():
    """Mock database for testing without actual database dependencies"""
    class MockDatabase:
        def __init__(self):
            self.templates = {}
            self.sessions = {}
            self.next_id = 1
        
        def create_prompt_template(self, name, builder_data):
            template_id = f"template_{self.next_id}"
            self.templates[template_id] = {
                "id": template_id,
                "name": name,
                "builder_data": builder_data
            }
            self.next_id += 1
            return template_id
        
        def get_prompt_template(self, template_id):
            return self.templates.get(template_id)
        
        def list_prompt_templates(self):
            return list(self.templates.values())
        
        def update_prompt_template(self, template_id, builder_data):
            if template_id in self.templates:
                self.templates[template_id]["builder_data"] = builder_data
                return True
            return False
        
        def delete_prompt_template(self, template_id):
            if template_id in self.templates:
                del self.templates[template_id]
                return True
            return False
    
    return MockDatabase()


@pytest.fixture
def performance_test_data():
    """Large dataset for performance testing"""
    return {
        "large_context": [f"Context item {i}" for i in range(100)],
        "large_instructions": [f"MUST follow rule {i}" for i in range(50)],
        "large_variables": [f"var_{i}" for i in range(20)],
        "complex_task": "This is a very complex task " * 100
    }
