"""Unit tests for simple dataset generator"""

import pytest
import json
from unittest.mock import Mock, patch

# Try services import first, fallback to root
try:
    from services.simple_dataset_generator import SimpleDatasetGenerator
except ImportError:
    from simple_dataset_generator import SimpleDatasetGenerator


class TestSimpleDatasetGenerator:
    
    def setup_method(self):
        """Setup test fixtures"""
        with patch('simple_dataset_generator.boto3.client'):
            self.generator = SimpleDatasetGenerator()
    
    def test_generator_creation(self):
        """Test generator can be created"""
        assert self.generator is not None
        assert self.generator.model_id == "us.amazon.nova-pro-v1:0"
    
    @patch('simple_dataset_generator.boto3.client')
    def test_generate_sample_success(self, mock_boto):
        """Test successful sample generation"""
        # Mock Bedrock response
        mock_response = {
            'body': Mock()
        }
        mock_response['body'].read.return_value = json.dumps({
            'output': {
                'message': {
                    'content': [{'text': '{"input": "test question", "output": "test response"}'}]
                }
            }
        }).encode('utf-8')
        
        mock_boto.return_value.invoke_model.return_value = mock_response
        
        # Create new generator with mocked client
        generator = SimpleDatasetGenerator()
        result = generator.generate_sample("test prompt", 1)
        
        assert result["success"] is True
        assert "sample" in result
        assert result["sample"]["input"] == "test question"
        assert result["sample"]["output"] == "test response"
    
    @patch('simple_dataset_generator.boto3.client')
    def test_generate_sample_error(self, mock_boto):
        """Test error handling in sample generation"""
        mock_boto.return_value.invoke_model.side_effect = Exception("API Error")
        
        generator = SimpleDatasetGenerator()
        result = generator.generate_sample("test prompt", 1)
        
        assert result["success"] is False
        assert "error" in result
    
    @patch('simple_dataset_generator.boto3.client')
    def test_generate_dataset_multiple_samples(self, mock_boto):
        """Test generating multiple samples"""
        # Mock successful responses
        mock_response = {
            'body': Mock()
        }
        mock_response['body'].read.return_value = json.dumps({
            'output': {
                'message': {
                    'content': [{'text': '{"input": "test question", "output": "test response"}'}]
                }
            }
        }).encode('utf-8')
        
        mock_boto.return_value.invoke_model.return_value = mock_response
        
        generator = SimpleDatasetGenerator()
        result = generator.generate_dataset("test prompt", 3)
        
        assert result["success"] is True
        assert len(result["samples"]) == 3
        assert result["total_generated"] == 3
        assert len(result["errors"]) == 0
