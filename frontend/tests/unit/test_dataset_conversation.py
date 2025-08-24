"""Unit tests for dataset conversation service"""

import pytest
from unittest.mock import Mock, patch
from dataset_conversation import DatasetConversationService, RequirementsChecklist


class TestRequirementsChecklist:
    
    def test_checklist_creation(self):
        """Test checklist can be created"""
        checklist = RequirementsChecklist()
        assert checklist is not None
        assert checklist.dataset_format == "jsonl"
    
    def test_is_complete_empty(self):
        """Test incomplete checklist"""
        checklist = RequirementsChecklist()
        assert checklist.is_complete() is False
    
    def test_is_complete_filled(self):
        """Test complete checklist"""
        checklist = RequirementsChecklist(
            role_persona="test role",
            task_goal="test task",
            use_case="test use case",
            input_format="test input",
            output_format="test output"
        )
        assert checklist.is_complete() is True
    
    def test_get_missing_fields(self):
        """Test missing fields detection"""
        checklist = RequirementsChecklist(role_persona="test role")
        missing = checklist.get_missing_fields()
        assert "task_goal" in missing
        assert "use_case" in missing
        assert "role_persona" not in missing


class TestDatasetConversationService:
    
    def setup_method(self):
        """Setup test fixtures"""
        with patch('dataset_conversation.boto3.client'):
            self.service = DatasetConversationService()
    
    def test_service_creation(self):
        """Test service can be created"""
        assert self.service is not None
        assert self.service.model_id == "us.amazon.nova-premier-v1:0"
    
    def test_extract_from_prompt_role(self):
        """Test role extraction from prompt"""
        prompt = "You are a helpful assistant for customer service."
        result = self.service._extract_from_prompt("role")
        # Should extract from stored prompt
        assert isinstance(result, str)
    
    def test_extract_from_prompt_task(self):
        """Test task extraction from prompt"""
        self.service.original_prompt = "You must analyze each interaction and provide classifications"
        result = self.service._extract_from_prompt("task")
        assert "analyze" in result.lower()
    
    def test_clean_prompt_display(self):
        """Test prompt display cleaning"""
        malformed_xml = '<gender reasoning="test"</gender reasoning>'
        cleaned = self.service._clean_prompt_display(malformed_xml)
        assert '</gender>' in cleaned
        assert 'reasoning>' not in cleaned
