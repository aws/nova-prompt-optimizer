# Nova Prompt Optimizer API Documentation

This documentation covers the REST API for the Nova Prompt Optimizer Frontend backend.

## Overview

The Nova Prompt Optimizer API provides programmatic access to all functionality available in the web interface, including dataset management, prompt optimization, custom metrics, and human annotation workflows.

## Base URL

```
http://localhost:8000/api/v1
```

## Authentication

Currently, the API uses session-based authentication. Future versions will support API keys and OAuth2.

## API Specification

The complete API specification is available in OpenAPI 3.0 format:

- **Interactive Documentation**: [http://localhost:8000/docs](http://localhost:8000/docs) (Swagger UI)
- **Alternative Documentation**: [http://localhost:8000/redoc](http://localhost:8000/redoc) (ReDoc)
- **OpenAPI JSON**: [http://localhost:8000/openapi.json](http://localhost:8000/openapi.json)

## Quick Start

### 1. Upload a Dataset

```bash
curl -X POST "http://localhost:8000/api/v1/datasets/upload" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@your_dataset.csv" \
  -F "input_columns=input" \
  -F "output_columns=output" \
  -F "split_ratio=0.8"
```

### 2. Create a Prompt

```bash
curl -X POST "http://localhost:8000/api/v1/prompts" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Classification Prompt",
    "system_prompt": "You are a helpful classifier.",
    "user_prompt": "Classify this text: {{input}}",
    "description": "Basic classification prompt"
  }'
```

### 3. Start Optimization

```bash
curl -X POST "http://localhost:8000/api/v1/optimize/start" \
  -H "Content-Type: application/json" \
  -d '{
    "dataset_id": "dataset-uuid",
    "prompt_id": "prompt-uuid",
    "optimizer_type": "nova_prompt_optimizer",
    "model_name": "nova-pro",
    "max_iterations": 10
  }'
```

### 4. Check Optimization Status

```bash
curl -X GET "http://localhost:8000/api/v1/optimize/{task_id}/status"
```

## API Endpoints

### Datasets

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/datasets/upload` | Upload and process a new dataset |
| GET | `/datasets` | List all datasets |
| GET | `/datasets/{id}` | Get dataset details |
| GET | `/datasets/{id}/preview` | Preview dataset contents |
| DELETE | `/datasets/{id}` | Delete a dataset |

### Prompts

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/prompts` | Create a new prompt |
| GET | `/prompts` | List all prompts |
| GET | `/prompts/{id}` | Get prompt details |
| PUT | `/prompts/{id}` | Update a prompt |
| DELETE | `/prompts/{id}` | Delete a prompt |
| POST | `/prompts/{id}/preview` | Preview prompt with sample data |

### Optimization

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/optimize/start` | Start a new optimization |
| GET | `/optimize/{task_id}/status` | Get optimization status |
| POST | `/optimize/{task_id}/cancel` | Cancel an optimization |
| GET | `/optimize/history` | List optimization history |
| GET | `/optimize/{task_id}/results` | Get optimization results |

### Custom Metrics

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/metrics` | Create a custom metric |
| GET | `/metrics` | List all metrics |
| GET | `/metrics/{id}` | Get metric details |
| PUT | `/metrics/{id}` | Update a metric |
| DELETE | `/metrics/{id}` | Delete a metric |
| POST | `/metrics/{id}/test` | Test a metric with sample data |

### Annotations

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/rubrics/generate` | Generate AI rubric from dataset |
| GET | `/rubrics` | List all rubrics |
| GET | `/rubrics/{id}` | Get rubric details |
| PUT | `/rubrics/{id}` | Update a rubric |
| POST | `/annotations` | Submit an annotation |
| GET | `/annotations/tasks/{annotator_id}` | Get annotation tasks |
| GET | `/annotations/agreement/{task_id}` | Get inter-annotator agreement |

### WebSocket

| Endpoint | Description |
|----------|-------------|
| `/ws/optimization/{task_id}` | Real-time optimization progress updates |

## Data Models

### Dataset

```json
{
  "id": "uuid",
  "name": "string",
  "description": "string",
  "file_type": "csv|json",
  "input_columns": ["string"],
  "output_columns": ["string"],
  "row_count": "integer",
  "split_ratio": "float",
  "created_at": "datetime",
  "status": "processing|ready|error"
}
```

### Prompt

```json
{
  "id": "uuid",
  "name": "string",
  "description": "string",
  "system_prompt": "string",
  "user_prompt": "string",
  "variables": ["string"],
  "created_at": "datetime",
  "updated_at": "datetime"
}
```

### Optimization Task

```json
{
  "id": "uuid",
  "dataset_id": "uuid",
  "prompt_id": "uuid",
  "optimizer_type": "string",
  "model_name": "string",
  "status": "pending|running|completed|failed|cancelled",
  "progress": "float",
  "current_step": "string",
  "max_iterations": "integer",
  "created_at": "datetime",
  "completed_at": "datetime"
}
```

### Optimization Results

```json
{
  "task_id": "uuid",
  "original_prompt": "Prompt",
  "optimized_prompt": "Prompt",
  "metrics": {
    "original": {"metric_name": "float"},
    "optimized": {"metric_name": "float"},
    "improvement": {"metric_name": "float"}
  },
  "individual_results": [
    {
      "input": "string",
      "ground_truth": "string",
      "original_prediction": "string",
      "optimized_prediction": "string",
      "original_score": "float",
      "optimized_score": "float"
    }
  ]
}
```

## Error Handling

The API uses standard HTTP status codes and returns detailed error information:

### Error Response Format

```json
{
  "error": {
    "code": "ERROR_CODE",
    "message": "Human-readable error message",
    "details": {
      "field": "Additional error details"
    }
  }
}
```

### Common Error Codes

| Code | Status | Description |
|------|--------|-------------|
| `VALIDATION_ERROR` | 400 | Request validation failed |
| `RESOURCE_NOT_FOUND` | 404 | Requested resource doesn't exist |
| `PROCESSING_ERROR` | 422 | Unable to process request |
| `RATE_LIMIT_EXCEEDED` | 429 | Too many requests |
| `INTERNAL_ERROR` | 500 | Server error |

## Rate Limiting

The API implements rate limiting to ensure fair usage:

- **General Endpoints**: 100 requests per minute
- **Upload Endpoints**: 10 requests per minute
- **Optimization Endpoints**: 5 concurrent optimizations per user

Rate limit headers are included in responses:

```
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 95
X-RateLimit-Reset: 1640995200
```

## Pagination

List endpoints support pagination using cursor-based pagination:

### Request Parameters

- `limit`: Number of items per page (default: 20, max: 100)
- `cursor`: Cursor for next page (from previous response)

### Response Format

```json
{
  "data": [...],
  "pagination": {
    "has_next": true,
    "next_cursor": "cursor_string",
    "total_count": 150
  }
}
```

## WebSocket API

### Connection

```javascript
const ws = new WebSocket('ws://localhost:8000/ws/optimization/task-uuid');
```

### Message Format

```json
{
  "type": "progress_update",
  "data": {
    "task_id": "uuid",
    "progress": 0.45,
    "current_step": "Evaluating generation 5",
    "estimated_completion": "2024-01-15T10:30:00Z"
  }
}
```

### Message Types

- `progress_update`: Optimization progress information
- `status_change`: Task status changed (completed, failed, etc.)
- `error`: Error occurred during optimization
- `log_message`: Detailed log information

## SDK and Client Libraries

### Python SDK

```python
from nova_optimizer_client import NovaOptimizerClient

client = NovaOptimizerClient(base_url="http://localhost:8000")

# Upload dataset
dataset = client.datasets.upload(
    file_path="data.csv",
    input_columns=["input"],
    output_columns=["output"]
)

# Create prompt
prompt = client.prompts.create(
    name="My Prompt",
    user_prompt="Classify: {{input}}"
)

# Start optimization
task = client.optimize.start(
    dataset_id=dataset.id,
    prompt_id=prompt.id,
    optimizer_type="nova_prompt_optimizer"
)

# Wait for completion
results = client.optimize.wait_for_completion(task.id)
```

### JavaScript/TypeScript SDK

```typescript
import { NovaOptimizerClient } from '@nova/optimizer-client';

const client = new NovaOptimizerClient({
  baseUrl: 'http://localhost:8000'
});

// Upload dataset
const dataset = await client.datasets.upload({
  file: fileBlob,
  inputColumns: ['input'],
  outputColumns: ['output']
});

// Create prompt
const prompt = await client.prompts.create({
  name: 'My Prompt',
  userPrompt: 'Classify: {{input}}'
});

// Start optimization
const task = await client.optimize.start({
  datasetId: dataset.id,
  promptId: prompt.id,
  optimizerType: 'nova_prompt_optimizer'
});

// Monitor progress
client.optimize.onProgress(task.id, (progress) => {
  console.log(`Progress: ${progress.progress * 100}%`);
});
```

## Examples

### Complete Workflow Example

```bash
#!/bin/bash

# 1. Upload dataset
DATASET_RESPONSE=$(curl -s -X POST "http://localhost:8000/api/v1/datasets/upload" \
  -F "file=@sample_data.csv" \
  -F "input_columns=question" \
  -F "output_columns=answer")

DATASET_ID=$(echo $DATASET_RESPONSE | jq -r '.id')

# 2. Create prompt
PROMPT_RESPONSE=$(curl -s -X POST "http://localhost:8000/api/v1/prompts" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "QA Prompt",
    "user_prompt": "Answer this question: {{question}}"
  }')

PROMPT_ID=$(echo $PROMPT_RESPONSE | jq -r '.id')

# 3. Start optimization
TASK_RESPONSE=$(curl -s -X POST "http://localhost:8000/api/v1/optimize/start" \
  -H "Content-Type: application/json" \
  -d "{
    \"dataset_id\": \"$DATASET_ID\",
    \"prompt_id\": \"$PROMPT_ID\",
    \"optimizer_type\": \"nova_prompt_optimizer\",
    \"model_name\": \"nova-pro\"
  }")

TASK_ID=$(echo $TASK_RESPONSE | jq -r '.id')

# 4. Monitor progress
while true; do
  STATUS_RESPONSE=$(curl -s "http://localhost:8000/api/v1/optimize/$TASK_ID/status")
  STATUS=$(echo $STATUS_RESPONSE | jq -r '.status')
  PROGRESS=$(echo $STATUS_RESPONSE | jq -r '.progress')
  
  echo "Status: $STATUS, Progress: $(echo "$PROGRESS * 100" | bc)%"
  
  if [ "$STATUS" = "completed" ] || [ "$STATUS" = "failed" ]; then
    break
  fi
  
  sleep 10
done

# 5. Get results
if [ "$STATUS" = "completed" ]; then
  curl -s "http://localhost:8000/api/v1/optimize/$TASK_ID/results" | jq '.'
fi
```

## Testing

### API Testing with curl

```bash
# Test dataset upload
curl -X POST "http://localhost:8000/api/v1/datasets/upload" \
  -F "file=@test_data.csv" \
  -F "input_columns=input" \
  -F "output_columns=output"

# Test prompt creation
curl -X POST "http://localhost:8000/api/v1/prompts" \
  -H "Content-Type: application/json" \
  -d '{"name": "Test", "user_prompt": "Test: {{input}}"}'
```

### API Testing with Python

```python
import requests

base_url = "http://localhost:8000/api/v1"

# Test dataset upload
with open("test_data.csv", "rb") as f:
    response = requests.post(
        f"{base_url}/datasets/upload",
        files={"file": f},
        data={
            "input_columns": "input",
            "output_columns": "output"
        }
    )
    print(response.json())
```

## Deployment

### Environment Variables

```bash
# API Configuration
API_HOST=0.0.0.0
API_PORT=8000
API_WORKERS=4

# Database
DATABASE_URL=postgresql://user:pass@localhost/nova_optimizer

# AWS Configuration
AWS_REGION=us-east-1
AWS_ACCESS_KEY_ID=your_key
AWS_SECRET_ACCESS_KEY=your_secret

# Redis (for background tasks)
REDIS_URL=redis://localhost:6379

# File Storage
UPLOAD_PATH=/app/uploads
MAX_FILE_SIZE=104857600  # 100MB
```

### Docker Deployment

```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Health Checks

```bash
# Basic health check
curl http://localhost:8000/health

# Detailed health check
curl http://localhost:8000/health/detailed
```

## Support

For API support and questions:

- **Documentation**: [Interactive API Docs](http://localhost:8000/docs)
- **Issues**: Report bugs and feature requests
- **Community**: Join the developer community
- **Support**: Contact technical support for enterprise users