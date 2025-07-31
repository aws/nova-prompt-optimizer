"""
Integration tests for complete optimization workflows.
"""
import pytest
from unittest.mock import Mock, AsyncMock, patch
import asyncio

# These imports would be from the actual implementation
# from app.services.dataset_service import DatasetService
# from app.services.prompt_service import PromptService
# from app.services.optimization_service import OptimizationService


class TestOptimizationWorkflow:
    """Integration tests for the complete optimization workflow."""

    @pytest.fixture
    def workflow_services(self):
        """Create mock services for workflow testing."""
        return {
            "dataset_service": Mock(),
            "prompt_service": Mock(),
            "optimization_service": Mock()
        }

    @pytest.mark.integration
    async def test_complete_optimization_workflow(
        self, 
        workflow_services, 
        mock_dataset_file, 
        mock_prompt,
        mock_optimization_config
    ):
        """Test the complete optimization workflow from dataset upload to results."""
        dataset_service = workflow_services["dataset_service"]
        prompt_service = workflow_services["prompt_service"]
        optimization_service = workflow_services["optimization_service"]
        
        # Step 1: Upload and process dataset
        dataset_result = {
            "id": "dataset-123",
            "name": "test_dataset.csv",
            "rows": 100,
            "columns": ["input", "output", "category"]
        }
        dataset_service.process_dataset = AsyncMock(return_value=dataset_result)
        
        dataset = await dataset_service.process_dataset(
            file_path=mock_dataset_file,
            input_columns=["input"],
            output_columns=["output"],
            split_ratio=0.8
        )
        
        assert dataset["id"] == "dataset-123"
        assert dataset["rows"] == 100
        
        # Step 2: Create and validate prompt
        prompt_service.create_prompt = AsyncMock(return_value=mock_prompt)
        prompt_service.validate_template = Mock(return_value=True)
        
        prompt = await prompt_service.create_prompt({
            "name": "Test Prompt",
            "system_prompt": "You are a helpful assistant.",
            "user_prompt": "Answer: {{input}}"
        })
        
        assert prompt["id"] == "test-prompt-1"
        assert "input" in prompt["variables"]
        
        # Step 3: Start optimization
        optimization_task = {
            "id": "task-123",
            "status": "queued",
            "progress": 0.0,
            "config": mock_optimization_config
        }
        optimization_service.start_optimization = AsyncMock(return_value=optimization_task)
        
        config = {
            "dataset_id": dataset["id"],
            "prompt_id": prompt["id"],
            "optimizer_type": "nova",
            "model_name": "nova-pro",
            "max_iterations": 5
        }
        
        task = await optimization_service.start_optimization(config)
        assert task["id"] == "task-123"
        assert task["status"] == "queued"
        
        # Step 4: Monitor progress
        progress_updates = [
            {"status": "running", "progress": 0.2, "step": "Initializing"},
            {"status": "running", "progress": 0.6, "step": "Iteration 2/5"},
            {"status": "completed", "progress": 1.0, "step": "Optimization complete"}
        ]
        
        optimization_service.get_status = AsyncMock(side_effect=progress_updates)
        
        # Simulate monitoring progress
        for expected_update in progress_updates:
            status = await optimization_service.get_status(task["id"])
            assert status["progress"] == expected_update["progress"]
            assert status["status"] == expected_update["status"]
        
        # Step 5: Get final results
        final_results = {
            "task_id": "task-123",
            "status": "completed",
            "original_prompt": {
                "system_prompt": "You are a helpful assistant.",
                "user_prompt": "Answer: {{input}}"
            },
            "optimized_prompt": {
                "system_prompt": "You are an expert assistant with comprehensive knowledge.",
                "user_prompt": "Provide a detailed and accurate answer to: {{input}}"
            },
            "metrics": {
                "original_accuracy": 0.75,
                "optimized_accuracy": 0.92,
                "improvement": 0.17
            }
        }
        
        optimization_service.get_results = AsyncMock(return_value=final_results)
        
        results = await optimization_service.get_results(task["id"])
        
        assert results["status"] == "completed"
        assert results["metrics"]["optimized_accuracy"] > results["metrics"]["original_accuracy"]
        assert results["metrics"]["improvement"] > 0

    @pytest.mark.integration
    async def test_workflow_with_custom_metrics(self, workflow_services):
        """Test optimization workflow with custom evaluation metrics."""
        optimization_service = workflow_services["optimization_service"]
        
        # Mock custom metric creation
        custom_metric = {
            "id": "metric-123",
            "name": "Custom Accuracy",
            "code": "def apply(self, prediction, ground_truth): return prediction == ground_truth"
        }
        
        optimization_service.create_custom_metric = AsyncMock(return_value=custom_metric)
        
        metric = await optimization_service.create_custom_metric({
            "name": "Custom Accuracy",
            "code": "def apply(self, prediction, ground_truth): return prediction == ground_truth"
        })
        
        assert metric["id"] == "metric-123"
        assert metric["name"] == "Custom Accuracy"
        
        # Use custom metric in optimization
        config = {
            "dataset_id": "dataset-123",
            "prompt_id": "prompt-123",
            "optimizer_type": "nova",
            "custom_metrics": [metric["id"]]
        }
        
        optimization_service.start_optimization = AsyncMock(return_value={
            "id": "task-456",
            "status": "queued",
            "config": config
        })
        
        task = await optimization_service.start_optimization(config)
        assert "custom_metrics" in task["config"]

    @pytest.mark.integration
    async def test_workflow_error_handling(self, workflow_services, mock_dataset_file):
        """Test error handling throughout the optimization workflow."""
        dataset_service = workflow_services["dataset_service"]
        optimization_service = workflow_services["optimization_service"]
        
        # Test dataset processing error
        dataset_service.process_dataset = AsyncMock(
            side_effect=Exception("Invalid dataset format")
        )
        
        with pytest.raises(Exception, match="Invalid dataset format"):
            await dataset_service.process_dataset(
                file_path=mock_dataset_file,
                input_columns=["invalid"],
                output_columns=["output"]
            )
        
        # Test optimization failure
        optimization_service.start_optimization = AsyncMock(
            side_effect=Exception("Model not available")
        )
        
        config = {
            "dataset_id": "dataset-123",
            "prompt_id": "prompt-123",
            "optimizer_type": "invalid_optimizer"
        }
        
        with pytest.raises(Exception, match="Model not available"):
            await optimization_service.start_optimization(config)

    @pytest.mark.integration
    async def test_concurrent_optimizations(self, workflow_services):
        """Test running multiple optimizations concurrently."""
        optimization_service = workflow_services["optimization_service"]
        
        # Mock multiple optimization tasks
        tasks = []
        for i in range(3):
            task = {
                "id": f"task-{i}",
                "status": "queued",
                "progress": 0.0,
                "config": {"optimizer_type": "nova"}
            }
            tasks.append(task)
        
        optimization_service.start_optimization = AsyncMock(side_effect=tasks)
        
        # Start multiple optimizations
        configs = [
            {"dataset_id": "dataset-1", "prompt_id": "prompt-1"},
            {"dataset_id": "dataset-2", "prompt_id": "prompt-2"},
            {"dataset_id": "dataset-3", "prompt_id": "prompt-3"}
        ]
        
        started_tasks = []
        for config in configs:
            task = await optimization_service.start_optimization(config)
            started_tasks.append(task)
        
        assert len(started_tasks) == 3
        assert all(task["status"] == "queued" for task in started_tasks)
        
        # Mock concurrent execution
        optimization_service.get_status = AsyncMock(return_value={
            "status": "running",
            "progress": 0.5
        })
        
        # Check all tasks are running
        statuses = []
        for task in started_tasks:
            status = await optimization_service.get_status(task["id"])
            statuses.append(status)
        
        assert all(status["status"] == "running" for status in statuses)

    @pytest.mark.integration
    @pytest.mark.slow
    async def test_long_running_optimization(self, workflow_services):
        """Test handling of long-running optimization tasks."""
        optimization_service = workflow_services["optimization_service"]
        
        # Mock a long-running task
        task = {
            "id": "long-task-123",
            "status": "queued",
            "progress": 0.0,
            "estimated_duration": 3600  # 1 hour
        }
        
        optimization_service.start_optimization = AsyncMock(return_value=task)
        
        config = {
            "dataset_id": "large-dataset",
            "prompt_id": "complex-prompt",
            "optimizer_type": "miprov2",
            "max_iterations": 50
        }
        
        started_task = await optimization_service.start_optimization(config)
        assert started_task["estimated_duration"] == 3600
        
        # Mock progress updates over time
        progress_sequence = [
            {"progress": 0.1, "status": "running", "step": "Initialization"},
            {"progress": 0.3, "status": "running", "step": "Iteration 15/50"},
            {"progress": 0.7, "status": "running", "step": "Iteration 35/50"},
            {"progress": 1.0, "status": "completed", "step": "Optimization complete"}
        ]
        
        optimization_service.get_status = AsyncMock(side_effect=progress_sequence)
        
        # Simulate checking progress over time
        for expected_progress in progress_sequence:
            status = await optimization_service.get_status(started_task["id"])
            assert status["progress"] == expected_progress["progress"]
            assert status["status"] == expected_progress["status"]
            
            # Simulate time delay
            await asyncio.sleep(0.1)

    @pytest.mark.integration
    async def test_workflow_with_annotation(self, workflow_services):
        """Test optimization workflow including human annotation."""
        optimization_service = workflow_services["optimization_service"]
        
        # Complete optimization first
        optimization_results = {
            "task_id": "task-123",
            "status": "completed",
            "optimized_prompt": "Optimized prompt text",
            "test_results": [
                {"input": "test1", "output": "result1", "score": 0.9},
                {"input": "test2", "output": "result2", "score": 0.8}
            ]
        }
        
        optimization_service.get_results = AsyncMock(return_value=optimization_results)
        
        results = await optimization_service.get_results("task-123")
        assert results["status"] == "completed"
        
        # Create annotation task
        annotation_task = {
            "id": "annotation-123",
            "optimization_task_id": "task-123",
            "status": "pending",
            "results_to_annotate": results["test_results"]
        }
        
        optimization_service.create_annotation_task = AsyncMock(return_value=annotation_task)
        
        annotation = await optimization_service.create_annotation_task("task-123")
        assert annotation["optimization_task_id"] == "task-123"
        assert len(annotation["results_to_annotate"]) == 2