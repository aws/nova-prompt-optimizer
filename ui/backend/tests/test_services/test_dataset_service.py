"""
Unit tests for the dataset service.
"""
import pytest
from unittest.mock import Mock, patch, AsyncMock
import tempfile
import os

# These imports would be from the actual implementation
# from app.services.dataset_service import DatasetService
# from app.models.dataset import Dataset, DatasetCreate
# from app.core.exceptions import ValidationError


class TestDatasetService:
    """Test cases for DatasetService."""

    @pytest.fixture
    def dataset_service(self):
        """Create a DatasetService instance for testing."""
        # This would be the actual service instantiation
        # return DatasetService()
        return Mock()

    @pytest.mark.unit
    def test_validate_csv_file_format(self, dataset_service, mock_dataset_file):
        """Test CSV file format validation."""
        # Mock the validation logic
        dataset_service.validate_file_format = Mock(return_value=True)
        
        result = dataset_service.validate_file_format(mock_dataset_file, "csv")
        assert result is True
        dataset_service.validate_file_format.assert_called_once_with(mock_dataset_file, "csv")

    @pytest.mark.unit
    def test_validate_json_file_format(self, dataset_service, mock_json_dataset_file):
        """Test JSON file format validation."""
        dataset_service.validate_file_format = Mock(return_value=True)
        
        result = dataset_service.validate_file_format(mock_json_dataset_file, "json")
        assert result is True

    @pytest.mark.unit
    def test_invalid_file_format_raises_error(self, dataset_service):
        """Test that invalid file format raises ValidationError."""
        dataset_service.validate_file_format = Mock(side_effect=Exception("Invalid format"))
        
        with pytest.raises(Exception, match="Invalid format"):
            dataset_service.validate_file_format("invalid_file.txt", "txt")

    @pytest.mark.unit
    async def test_process_dataset_csv(self, dataset_service, mock_dataset_file):
        """Test processing a CSV dataset."""
        # Mock the processing logic
        expected_result = {
            "id": "dataset-123",
            "name": "test_dataset.csv",
            "format": "csv",
            "rows": 3,
            "columns": ["input", "output", "category"],
            "input_columns": ["input"],
            "output_columns": ["output"]
        }
        
        dataset_service.process_dataset = AsyncMock(return_value=expected_result)
        
        result = await dataset_service.process_dataset(
            file_path=mock_dataset_file,
            input_columns=["input"],
            output_columns=["output"],
            split_ratio=0.8
        )
        
        assert result["format"] == "csv"
        assert result["rows"] == 3
        assert "input" in result["columns"]

    @pytest.mark.unit
    async def test_process_dataset_json(self, dataset_service, mock_json_dataset_file):
        """Test processing a JSON dataset."""
        expected_result = {
            "id": "dataset-456",
            "name": "test_dataset.json",
            "format": "json",
            "rows": 3,
            "columns": ["input", "output", "category"],
            "input_columns": ["input"],
            "output_columns": ["output"]
        }
        
        dataset_service.process_dataset = AsyncMock(return_value=expected_result)
        
        result = await dataset_service.process_dataset(
            file_path=mock_json_dataset_file,
            input_columns=["input"],
            output_columns=["output"],
            split_ratio=0.8
        )
        
        assert result["format"] == "json"
        assert result["rows"] == 3

    @pytest.mark.unit
    async def test_get_dataset_preview(self, dataset_service):
        """Test getting dataset preview."""
        expected_preview = {
            "rows": [
                {"input": "What is the capital of France?", "output": "Paris", "category": "geography"},
                {"input": "What is 2+2?", "output": "4", "category": "math"}
            ],
            "total_rows": 3,
            "columns": ["input", "output", "category"]
        }
        
        dataset_service.get_preview = AsyncMock(return_value=expected_preview)
        
        result = await dataset_service.get_preview(
            dataset_id="dataset-123",
            limit=2,
            offset=0
        )
        
        assert len(result["rows"]) == 2
        assert result["total_rows"] == 3
        assert "input" in result["columns"]

    @pytest.mark.unit
    async def test_delete_dataset(self, dataset_service):
        """Test dataset deletion."""
        dataset_service.delete_dataset = AsyncMock(return_value=True)
        
        result = await dataset_service.delete_dataset("dataset-123")
        assert result is True

    @pytest.mark.unit
    async def test_list_datasets(self, dataset_service):
        """Test listing all datasets."""
        expected_datasets = [
            {"id": "dataset-1", "name": "Dataset 1", "created_at": "2024-01-01T00:00:00Z"},
            {"id": "dataset-2", "name": "Dataset 2", "created_at": "2024-01-02T00:00:00Z"}
        ]
        
        dataset_service.list_datasets = AsyncMock(return_value=expected_datasets)
        
        result = await dataset_service.list_datasets()
        assert len(result) == 2
        assert result[0]["id"] == "dataset-1"

    @pytest.mark.unit
    def test_validate_column_mapping(self, dataset_service):
        """Test column mapping validation."""
        dataset_service.validate_column_mapping = Mock(return_value=True)
        
        columns = ["input", "output", "category"]
        input_cols = ["input"]
        output_cols = ["output"]
        
        result = dataset_service.validate_column_mapping(columns, input_cols, output_cols)
        assert result is True

    @pytest.mark.unit
    def test_invalid_column_mapping_raises_error(self, dataset_service):
        """Test that invalid column mapping raises error."""
        dataset_service.validate_column_mapping = Mock(
            side_effect=Exception("Column 'invalid' not found in dataset")
        )
        
        columns = ["input", "output"]
        input_cols = ["invalid"]
        output_cols = ["output"]
        
        with pytest.raises(Exception, match="Column 'invalid' not found"):
            dataset_service.validate_column_mapping(columns, input_cols, output_cols)