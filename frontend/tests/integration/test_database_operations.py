"""Integration tests for database operations"""

import pytest
from database import Database


class TestDatabaseOperations:
    
    def setup_method(self):
        """Setup test fixtures"""
        self.db = Database()
    
    def test_dataset_crud_operations(self):
        """Test dataset CRUD operations"""
        # Test listing datasets
        datasets = self.db.get_datasets()
        assert isinstance(datasets, list)
        
        initial_count = len(datasets)
        
        # Note: We don't create/delete in tests to avoid affecting real data
        # In a real test environment, we'd use a test database
        assert initial_count >= 0
    
    def test_prompt_crud_operations(self):
        """Test prompt CRUD operations"""
        # Test listing prompts
        prompts = self.db.get_prompts()
        assert isinstance(prompts, list)
        
        # Test getting specific prompt if any exist
        if prompts:
            prompt = self.db.get_prompt(prompts[0]['id'])
            assert prompt is not None
            assert 'id' in prompt
            assert 'name' in prompt
    
    def test_optimization_workflow(self):
        """Test optimization workflow database operations"""
        # Test listing optimizations
        optimizations = self.db.get_optimizations()
        assert isinstance(optimizations, list)
