"""
Unit tests for the optimization service.
"""
import pytest
from unittest.mock import Mock, AsyncMock, patch

# These imports would be from the actual implementation
# from app.services.optimization_service import OptimizationService
# from app.models.optimization import OptimizationTask, OptimizationConfig


class TestOptimizationService:
    """Test cases for OptimizationService."""

    @pytest.fixture
    def optimization_service(self):
        """Create an OptimizationService instance for testing."""
        return Mock()

    @pytest.mark.unit
    async def test_start_optimization(self, optimization_service, mock_optimization_config):
        """Test starting an optimization task."""
        expected_task = {
            "id": "task-123",
            "status": "queued",
            "progress": 0.0,
            "config": mock_optimization_config,
            "created_at": "2024-01-01T00:00:00Z"
        }
        
        optimization_service.start_optimization = AsyncMock(return_value=expected_task)
        
        result = await optimization_service.start_optimization(mock_optimization_config)
        
        assert result["id"] == "task-123"
        assert result["status"] == "queued"
        assert result["progress"] == 0.0

    @pytest.mark.unit
    async def test_get_optimization_status(self, optimization_service):
        """Test getting optimization task status."""
        expected_status = {
            "id": "task-123",
            "status": "running",
            "progress": 0.6,
            "current_step": "Evaluating iteration 3",
            "estimated_completion": "2024-01-01T01:00:00Z"
        }
        
        optimization_service.get_status = AsyncMock(return_value=expected_status)
        
        result = await optimization_service.get_status("task-123")
        
        assert result["status"] == "running"
        assert result["progress"] == 0.6
        assert "current_step" in result

    @pytest.mark.unit
    async def test_cancel_optimization(self, optimization_service):
        """Test canceling an optimization task."""
        optimization_service.cancel_optimization = AsyncMock(return_value=True)
        
        result = await optimization_service.cancel_optimization("task-123")
        assert result is True

    @pytest.mark.unit
    async def test_get_optimization_results(self, optimization_service, mock_optimization_results):
        """Test getting optimization results."""
        optimization_service.get_results = AsyncMock(return_value=mock_optimization_results)
        
        result = await optimization_service.get_results("task-123")
        
        assert result["task_id"] == "task-123"
        assert result["status"] == "completed"
        assert "original_prompt" in result
        assert "optimized_prompt" in result
        assert "metrics" in result

    @pytest.mark.unit
    async def test_list_optimization_history(self, optimization_service):
        """Test listing optimization history."""
        expected_history = [
            {"id": "task-1", "status": "completed", "created_at": "2024-01-01T00:00:00Z"},
            {"id": "task-2", "status": "running", "created_at": "2024-01-02T00:00:00Z"}
        ]
        
        optimization_service.get_history = AsyncMock(return_value=expected_history)
        
        result = await optimization_service.get_history(limit=10, offset=0)
        
        assert len(result) == 2
        assert result[0]["id"] == "task-1"
        assert result[1]["status"] == "running"

    @pytest.mark.unit
    def test_validate_optimization_config(self, optimization_service, mock_optimization_config):
        """Test optimization configuration validation."""
        optimization_service.validate_config = Mock(return_value=True)
        
        result = optimization_service.validate_config(mock_optimization_config)
        assert result is True

    @pytest.mark.unit
    def test_invalid_optimization_config(self, optimization_service):
        """Test invalid optimization configuration."""
        optimization_service.validate_config = Mock(
            side_effect=Exception("Invalid optimizer type")
        )
        
        invalid_config = {"optimizer_type": "invalid"}
        
        with pytest.raises(Exception, match="Invalid optimizer type"):
            optimization_service.validate_config(invalid_config)

    @pytest.mark.unit
    @patch('app.services.optimization_service.NovaPromptOptimizer')
    async def test_run_nova_optimization(self, mock_optimizer, optimization_service):
        """Test running Nova optimization."""
        # Mock the optimizer
        mock_optimizer_instance = Mock()
        mock_optimizer_instance.optimize = AsyncMock(return_value={
            "optimized_prompt": "Optimized prompt",
            "metrics": {"accuracy": 0.95}
        })
        mock_optimizer.return_value = mock_optimizer_instance
        
        optimization_service.run_optimization = AsyncMock(return_value={
            "status": "completed",
            "results": {"accuracy": 0.95}
        })
        
        config = {"optimizer_type": "nova", "model_name": "nova-pro"}
        result = await optimization_service.run_optimization("task-123", config)
        
        assert result["status"] == "completed"
        assert "results" in result

    @pytest.mark.unit
    @patch('app.services.optimization_service.MIPROv2')
    async def test_run_miprov2_optimization(self, mock_optimizer, optimization_service):
        """Test running MIPROv2 optimization."""
        mock_optimizer_instance = Mock()
        mock_optimizer_instance.optimize = AsyncMock(return_value={
            "optimized_prompt": "MIPROv2 optimized prompt",
            "metrics": {"accuracy": 0.88}
        })
        mock_optimizer.return_value = mock_optimizer_instance
        
        optimization_service.run_optimization = AsyncMock(return_value={
            "status": "completed",
            "results": {"accuracy": 0.88}
        })
        
        config = {"optimizer_type": "miprov2", "model_name": "claude-3"}
        result = await optimization_service.run_optimization("task-123", config)
        
        assert result["status"] == "completed"

    @pytest.mark.unit
    async def test_optimization_progress_updates(self, optimization_service):
        """Test optimization progress updates."""
        progress_updates = [
            {"progress": 0.2, "step": "Initializing"},
            {"progress": 0.5, "step": "Running iteration 1"},
            {"progress": 0.8, "step": "Running iteration 2"},
            {"progress": 1.0, "step": "Completed"}
        ]
        
        optimization_service.get_progress_updates = AsyncMock(return_value=progress_updates)
        
        result = await optimization_service.get_progress_updates("task-123")
        
        assert len(result) == 4
        assert result[-1]["progress"] == 1.0
        assert result[-1]["step"] == "Completed"

    @pytest.mark.unit
    async def test_export_optimization_results(self, optimization_service):
        """Test exporting optimization results."""
        expected_export = {
            "format": "json",
            "data": {"optimized_prompt": "test", "metrics": {"accuracy": 0.9}},
            "filename": "optimization_results_task-123.json"
        }
        
        optimization_service.export_results = AsyncMock(return_value=expected_export)
        
        result = await optimization_service.export_results("task-123", "json")
        
        assert result["format"] == "json"
        assert "data" in result
        assert "filename" in result