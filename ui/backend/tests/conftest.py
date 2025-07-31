"""
Test configuration and fixtures for the backend tests.
"""
import asyncio
import os
import tempfile
from typing import AsyncGenerator, Generator
from unittest.mock import Mock

import pytest
import pytest_asyncio
from fastapi.testclient import TestClient
from httpx import AsyncClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Import your app components here (these would be created in the actual implementation)
# from app.main import app
# from app.db.database import get_db, Base
# from app.core.config import settings


@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
def temp_dir() -> Generator[str, None, None]:
    """Create a temporary directory for test files."""
    with tempfile.TemporaryDirectory() as temp_dir:
        yield temp_dir


@pytest.fixture
def mock_dataset_file(temp_dir: str) -> str:
    """Create a mock CSV dataset file for testing."""
    csv_content = """input,output,category
"What is the capital of France?","Paris","geography"
"What is 2+2?","4","math"
"Who wrote Romeo and Juliet?","Shakespeare","literature"
"""
    file_path = os.path.join(temp_dir, "test_dataset.csv")
    with open(file_path, "w") as f:
        f.write(csv_content)
    return file_path


@pytest.fixture
def mock_json_dataset_file(temp_dir: str) -> str:
    """Create a mock JSON dataset file for testing."""
    json_content = """[
    {"input": "What is the capital of France?", "output": "Paris", "category": "geography"},
    {"input": "What is 2+2?", "output": "4", "category": "math"},
    {"input": "Who wrote Romeo and Juliet?", "output": "Shakespeare", "category": "literature"}
]"""
    file_path = os.path.join(temp_dir, "test_dataset.json")
    with open(file_path, "w") as f:
        f.write(json_content)
    return file_path


@pytest.fixture
def mock_prompt():
    """Create a mock prompt for testing."""
    return {
        "id": "test-prompt-1",
        "name": "Test Prompt",
        "system_prompt": "You are a helpful assistant.",
        "user_prompt": "Answer the following question: {{input}}",
        "variables": ["input"],
        "created_at": "2024-01-01T00:00:00Z"
    }


@pytest.fixture
def mock_optimization_config():
    """Create a mock optimization configuration for testing."""
    return {
        "dataset_id": "test-dataset-1",
        "prompt_id": "test-prompt-1",
        "optimizer_type": "nova",
        "model_name": "nova-pro",
        "max_iterations": 5,
        "evaluation_metrics": ["accuracy"],
        "parameters": {
            "temperature": 0.7,
            "max_tokens": 1000
        }
    }


@pytest.fixture
def mock_optimization_results():
    """Create mock optimization results for testing."""
    return {
        "task_id": "test-task-1",
        "status": "completed",
        "original_prompt": {
            "system_prompt": "You are a helpful assistant.",
            "user_prompt": "Answer: {{input}}"
        },
        "optimized_prompt": {
            "system_prompt": "You are an expert assistant with deep knowledge.",
            "user_prompt": "Please provide a comprehensive answer to: {{input}}"
        },
        "metrics": {
            "original_accuracy": 0.75,
            "optimized_accuracy": 0.92,
            "improvement": 0.17
        },
        "individual_results": [
            {
                "input": "What is the capital of France?",
                "expected": "Paris",
                "original_output": "Paris",
                "optimized_output": "Paris",
                "original_score": 1.0,
                "optimized_score": 1.0
            }
        ]
    }


@pytest.fixture
def mock_aws_credentials():
    """Mock AWS credentials for testing."""
    os.environ["AWS_ACCESS_KEY_ID"] = "test-access-key"
    os.environ["AWS_SECRET_ACCESS_KEY"] = "test-secret-key"
    os.environ["AWS_DEFAULT_REGION"] = "us-east-1"
    yield
    # Cleanup
    for key in ["AWS_ACCESS_KEY_ID", "AWS_SECRET_ACCESS_KEY", "AWS_DEFAULT_REGION"]:
        if key in os.environ:
            del os.environ[key]


@pytest.fixture
def mock_bedrock_client():
    """Create a mock Bedrock client for testing."""
    mock_client = Mock()
    mock_client.converse.return_value = {
        "output": {
            "message": {
                "content": [
                    {
                        "text": "This is a mock response from Bedrock."
                    }
                ]
            }
        },
        "usage": {
            "inputTokens": 10,
            "outputTokens": 8
        }
    }
    return mock_client


# Database fixtures would go here when the actual database models are implemented
# @pytest.fixture
# def test_db():
#     """Create a test database."""
#     engine = create_engine("sqlite:///./test.db", connect_args={"check_same_thread": False})
#     TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
#     Base.metadata.create_all(bind=engine)
#     
#     def override_get_db():
#         try:
#             db = TestingSessionLocal()
#             yield db
#         finally:
#             db.close()
#     
#     app.dependency_overrides[get_db] = override_get_db
#     yield
#     Base.metadata.drop_all(bind=engine)


# @pytest.fixture
# def client(test_db):
#     """Create a test client."""
#     return TestClient(app)


# @pytest_asyncio.fixture
# async def async_client(test_db) -> AsyncGenerator[AsyncClient, None]:
#     """Create an async test client."""
#     async with AsyncClient(app=app, base_url="http://test") as ac:
#         yield ac