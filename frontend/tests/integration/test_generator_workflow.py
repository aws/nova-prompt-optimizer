"""Integration tests for generator workflows"""

import pytest
from unittest.mock import Mock, patch
from database import Database

# Try services import first, fallback to root
try:
    from services.simple_dataset_generator import SimpleDatasetGenerator
except ImportError:
    from simple_dataset_generator import SimpleDatasetGenerator


class TestGeneratorWorkflow:
    
    def setup_method(self):
        """Setup test fixtures"""
        self.db = Database()
    
    def test_database_connection(self):
        """Test database connectivity"""
        assert self.db is not None
    
    def test_prompt_retrieval(self):
        """Test prompt can be retrieved from database"""
        prompts = self.db.get_prompts()
        assert isinstance(prompts, list)
    
    @patch('simple_dataset_generator.boto3.client')
    def test_end_to_end_simple_generation(self, mock_boto):
        """Test complete simple generation workflow"""
        # Mock Bedrock response
        mock_response = {
            'body': Mock()
        }
        mock_response['body'].read.return_value = '{"output": {"message": {"content": [{"text": "{\\"input\\": \\"test\\", \\"output\\": \\"response\\"}"}]}}}'
        mock_boto.return_value.invoke_model.return_value = mock_response
        
        from services.simple_dataset_generator import SimpleDatasetGenerator
        generator = SimpleDatasetGenerator()
        
        result = generator.generate_sample("test prompt", 1)
        assert result["success"] is True
    
    def test_prompt_to_dataset_workflow(self):
        """Test workflow from prompt selection to dataset generation"""
        # Get available prompts
        prompts = self.db.get_prompts()
        
        if prompts:
            # Test prompt retrieval
            prompt = self.db.get_prompt(prompts[0]['id'])
            assert prompt is not None
            assert 'variables' in prompt
