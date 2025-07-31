# Nova Prompt Optimizer Frontend

A modern web interface for the Nova Prompt Optimizer, providing an intuitive way to optimize prompts for Amazon Nova models using AWS Bedrock.

## Features

- **Dataset Management**: Upload and manage CSV/JSON datasets with automatic processing
- **Prompt Engineering**: Create and edit prompts with Jinja2 templating and variable detection
- **Custom Metrics**: Define domain-specific evaluation metrics with Python code
- **Optimization Workflows**: Run automated prompt optimization with multiple algorithms
- **AI Rubric Generation**: Generate evaluation rubrics from datasets using AI
- **Human Annotation**: Quality assurance through human annotation workflows
- **Real-time Progress**: Live updates during optimization with WebSocket integration
- **Results Analysis**: Comprehensive visualization and comparison of optimization results

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Frontend (React + TypeScript)           │
│                    - Shadcn/UI Components                  │
│                    - Tailwind CSS Styling                  │
│                    - Real-time WebSocket Updates           │
├─────────────────────────────────────────────────────────────┤
│                    API Layer (FastAPI)                     │
│                    - RESTful Endpoints                     │
│                    - Background Task Management            │
│                    - WebSocket Support                     │
├─────────────────────────────────────────────────────────────┤
│                 Integration Layer                          │
│                 - Adapter Pattern                          │
│                 - No SDK Modifications                     │
├─────────────────────────────────────────────────────────────┤
│              Nova Prompt Optimizer SDK                     │
│              - Dataset Adapters                            │
│              - Optimization Algorithms                     │
│              - Evaluation Framework                        │
├─────────────────────────────────────────────────────────────┤
│                   AWS Bedrock                              │
│                   - Nova Models                            │
│                   - Model Inference                        │
└─────────────────────────────────────────────────────────────┘
```

## Quick Start

### Prerequisites

- Docker and Docker Compose
- AWS CLI configured with appropriate credentials
- At least 4GB RAM and 10GB disk space

### 1. Clone and Setup

```bash
git clone <repository-url>
cd nova-prompt-optimizer/ui
cp .env.example .env
```

### 2. Configure Environment

Edit `.env` file with your settings:

```bash
# Required: Database passwords
POSTGRES_PASSWORD=your_secure_password
REDIS_PASSWORD=your_redis_password
SECRET_KEY=your_very_secure_secret_key_minimum_32_characters

# Required: AWS credentials
AWS_REGION=us-east-1
AWS_ACCESS_KEY_ID=your_aws_access_key
AWS_SECRET_ACCESS_KEY=your_aws_secret_key

# Optional: Frontend URLs (for production)
VITE_API_URL=https://your-domain.com
VITE_WS_URL=wss://your-domain.com
```

### 3. Deploy

```bash
# Development deployment
docker-compose up -d

# Production deployment
./scripts/deploy.sh deploy
```

### 4. Access Application

- **Frontend**: http://localhost (production) or http://localhost:5173 (development)
- **API Documentation**: http://localhost:8000/docs
- **API Health**: http://localhost:8000/health

## Development Setup

### Backend Development

```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
pip install -r requirements-test.txt

# Set up environment
cp .env.example .env
# Edit .env with your configuration

# Run database migrations
alembic upgrade head

# Start development server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Frontend Development

```bash
cd frontend

# Install dependencies
npm install

# Start development server
npm run dev

# The frontend will be available at http://localhost:5173
```

### Running Tests

```bash
# Backend tests
cd backend
pytest tests/ -v --cov=app

# Frontend tests
cd frontend
npm run test

# E2E tests
npm run test:e2e
```

## Production Deployment

### Using Docker Compose (Recommended)

```bash
# Deploy with monitoring
docker-compose -f docker-compose.prod.yml --profile monitoring up -d

# Deploy without monitoring
docker-compose -f docker-compose.prod.yml up -d
```

### Using Deployment Script

```bash
# Full deployment with backup
./scripts/deploy.sh deploy

# Deploy without backup (faster)
./scripts/deploy.sh deploy --skip-backup

# Check status
./scripts/deploy.sh status

# View logs
./scripts/deploy.sh logs

# Create backup
./scripts/deploy.sh backup
```

### Environment Configuration

#### Required Environment Variables

```bash
# Database
POSTGRES_PASSWORD=secure_password_here
DATABASE_URL=postgresql://user:password@host:5432/database

# Redis
REDIS_PASSWORD=redis_password_here
REDIS_URL=redis://:password@host:6379/0

# Application
SECRET_KEY=minimum_32_character_secret_key
AWS_REGION=us-east-1
AWS_ACCESS_KEY_ID=your_access_key
AWS_SECRET_ACCESS_KEY=your_secret_key
```

#### Optional Configuration

```bash
# Performance
API_WORKERS=4
CELERY_WORKER_CONCURRENCY=2
DB_POOL_SIZE=20

# Security
CORS_ORIGINS=https://yourdomain.com,https://api.yourdomain.com
ALLOWED_HOSTS=yourdomain.com,api.yourdomain.com

# Monitoring
ENABLE_METRICS=true
SENTRY_DSN=your_sentry_dsn

# Features
ENABLE_CUSTOM_METRICS=true
ENABLE_HUMAN_ANNOTATION=true
RATE_LIMIT_ENABLED=true
```

## Monitoring and Observability

### Health Checks

- **Basic Health**: `GET /health`
- **Detailed Health**: `GET /health/detailed`
- **Readiness Probe**: `GET /readiness`
- **Liveness Probe**: `GET /liveness`

### Metrics

- **Prometheus Metrics**: `GET /api/v1/metrics/prometheus`
- **Application Metrics**: `GET /api/v1/metrics`
- **System Status**: `GET /api/v1/status`

### Monitoring Stack

When deployed with `--profile monitoring`:

- **Prometheus**: http://localhost:9090
- **Grafana**: http://localhost:3000 (admin/admin)

### Logging

Logs are available via Docker Compose:

```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f backend

# With deployment script
./scripts/deploy.sh logs backend
```

## API Documentation

### Interactive Documentation

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **OpenAPI Spec**: http://localhost:8000/openapi.json

### Key Endpoints

#### Datasets
- `POST /api/v1/datasets/upload` - Upload dataset
- `GET /api/v1/datasets` - List datasets
- `GET /api/v1/datasets/{id}` - Get dataset details

#### Prompts
- `POST /api/v1/prompts` - Create prompt
- `GET /api/v1/prompts` - List prompts
- `PUT /api/v1/prompts/{id}` - Update prompt

#### Optimization
- `POST /api/v1/optimize/start` - Start optimization
- `GET /api/v1/optimize/{task_id}/status` - Get status
- `WS /ws/optimization/{task_id}` - Real-time updates

## Security

### Authentication

Currently uses session-based authentication. API key support planned for future releases.

### HTTPS/TLS

For production deployment with HTTPS:

1. Obtain SSL certificates
2. Configure nginx with SSL
3. Update environment variables:

```bash
VITE_API_URL=https://api.yourdomain.com
VITE_WS_URL=wss://api.yourdomain.com
```

### Security Headers

The application includes security headers:
- X-Frame-Options
- X-XSS-Protection
- X-Content-Type-Options
- Content-Security-Policy

## Backup and Recovery

### Automated Backups

```bash
# Create backup
./scripts/deploy.sh backup

# Backups are stored in ./backups/ directory
```

### Manual Backup

```bash
# Database backup
docker-compose exec db pg_dump -U nova_user nova_optimizer > backup.sql

# File uploads backup
docker-compose exec backend tar -czf uploads_backup.tar.gz -C /app uploads
```

### Recovery

```bash
# Restore from backup
./scripts/deploy.sh rollback backups/backup_20240115_143022.tar.gz
```

## Troubleshooting

### Common Issues

#### Application Won't Start

1. Check Docker is running: `docker info`
2. Verify environment file: `cat .env`
3. Check logs: `docker-compose logs`

#### Database Connection Issues

1. Verify database is running: `docker-compose ps db`
2. Check database logs: `docker-compose logs db`
3. Test connection: `docker-compose exec db pg_isready`

#### High Memory Usage

1. Check system resources: `docker stats`
2. Reduce worker count in `.env`
3. Increase system memory

#### Slow Performance

1. Check system resources
2. Optimize database queries
3. Enable Redis caching
4. Scale horizontally

### Getting Help

1. Check logs: `./scripts/deploy.sh logs`
2. Verify health: `curl http://localhost:8000/health/detailed`
3. Review documentation: http://localhost:8000/docs-static/
4. Contact support team

## Development

### Contributing

1. Fork the repository
2. Create feature branch: `git checkout -b feature/new-feature`
3. Make changes and add tests
4. Run tests: `npm test` and `pytest`
5. Submit pull request

### Code Style

- **Backend**: Black, isort, flake8, mypy
- **Frontend**: Prettier, ESLint, TypeScript strict mode

### Testing

- **Unit Tests**: Jest (frontend), pytest (backend)
- **Integration Tests**: API testing with real database
- **E2E Tests**: Playwright for full workflow testing

## License

This project is licensed under the Apache 2.0 License - see the LICENSE file for details.

## Support

- **Documentation**: [User Guide](./docs/user-guide/)
- **API Reference**: [API Documentation](./docs/api/)
- **Developer Guide**: [Developer Documentation](./docs/developer/)
- **Issues**: GitHub Issues
- **Discussions**: GitHub Discussions