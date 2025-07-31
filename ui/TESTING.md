# Testing Guide for Nova Prompt Optimizer Frontend

This document provides comprehensive information about the testing infrastructure and practices for the Nova Prompt Optimizer Frontend.

## Overview

The testing suite includes:
- **Backend Unit Tests**: Testing individual services and API endpoints
- **Backend Integration Tests**: Testing complete workflows and service interactions
- **Frontend Component Tests**: Testing React components in isolation
- **End-to-End Tests**: Testing complete user workflows across the entire application

## Test Structure

```
ui/
├── backend/
│   ├── tests/
│   │   ├── conftest.py              # Test configuration and fixtures
│   │   ├── test_services/           # Service layer tests
│   │   ├── test_api/                # API endpoint tests
│   │   └── test_integration/        # Integration tests
│   ├── pytest.ini                  # Pytest configuration
│   └── requirements-test.txt        # Testing dependencies
├── frontend/
│   ├── src/
│   │   ├── test/
│   │   │   ├── setup.ts             # Test setup and configuration
│   │   │   └── mocks/               # Mock API handlers
│   │   └── components/
│   │       └── **/__tests__/        # Component tests
│   ├── cypress/
│   │   ├── e2e/                     # End-to-end test specs
│   │   ├── fixtures/                # Test data
│   │   └── support/                 # Custom commands and utilities
│   ├── vitest.config.ts             # Vitest configuration
│   └── cypress.config.ts            # Cypress configuration
└── test-runner.sh                   # Unified test runner script
```

## Running Tests

### Quick Start

Run all tests:
```bash
./test-runner.sh
```

### Backend Tests Only

```bash
# Run all backend tests
./test-runner.sh --backend-only

# Run with coverage
./test-runner.sh --backend-only --coverage

# Run in parallel
./test-runner.sh --backend-only --parallel

# Run specific test file
cd backend && python -m pytest tests/test_services/test_dataset_service.py

# Run specific test
cd backend && python -m pytest tests/test_services/test_dataset_service.py::TestDatasetService::test_validate_csv_file_format
```

### Frontend Tests Only

```bash
# Run all frontend tests
./test-runner.sh --frontend-only

# Run with coverage
./test-runner.sh --frontend-only --coverage

# Run in watch mode
cd frontend && npm run test:watch

# Run specific test file
cd frontend && npm run test -- src/components/dataset/__tests__/DatasetUpload.test.tsx

# Run with UI
cd frontend && npm run test:ui
```

### End-to-End Tests Only

```bash
# Run E2E tests headlessly
./test-runner.sh --e2e-only

# Run E2E tests with Cypress UI
cd frontend && npm run test:e2e:open
```

## Backend Testing

### Test Categories

#### Unit Tests (`@pytest.mark.unit`)
- Test individual functions and methods
- Mock external dependencies
- Fast execution
- High coverage of business logic

#### Integration Tests (`@pytest.mark.integration`)
- Test service interactions
- Test complete workflows
- Use real database connections (test database)
- Test API endpoints with full request/response cycle

#### API Tests (`@pytest.mark.api`)
- Test HTTP endpoints
- Validate request/response formats
- Test error handling
- Test authentication and authorization

### Writing Backend Tests

#### Service Tests Example

```python
import pytest
from unittest.mock import Mock, AsyncMock

class TestDatasetService:
    @pytest.fixture
    def dataset_service(self):
        return Mock()

    @pytest.mark.unit
    async def test_process_dataset_csv(self, dataset_service, mock_dataset_file):
        # Arrange
        expected_result = {"id": "dataset-123", "rows": 100}
        dataset_service.process_dataset = AsyncMock(return_value=expected_result)
        
        # Act
        result = await dataset_service.process_dataset(
            file_path=mock_dataset_file,
            input_columns=["input"],
            output_columns=["output"]
        )
        
        # Assert
        assert result["rows"] == 100
        dataset_service.process_dataset.assert_called_once()
```

#### API Tests Example

```python
@pytest.mark.api
def test_upload_dataset_csv(client, mock_dataset_file):
    with open(mock_dataset_file, 'rb') as f:
        files = {"file": ("test.csv", f, "text/csv")}
        data = {"input_columns": ["input"], "output_columns": ["output"]}
        
        response = client.post("/datasets/upload", files=files, data=data)
        
        assert response.status_code == 200
        assert response.json()["name"] == "test.csv"
```

### Test Fixtures

Common fixtures are defined in `conftest.py`:

- `temp_dir`: Temporary directory for test files
- `mock_dataset_file`: Sample CSV dataset
- `mock_json_dataset_file`: Sample JSON dataset
- `mock_prompt`: Sample prompt configuration
- `mock_optimization_config`: Sample optimization configuration
- `mock_aws_credentials`: Mock AWS credentials
- `mock_bedrock_client`: Mock Bedrock client

## Frontend Testing

### Test Categories

#### Component Tests
- Test React component rendering
- Test user interactions
- Test component state changes
- Mock external dependencies

#### Hook Tests
- Test custom React hooks
- Test state management
- Test side effects

#### Integration Tests
- Test component interactions
- Test API integration
- Test routing

### Writing Frontend Tests

#### Component Test Example

```typescript
import { describe, it, expect, vi } from 'vitest'
import { render, screen, fireEvent } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { DatasetUpload } from '../DatasetUpload'

describe('DatasetUpload', () => {
  it('renders upload interface correctly', () => {
    render(<DatasetUpload onUploadComplete={vi.fn()} />)
    
    expect(screen.getByText('Upload Dataset')).toBeInTheDocument()
    expect(screen.getByText(/Drag & drop/)).toBeInTheDocument()
  })

  it('handles file selection', async () => {
    const user = userEvent.setup()
    const mockOnUpload = vi.fn()
    
    render(<DatasetUpload onUploadComplete={mockOnUpload} />)
    
    const file = new File(['data'], 'test.csv', { type: 'text/csv' })
    const input = screen.getByLabelText(/upload/i)
    
    await user.upload(input, file)
    
    expect(input.files[0]).toBe(file)
  })
})
```

### Mock Service Worker (MSW)

API calls are mocked using MSW for consistent testing:

```typescript
// src/test/mocks/handlers.ts
export const handlers = [
  http.post('/api/datasets/upload', () => {
    return HttpResponse.json({
      id: 'dataset-123',
      name: 'test_dataset.csv',
      status: 'processed'
    })
  })
]
```

## End-to-End Testing

### Cypress Tests

E2E tests simulate real user workflows:

```typescript
describe('Complete Optimization Workflow', () => {
  it('completes full optimization workflow', () => {
    // Upload dataset
    cy.uploadDataset('sample-dataset.csv', ['input'], ['output'])
    
    // Create prompt
    cy.createPrompt('Test Prompt', 'System prompt', 'User prompt')
    
    // Start optimization
    cy.startOptimization({
      datasetId: 'dataset-123',
      promptId: 'prompt-123',
      optimizerType: 'nova',
      modelName: 'nova-pro'
    })
    
    // Wait for completion and verify results
    cy.waitForOptimization('task-123')
    cy.get('[data-testid="optimization-results"]').should('be.visible')
  })
})
```

### Custom Cypress Commands

Custom commands are defined in `cypress/support/commands.ts`:

- `cy.uploadDataset()`: Upload and process a dataset
- `cy.createPrompt()`: Create a new prompt
- `cy.startOptimization()`: Start an optimization task
- `cy.waitForOptimization()`: Wait for optimization completion
- `cy.navigateToStep()`: Navigate between workflow steps

## Test Data and Fixtures

### Backend Fixtures

Located in `backend/tests/conftest.py`:
- Mock datasets (CSV and JSON)
- Mock prompts with variables
- Mock optimization configurations
- Mock AWS services

### Frontend Fixtures

Located in `frontend/cypress/fixtures/`:
- `sample-dataset.csv`: Test dataset file
- `dataset-response.json`: Mock API responses
- `optimization-results.json`: Mock optimization results

## Coverage Requirements

### Backend Coverage Targets
- **Lines**: 80% minimum
- **Functions**: 80% minimum
- **Branches**: 80% minimum
- **Statements**: 80% minimum

### Frontend Coverage Targets
- **Lines**: 80% minimum
- **Functions**: 80% minimum
- **Branches**: 80% minimum
- **Statements**: 80% minimum

### Generating Coverage Reports

```bash
# Backend coverage
cd backend && python -m pytest --cov=app --cov-report=html

# Frontend coverage
cd frontend && npm run test:coverage

# Both with unified script
./test-runner.sh --coverage
```

## Continuous Integration

### GitHub Actions Workflow

```yaml
name: Test Suite
on: [push, pull_request]

jobs:
  backend-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      - run: pip install -r ui/backend/requirements-test.txt
      - run: cd ui && ./test-runner.sh --backend-only --coverage

  frontend-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-node@v3
        with:
          node-version: '18'
      - run: cd ui/frontend && npm ci
      - run: cd ui && ./test-runner.sh --frontend-only --coverage

  e2e-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-node@v3
        with:
          node-version: '18'
      - run: cd ui/frontend && npm ci
      - run: cd ui && ./test-runner.sh --e2e-only
```

## Best Practices

### General Testing Principles

1. **Test Pyramid**: More unit tests, fewer integration tests, minimal E2E tests
2. **Fast Feedback**: Unit tests should run quickly
3. **Isolation**: Tests should not depend on each other
4. **Deterministic**: Tests should produce consistent results
5. **Maintainable**: Tests should be easy to read and update

### Backend Testing Best Practices

1. **Mock External Dependencies**: Use mocks for AWS services, databases, etc.
2. **Test Edge Cases**: Test error conditions and boundary values
3. **Use Fixtures**: Reuse common test data through fixtures
4. **Async Testing**: Properly test async functions with `pytest-asyncio`
5. **Database Testing**: Use separate test database or in-memory database

### Frontend Testing Best Practices

1. **Test User Behavior**: Focus on what users see and do
2. **Mock API Calls**: Use MSW for consistent API mocking
3. **Accessibility Testing**: Include accessibility checks in tests
4. **Component Isolation**: Test components in isolation with mocked dependencies
5. **User Events**: Use `@testing-library/user-event` for realistic interactions

### E2E Testing Best Practices

1. **Test Critical Paths**: Focus on the most important user workflows
2. **Data Independence**: Each test should set up its own data
3. **Wait Strategies**: Use proper waits for dynamic content
4. **Page Object Model**: Organize tests with reusable page objects
5. **Environment Consistency**: Use consistent test environments

## Debugging Tests

### Backend Test Debugging

```bash
# Run with verbose output
python -m pytest -v

# Run with pdb debugger
python -m pytest --pdb

# Run specific test with output
python -m pytest tests/test_services/test_dataset_service.py::test_name -s
```

### Frontend Test Debugging

```bash
# Run with debug output
npm run test -- --reporter=verbose

# Run in watch mode for development
npm run test:watch

# Open Vitest UI for interactive debugging
npm run test:ui
```

### Cypress Debugging

```bash
# Open Cypress Test Runner for interactive debugging
npm run test:e2e:open

# Run with video recording
npm run test:e2e -- --record
```

## Performance Testing

### Load Testing

For performance testing of the optimization workflows:

```python
# Example load test with pytest-benchmark
@pytest.mark.benchmark
def test_optimization_performance(benchmark):
    result = benchmark(run_optimization, large_dataset)
    assert result.status == "completed"
```

### Memory Testing

Monitor memory usage during large dataset processing:

```python
import psutil
import pytest

@pytest.mark.slow
def test_large_dataset_memory_usage():
    process = psutil.Process()
    initial_memory = process.memory_info().rss
    
    # Process large dataset
    result = process_large_dataset()
    
    final_memory = process.memory_info().rss
    memory_increase = final_memory - initial_memory
    
    # Assert memory usage is within acceptable limits
    assert memory_increase < 500 * 1024 * 1024  # 500MB limit
```

## Troubleshooting

### Common Issues

1. **Import Errors**: Ensure all dependencies are installed
2. **Async Test Failures**: Use proper async/await syntax
3. **Mock Issues**: Verify mock setup and assertions
4. **Timeout Issues**: Increase timeout values for slow operations
5. **Database Issues**: Ensure test database is properly configured

### Getting Help

1. Check test output for specific error messages
2. Review test logs and coverage reports
3. Use debugger to step through failing tests
4. Consult the testing framework documentation
5. Ask team members for assistance

## Contributing

When adding new features:

1. Write tests first (TDD approach)
2. Ensure all tests pass
3. Maintain or improve coverage
4. Update test documentation
5. Add integration tests for new workflows

When fixing bugs:

1. Write a failing test that reproduces the bug
2. Fix the bug
3. Ensure the test now passes
4. Add regression tests if needed