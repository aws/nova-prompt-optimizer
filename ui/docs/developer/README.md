# Developer Documentation

This documentation is for developers who want to contribute to, extend, or maintain the Nova Prompt Optimizer Frontend.

## Table of Contents

1. [Architecture Overview](#architecture-overview)
2. [Development Setup](#development-setup)
3. [Project Structure](#project-structure)
4. [Backend Development](#backend-development)
5. [Frontend Development](#frontend-development)
6. [Testing](#testing)
7. [Deployment](#deployment)
8. [Contributing](#contributing)

## Architecture Overview

The Nova Prompt Optimizer Frontend follows a clean architecture pattern with clear separation between layers:

```
┌─────────────────────────────────────────────────────────────┐
│                    Frontend (React)                         │
├─────────────────────────────────────────────────────────────┤
│                    API Layer (FastAPI)                      │
├─────────────────────────────────────────────────────────────┤
│                 Integration Layer                           │
├─────────────────────────────────────────────────────────────┤
│              Nova Prompt Optimizer SDK                      │
├─────────────────────────────────────────────────────────────┤
│                   AWS Bedrock                               │
└─────────────────────────────────────────────────────────────┘
```

### Key Principles

1. **No SDK Modifications**: The existing Nova Prompt Optimizer SDK remains unchanged
2. **Clean Separation**: Clear boundaries between frontend, API, and integration layers
3. **Adapter Pattern**: Consistent use of adapters for external integrations
4. **Type Safety**: Full TypeScript support with shared type definitions
5. **Real-time Updates**: WebSocket integration for live progress tracking

## Development Setup

### Prerequisites

- Python 3.11+
- Node.js 18+
- npm or yarn
- Docker (optional, for containerized development)
- AWS CLI configured with appropriate credentials

### Backend Setup

```bash
# Navigate to backend directory
cd ui/backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
pip install -r requirements-test.txt

# Set up environment variables
cp .env.example .env
# Edit .env with your configuration

# Initialize database
alembic upgrade head

# Start development server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Frontend Setup

```bash
# Navigate to frontend directory
cd ui/frontend

# Install dependencies
npm install

# Start development server
npm run dev

# The frontend will be available at http://localhost:5173
```

### Docker Development

```bash
# From the ui directory
docker-compose up -d

# This starts:
# - Backend API on http://localhost:8000
# - Frontend on http://localhost:5173
# - PostgreSQL database
# - Redis for background tasks
```

## Project Structure

### Backend Structure

```
ui/backend/
├── app/
│   ├── __init__.py
│   ├── main.py                 # FastAPI application entry point
│   ├── config.py               # Configuration management
│   ├── dependencies.py         # Dependency injection
│   ├── models/                 # Pydantic models
│   │   ├── dataset.py
│   │   ├── prompt.py
│   │   ├── optimization.py
│   │   └── ...
│   ├── routers/                # API route handlers
│   │   ├── datasets.py
│   │   ├── prompts.py
│   │   ├── optimization.py
│   │   └── ...
│   ├── services/               # Business logic layer
│   │   ├── dataset_service.py
│   │   ├── prompt_service.py
│   │   └── ...
│   ├── adapters/               # Integration with Nova SDK
│   │   ├── dataset_adapter.py
│   │   ├── prompt_adapter.py
│   │   └── ...
│   ├── core/                   # Core utilities
│   │   ├── exceptions.py
│   │   ├── logging.py
│   │   └── ...
│   └── db/                     # Database layer
│       ├── database.py
│       ├── models.py
│       └── migrations/
├── tests/                      # Test suite
├── requirements.txt            # Dependencies
└── Dockerfile                  # Container configuration
```

### Frontend Structure

```
ui/frontend/
├── src/
│   ├── components/             # React components
│   │   ├── common/             # Shared components
│   │   ├── dataset/            # Dataset management
│   │   ├── prompt/             # Prompt editing
│   │   ├── optimization/       # Optimization workflow
│   │   └── ...
│   ├── pages/                  # Page components
│   ├── hooks/                  # Custom React hooks
│   ├── services/               # API client services
│   ├── store/                  # State management
│   ├── types/                  # TypeScript definitions
│   ├── utils/                  # Utility functions
│   └── styles/                 # Styling
├── public/                     # Static assets
├── package.json                # Dependencies and scripts
├── tsconfig.json               # TypeScript configuration
├── tailwind.config.js          # Tailwind CSS configuration
└── vite.config.ts              # Vite build configuration
```

## Backend Development

### Adding New Endpoints

1. **Define Pydantic Models**

```python
# app/models/new_feature.py
from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class NewFeatureCreate(BaseModel):
    name: str
    description: Optional[str] = None

class NewFeatureResponse(BaseModel):
    id: str
    name: str
    description: Optional[str]
    created_at: datetime
    
    class Config:
        from_attributes = True
```

2. **Create Service Layer**

```python
# app/services/new_feature_service.py
from typing import List, Optional
from app.models.new_feature import NewFeatureCreate, NewFeatureResponse
from app.adapters.nova_adapter import NovaAdapter

class NewFeatureService:
    def __init__(self):
        self.nova_adapter = NovaAdapter()
    
    async def create_feature(self, feature_data: NewFeatureCreate) -> NewFeatureResponse:
        # Business logic here
        # Integration with Nova SDK through adapters
        pass
    
    async def get_features(self) -> List[NewFeatureResponse]:
        # Implementation
        pass
```

3. **Add Router**

```python
# app/routers/new_feature.py
from fastapi import APIRouter, Depends, HTTPException
from typing import List
from app.models.new_feature import NewFeatureCreate, NewFeatureResponse
from app.services.new_feature_service import NewFeatureService

router = APIRouter()

@router.post("/", response_model=NewFeatureResponse)
async def create_feature(
    feature_data: NewFeatureCreate,
    service: NewFeatureService = Depends()
):
    """Create a new feature."""
    try:
        return await service.create_feature(feature_data)
    except Exception as e:
        raise HTTPException(status_code=422, detail=str(e))

@router.get("/", response_model=List[NewFeatureResponse])
async def list_features(
    service: NewFeatureService = Depends()
):
    """List all features."""
    return await service.get_features()
```

4. **Register Router**

```python
# app/main.py
from app.routers import new_feature

app.include_router(
    new_feature.router,
    prefix="/api/v1/new-feature",
    tags=["New Feature"]
)
```

### Database Integration

The backend uses SQLAlchemy with Alembic for database migrations.

#### Adding New Models

```python
# app/db/models.py
from sqlalchemy import Column, String, DateTime, Text
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()

class NewFeature(Base):
    __tablename__ = "new_features"
    
    id = Column(String, primary_key=True)
    name = Column(String, nullable=False)
    description = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
```

#### Creating Migrations

```bash
# Generate migration
alembic revision --autogenerate -m "Add new feature table"

# Apply migration
alembic upgrade head
```

### Background Tasks

Long-running operations use Celery with Redis:

```python
# app/core/tasks.py
from celery import Celery
from app.services.optimization_service import OptimizationService

celery_app = Celery("nova_optimizer")

@celery_app.task
def run_optimization(task_id: str, config: dict):
    """Background task for optimization."""
    service = OptimizationService()
    return service.run_optimization_sync(task_id, config)
```

### WebSocket Integration

Real-time updates use FastAPI WebSocket support:

```python
# app/routers/websocket.py
from fastapi import WebSocket, WebSocketDisconnect
from typing import Dict, List

class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, List[WebSocket]] = {}
    
    async def connect(self, websocket: WebSocket, task_id: str):
        await websocket.accept()
        if task_id not in self.active_connections:
            self.active_connections[task_id] = []
        self.active_connections[task_id].append(websocket)
    
    async def broadcast_progress(self, task_id: str, data: dict):
        if task_id in self.active_connections:
            for connection in self.active_connections[task_id]:
                await connection.send_json(data)

manager = ConnectionManager()

@router.websocket("/optimization/{task_id}")
async def optimization_websocket(websocket: WebSocket, task_id: str):
    await manager.connect(websocket, task_id)
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(websocket, task_id)
```

## Frontend Development

### Component Development

The frontend uses React with TypeScript and Shadcn/UI components.

#### Creating New Components

```typescript
// src/components/new-feature/NewFeature.tsx
import React from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { useNewFeature } from '@/hooks/useNewFeature';

interface NewFeatureProps {
  featureId?: string;
  onFeatureChange?: (feature: NewFeature) => void;
}

export const NewFeature: React.FC<NewFeatureProps> = ({
  featureId,
  onFeatureChange
}) => {
  const { feature, loading, error, updateFeature } = useNewFeature(featureId);

  if (loading) return <div>Loading...</div>;
  if (error) return <div>Error: {error.message}</div>;

  return (
    <Card>
      <CardHeader>
        <CardTitle>{feature?.name}</CardTitle>
      </CardHeader>
      <CardContent>
        <p>{feature?.description}</p>
        <Button onClick={() => updateFeature(feature)}>
          Update Feature
        </Button>
      </CardContent>
    </Card>
  );
};
```

#### Custom Hooks

```typescript
// src/hooks/useNewFeature.ts
import { useState, useEffect } from 'react';
import { newFeatureApi } from '@/services/api/newFeature';
import { NewFeature } from '@/types/newFeature';

export const useNewFeature = (featureId?: string) => {
  const [feature, setFeature] = useState<NewFeature | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<Error | null>(null);

  useEffect(() => {
    if (featureId) {
      loadFeature(featureId);
    }
  }, [featureId]);

  const loadFeature = async (id: string) => {
    setLoading(true);
    try {
      const data = await newFeatureApi.getFeature(id);
      setFeature(data);
    } catch (err) {
      setError(err as Error);
    } finally {
      setLoading(false);
    }
  };

  const updateFeature = async (updatedFeature: NewFeature) => {
    try {
      const data = await newFeatureApi.updateFeature(updatedFeature);
      setFeature(data);
      return data;
    } catch (err) {
      setError(err as Error);
      throw err;
    }
  };

  return {
    feature,
    loading,
    error,
    updateFeature,
    reload: () => featureId && loadFeature(featureId)
  };
};
```

#### API Services

```typescript
// src/services/api/newFeature.ts
import { apiClient } from './client';
import { NewFeature, NewFeatureCreate } from '@/types/newFeature';

export const newFeatureApi = {
  async getFeatures(): Promise<NewFeature[]> {
    const response = await apiClient.get('/new-feature');
    return response.data;
  },

  async getFeature(id: string): Promise<NewFeature> {
    const response = await apiClient.get(`/new-feature/${id}`);
    return response.data;
  },

  async createFeature(data: NewFeatureCreate): Promise<NewFeature> {
    const response = await apiClient.post('/new-feature', data);
    return response.data;
  },

  async updateFeature(feature: NewFeature): Promise<NewFeature> {
    const response = await apiClient.put(`/new-feature/${feature.id}`, feature);
    return response.data;
  },

  async deleteFeature(id: string): Promise<void> {
    await apiClient.delete(`/new-feature/${id}`);
  }
};
```

### State Management

The frontend uses React Context for global state:

```typescript
// src/store/context/NewFeatureContext.tsx
import React, { createContext, useContext, useReducer } from 'react';
import { NewFeature } from '@/types/newFeature';

interface NewFeatureState {
  features: NewFeature[];
  selectedFeature: NewFeature | null;
  loading: boolean;
}

type NewFeatureAction =
  | { type: 'SET_FEATURES'; payload: NewFeature[] }
  | { type: 'SELECT_FEATURE'; payload: NewFeature }
  | { type: 'SET_LOADING'; payload: boolean };

const NewFeatureContext = createContext<{
  state: NewFeatureState;
  dispatch: React.Dispatch<NewFeatureAction>;
} | null>(null);

export const useNewFeatureContext = () => {
  const context = useContext(NewFeatureContext);
  if (!context) {
    throw new Error('useNewFeatureContext must be used within NewFeatureProvider');
  }
  return context;
};

export const NewFeatureProvider: React.FC<{ children: React.ReactNode }> = ({
  children
}) => {
  const [state, dispatch] = useReducer(newFeatureReducer, initialState);

  return (
    <NewFeatureContext.Provider value={{ state, dispatch }}>
      {children}
    </NewFeatureContext.Provider>
  );
};
```

### Styling with Shadcn/UI

The frontend uses Shadcn/UI components with Tailwind CSS:

```typescript
// Example component using Shadcn/UI
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Alert, AlertDescription } from '@/components/ui/alert';

export const ExampleComponent = () => {
  return (
    <Card className="w-full max-w-md">
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          Feature Status
          <Badge variant="secondary">Active</Badge>
        </CardTitle>
      </CardHeader>
      <CardContent className="space-y-4">
        <Alert>
          <AlertDescription>
            This feature is currently in beta.
          </AlertDescription>
        </Alert>
        
        <div className="space-y-2">
          <Input placeholder="Enter feature name" />
          <Button className="w-full">Save Feature</Button>
        </div>
      </CardContent>
    </Card>
  );
};
```

## Testing

### Backend Testing

The backend uses pytest with comprehensive test coverage:

```python
# tests/test_services/test_new_feature_service.py
import pytest
from unittest.mock import Mock, patch
from app.services.new_feature_service import NewFeatureService
from app.models.new_feature import NewFeatureCreate

@pytest.fixture
def service():
    return NewFeatureService()

@pytest.fixture
def sample_feature_data():
    return NewFeatureCreate(
        name="Test Feature",
        description="A test feature"
    )

@pytest.mark.asyncio
async def test_create_feature(service, sample_feature_data):
    """Test feature creation."""
    with patch.object(service.nova_adapter, 'create_feature') as mock_create:
        mock_create.return_value = Mock(id="test-id")
        
        result = await service.create_feature(sample_feature_data)
        
        assert result.name == sample_feature_data.name
        assert result.description == sample_feature_data.description
        mock_create.assert_called_once()

@pytest.mark.asyncio
async def test_create_feature_error(service, sample_feature_data):
    """Test feature creation error handling."""
    with patch.object(service.nova_adapter, 'create_feature') as mock_create:
        mock_create.side_effect = Exception("Creation failed")
        
        with pytest.raises(Exception, match="Creation failed"):
            await service.create_feature(sample_feature_data)
```

### Frontend Testing

The frontend uses Vitest and React Testing Library:

```typescript
// src/components/new-feature/__tests__/NewFeature.test.tsx
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { vi } from 'vitest';
import { NewFeature } from '../NewFeature';
import { newFeatureApi } from '@/services/api/newFeature';

// Mock the API
vi.mock('@/services/api/newFeature');

const mockFeature = {
  id: '1',
  name: 'Test Feature',
  description: 'Test description',
  created_at: new Date().toISOString()
};

describe('NewFeature', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('renders feature information', async () => {
    vi.mocked(newFeatureApi.getFeature).mockResolvedValue(mockFeature);

    render(<NewFeature featureId="1" />);

    await waitFor(() => {
      expect(screen.getByText('Test Feature')).toBeInTheDocument();
      expect(screen.getByText('Test description')).toBeInTheDocument();
    });
  });

  it('handles update feature', async () => {
    vi.mocked(newFeatureApi.getFeature).mockResolvedValue(mockFeature);
    vi.mocked(newFeatureApi.updateFeature).mockResolvedValue(mockFeature);

    const onFeatureChange = vi.fn();
    render(<NewFeature featureId="1" onFeatureChange={onFeatureChange} />);

    await waitFor(() => {
      expect(screen.getByText('Test Feature')).toBeInTheDocument();
    });

    const updateButton = screen.getByText('Update Feature');
    fireEvent.click(updateButton);

    await waitFor(() => {
      expect(newFeatureApi.updateFeature).toHaveBeenCalledWith(mockFeature);
      expect(onFeatureChange).toHaveBeenCalledWith(mockFeature);
    });
  });

  it('displays loading state', () => {
    vi.mocked(newFeatureApi.getFeature).mockImplementation(
      () => new Promise(() => {}) // Never resolves
    );

    render(<NewFeature featureId="1" />);

    expect(screen.getByText('Loading...')).toBeInTheDocument();
  });

  it('displays error state', async () => {
    const error = new Error('Failed to load feature');
    vi.mocked(newFeatureApi.getFeature).mockRejectedValue(error);

    render(<NewFeature featureId="1" />);

    await waitFor(() => {
      expect(screen.getByText('Error: Failed to load feature')).toBeInTheDocument();
    });
  });
});
```

### Running Tests

```bash
# Backend tests
cd ui/backend
pytest tests/ -v --cov=app

# Frontend tests
cd ui/frontend
npm run test

# E2E tests
npm run test:e2e
```

## Deployment

### Environment Configuration

```bash
# Production environment variables
NODE_ENV=production
API_URL=https://api.nova-optimizer.example.com
DATABASE_URL=postgresql://user:pass@db:5432/nova_optimizer
REDIS_URL=redis://redis:6379
AWS_REGION=us-east-1
```

### Docker Deployment

```yaml
# docker-compose.prod.yml
version: '3.8'

services:
  backend:
    build:
      context: ./backend
      dockerfile: Dockerfile.prod
    environment:
      - DATABASE_URL=postgresql://user:pass@db:5432/nova_optimizer
      - REDIS_URL=redis://redis:6379
    depends_on:
      - db
      - redis

  frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile.prod
    environment:
      - VITE_API_URL=https://api.nova-optimizer.example.com

  db:
    image: postgres:15
    environment:
      - POSTGRES_DB=nova_optimizer
      - POSTGRES_USER=user
      - POSTGRES_PASSWORD=pass

  redis:
    image: redis:7-alpine
```

### CI/CD Pipeline

```yaml
# .github/workflows/deploy.yml
name: Deploy

on:
  push:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Test Backend
        run: |
          cd ui/backend
          pip install -r requirements.txt
          pytest tests/
      
      - name: Test Frontend
        run: |
          cd ui/frontend
          npm install
          npm run test

  deploy:
    needs: test
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Deploy to Production
        run: |
          docker-compose -f docker-compose.prod.yml up -d
```

## Contributing

### Code Style

#### Backend (Python)
- Follow PEP 8 style guidelines
- Use Black for code formatting
- Use isort for import sorting
- Type hints required for all functions

```bash
# Format code
black app/ tests/
isort app/ tests/

# Lint code
flake8 app/ tests/
mypy app/
```

#### Frontend (TypeScript)
- Use Prettier for code formatting
- Follow ESLint rules
- Use TypeScript strict mode
- Prefer functional components with hooks

```bash
# Format code
npm run format

# Lint code
npm run lint

# Type check
npm run type-check
```

### Git Workflow

1. **Create Feature Branch**
   ```bash
   git checkout -b feature/new-feature-name
   ```

2. **Make Changes**
   - Write tests first (TDD approach)
   - Implement feature
   - Update documentation

3. **Commit Changes**
   ```bash
   git add .
   git commit -m "feat: add new feature description"
   ```

4. **Push and Create PR**
   ```bash
   git push origin feature/new-feature-name
   ```

### Pull Request Guidelines

- **Title**: Use conventional commit format
- **Description**: Explain what and why
- **Tests**: Include test coverage
- **Documentation**: Update relevant docs
- **Screenshots**: For UI changes

### Code Review Checklist

- [ ] Code follows style guidelines
- [ ] Tests are included and passing
- [ ] Documentation is updated
- [ ] No breaking changes (or properly documented)
- [ ] Performance impact considered
- [ ] Security implications reviewed

## Troubleshooting Development Issues

### Common Backend Issues

#### Import Errors
```bash
# Ensure PYTHONPATH includes app directory
export PYTHONPATH="${PYTHONPATH}:$(pwd)/app"
```

#### Database Connection Issues
```bash
# Check database is running
docker ps | grep postgres

# Reset database
alembic downgrade base
alembic upgrade head
```

### Common Frontend Issues

#### Module Resolution
```bash
# Clear node modules and reinstall
rm -rf node_modules package-lock.json
npm install
```

#### Build Issues
```bash
# Clear Vite cache
rm -rf node_modules/.vite
npm run dev
```

### Performance Debugging

#### Backend Profiling
```python
# Add to endpoints for profiling
import cProfile
import pstats

def profile_endpoint():
    profiler = cProfile.Profile()
    profiler.enable()
    
    # Your endpoint logic here
    
    profiler.disable()
    stats = pstats.Stats(profiler)
    stats.sort_stats('cumulative')
    stats.print_stats()
```

#### Frontend Performance
```typescript
// Use React DevTools Profiler
import { Profiler } from 'react';

function onRenderCallback(id, phase, actualDuration) {
  console.log('Component:', id, 'Phase:', phase, 'Duration:', actualDuration);
}

<Profiler id="MyComponent" onRender={onRenderCallback}>
  <MyComponent />
</Profiler>
```

For more detailed information, refer to the specific documentation sections or contact the development team.