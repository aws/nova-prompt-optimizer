#!/bin/bash

# Nova Prompt Optimizer - Production Deployment Script
# This script handles the complete deployment process for production environments

set -e  # Exit on any error

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
ENV_FILE="${PROJECT_DIR}/.env"
COMPOSE_FILE="${PROJECT_DIR}/docker-compose.prod.yml"
BACKUP_DIR="${PROJECT_DIR}/backups"
LOG_FILE="${PROJECT_DIR}/logs/deploy.log"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Logging function
log() {
    local level=$1
    shift
    local message="$*"
    local timestamp=$(date '+%Y-%m-%d %H:%M:%S')
    
    case $level in
        "INFO")
            echo -e "${GREEN}[INFO]${NC} $message"
            ;;
        "WARN")
            echo -e "${YELLOW}[WARN]${NC} $message"
            ;;
        "ERROR")
            echo -e "${RED}[ERROR]${NC} $message"
            ;;
        "DEBUG")
            echo -e "${BLUE}[DEBUG]${NC} $message"
            ;;
    esac
    
    # Also log to file
    mkdir -p "$(dirname "$LOG_FILE")"
    echo "[$timestamp] [$level] $message" >> "$LOG_FILE"
}

# Function to check prerequisites
check_prerequisites() {
    log "INFO" "Checking prerequisites..."
    
    # Check if Docker is installed and running
    if ! command -v docker &> /dev/null; then
        log "ERROR" "Docker is not installed. Please install Docker first."
        exit 1
    fi
    
    if ! docker info &> /dev/null; then
        log "ERROR" "Docker is not running. Please start Docker first."
        exit 1
    fi
    
    # Check if Docker Compose is available
    if ! command -v docker-compose &> /dev/null && ! docker compose version &> /dev/null; then
        log "ERROR" "Docker Compose is not available. Please install Docker Compose."
        exit 1
    fi
    
    # Check if environment file exists
    if [ ! -f "$ENV_FILE" ]; then
        log "ERROR" "Environment file not found at $ENV_FILE"
        log "INFO" "Please copy .env.example to .env and configure it"
        exit 1
    fi
    
    # Check if compose file exists
    if [ ! -f "$COMPOSE_FILE" ]; then
        log "ERROR" "Docker Compose file not found at $COMPOSE_FILE"
        exit 1
    fi
    
    log "INFO" "Prerequisites check passed"
}

# Function to validate environment configuration
validate_environment() {
    log "INFO" "Validating environment configuration..."
    
    # Source environment file
    set -a
    source "$ENV_FILE"
    set +a
    
    # Check required variables
    local required_vars=(
        "POSTGRES_PASSWORD"
        "REDIS_PASSWORD"
        "SECRET_KEY"
        "AWS_ACCESS_KEY_ID"
        "AWS_SECRET_ACCESS_KEY"
    )
    
    local missing_vars=()
    for var in "${required_vars[@]}"; do
        if [ -z "${!var}" ]; then
            missing_vars+=("$var")
        fi
    done
    
    if [ ${#missing_vars[@]} -ne 0 ]; then
        log "ERROR" "Missing required environment variables:"
        for var in "${missing_vars[@]}"; do
            log "ERROR" "  - $var"
        done
        exit 1
    fi
    
    # Validate password strength
    if [ ${#POSTGRES_PASSWORD} -lt 12 ]; then
        log "WARN" "POSTGRES_PASSWORD should be at least 12 characters long"
    fi
    
    if [ ${#SECRET_KEY} -lt 32 ]; then
        log "ERROR" "SECRET_KEY must be at least 32 characters long"
        exit 1
    fi
    
    log "INFO" "Environment validation passed"
}

# Function to create backup
create_backup() {
    if [ "$1" = "--skip-backup" ]; then
        log "INFO" "Skipping backup as requested"
        return 0
    fi
    
    log "INFO" "Creating backup..."
    
    mkdir -p "$BACKUP_DIR"
    local backup_timestamp=$(date '+%Y%m%d_%H%M%S')
    local backup_file="${BACKUP_DIR}/backup_${backup_timestamp}.tar.gz"
    
    # Check if containers are running
    if docker-compose -f "$COMPOSE_FILE" ps | grep -q "Up"; then
        log "INFO" "Creating database backup..."
        
        # Backup database
        docker-compose -f "$COMPOSE_FILE" exec -T db pg_dump \
            -U "${POSTGRES_USER:-nova_user}" \
            -d "${POSTGRES_DB:-nova_optimizer}" \
            --no-password > "${BACKUP_DIR}/db_${backup_timestamp}.sql"
        
        # Backup uploaded files
        if docker-compose -f "$COMPOSE_FILE" ps backend | grep -q "Up"; then
            log "INFO" "Creating uploads backup..."
            docker-compose -f "$COMPOSE_FILE" exec -T backend \
                tar -czf - -C /app uploads > "${BACKUP_DIR}/uploads_${backup_timestamp}.tar.gz"
        fi
        
        # Create combined backup
        tar -czf "$backup_file" -C "$BACKUP_DIR" \
            "db_${backup_timestamp}.sql" \
            "uploads_${backup_timestamp}.tar.gz" 2>/dev/null || true
        
        # Clean up individual files
        rm -f "${BACKUP_DIR}/db_${backup_timestamp}.sql"
        rm -f "${BACKUP_DIR}/uploads_${backup_timestamp}.tar.gz"
        
        log "INFO" "Backup created: $backup_file"
    else
        log "WARN" "No running containers found, skipping backup"
    fi
}

# Function to build images
build_images() {
    log "INFO" "Building Docker images..."
    
    # Build with no cache for production
    docker-compose -f "$COMPOSE_FILE" build --no-cache --parallel
    
    log "INFO" "Docker images built successfully"
}

# Function to run database migrations
run_migrations() {
    log "INFO" "Running database migrations..."
    
    # Wait for database to be ready
    local max_attempts=30
    local attempt=1
    
    while [ $attempt -le $max_attempts ]; do
        if docker-compose -f "$COMPOSE_FILE" exec -T db pg_isready \
            -U "${POSTGRES_USER:-nova_user}" \
            -d "${POSTGRES_DB:-nova_optimizer}" &> /dev/null; then
            break
        fi
        
        log "INFO" "Waiting for database to be ready... (attempt $attempt/$max_attempts)"
        sleep 2
        ((attempt++))
    done
    
    if [ $attempt -gt $max_attempts ]; then
        log "ERROR" "Database failed to become ready"
        exit 1
    fi
    
    # Run migrations
    docker-compose -f "$COMPOSE_FILE" exec -T backend \
        alembic upgrade head
    
    log "INFO" "Database migrations completed"
}

# Function to perform health checks
health_check() {
    log "INFO" "Performing health checks..."
    
    local services=("backend" "frontend" "db" "redis")
    local max_attempts=30
    
    for service in "${services[@]}"; do
        log "INFO" "Checking health of $service..."
        local attempt=1
        
        while [ $attempt -le $max_attempts ]; do
            if docker-compose -f "$COMPOSE_FILE" ps "$service" | grep -q "healthy\|Up"; then
                log "INFO" "$service is healthy"
                break
            fi
            
            if [ $attempt -eq $max_attempts ]; then
                log "ERROR" "$service failed health check"
                return 1
            fi
            
            sleep 2
            ((attempt++))
        done
    done
    
    log "INFO" "All health checks passed"
}

# Function to deploy application
deploy() {
    local skip_backup=false
    local skip_build=false
    
    # Parse arguments
    while [[ $# -gt 0 ]]; do
        case $1 in
            --skip-backup)
                skip_backup=true
                shift
                ;;
            --skip-build)
                skip_build=true
                shift
                ;;
            *)
                log "ERROR" "Unknown option: $1"
                exit 1
                ;;
        esac
    done
    
    log "INFO" "Starting deployment process..."
    
    # Create backup
    if [ "$skip_backup" = false ]; then
        create_backup
    fi
    
    # Build images
    if [ "$skip_build" = false ]; then
        build_images
    fi
    
    # Stop existing containers
    log "INFO" "Stopping existing containers..."
    docker-compose -f "$COMPOSE_FILE" down
    
    # Start services
    log "INFO" "Starting services..."
    docker-compose -f "$COMPOSE_FILE" up -d
    
    # Wait for services to be ready
    sleep 10
    
    # Run migrations
    run_migrations
    
    # Perform health checks
    health_check
    
    log "INFO" "Deployment completed successfully!"
    log "INFO" "Application is available at: ${VITE_API_URL:-http://localhost}"
}

# Function to rollback deployment
rollback() {
    local backup_file=$1
    
    if [ -z "$backup_file" ]; then
        log "ERROR" "Please specify backup file for rollback"
        exit 1
    fi
    
    if [ ! -f "$backup_file" ]; then
        log "ERROR" "Backup file not found: $backup_file"
        exit 1
    fi
    
    log "INFO" "Rolling back to backup: $backup_file"
    
    # Stop current containers
    docker-compose -f "$COMPOSE_FILE" down
    
    # Extract backup
    local temp_dir=$(mktemp -d)
    tar -xzf "$backup_file" -C "$temp_dir"
    
    # Start database
    docker-compose -f "$COMPOSE_FILE" up -d db
    sleep 10
    
    # Restore database
    if [ -f "$temp_dir/db_"*.sql ]; then
        log "INFO" "Restoring database..."
        docker-compose -f "$COMPOSE_FILE" exec -T db psql \
            -U "${POSTGRES_USER:-nova_user}" \
            -d "${POSTGRES_DB:-nova_optimizer}" \
            < "$temp_dir/db_"*.sql
    fi
    
    # Start all services
    docker-compose -f "$COMPOSE_FILE" up -d
    
    # Restore uploads
    if [ -f "$temp_dir/uploads_"*.tar.gz ]; then
        log "INFO" "Restoring uploads..."
        docker-compose -f "$COMPOSE_FILE" exec -T backend \
            tar -xzf - -C /app < "$temp_dir/uploads_"*.tar.gz
    fi
    
    # Clean up
    rm -rf "$temp_dir"
    
    log "INFO" "Rollback completed"
}

# Function to show status
show_status() {
    log "INFO" "Application Status:"
    docker-compose -f "$COMPOSE_FILE" ps
    
    echo ""
    log "INFO" "Service URLs:"
    echo "  Frontend: ${VITE_API_URL:-http://localhost}"
    echo "  API: ${VITE_API_URL:-http://localhost:8000}"
    echo "  API Docs: ${VITE_API_URL:-http://localhost:8000}/docs"
    
    if docker-compose -f "$COMPOSE_FILE" --profile monitoring ps | grep -q prometheus; then
        echo "  Prometheus: http://localhost:9090"
        echo "  Grafana: http://localhost:3000"
    fi
}

# Function to show logs
show_logs() {
    local service=${1:-}
    local lines=${2:-100}
    
    if [ -n "$service" ]; then
        docker-compose -f "$COMPOSE_FILE" logs --tail="$lines" -f "$service"
    else
        docker-compose -f "$COMPOSE_FILE" logs --tail="$lines" -f
    fi
}

# Function to show help
show_help() {
    echo "Nova Prompt Optimizer Deployment Script"
    echo ""
    echo "Usage: $0 [COMMAND] [OPTIONS]"
    echo ""
    echo "Commands:"
    echo "  deploy              Deploy the application"
    echo "  rollback <backup>   Rollback to a specific backup"
    echo "  status              Show application status"
    echo "  logs [service]      Show logs (optionally for specific service)"
    echo "  backup              Create a backup"
    echo "  help                Show this help message"
    echo ""
    echo "Deploy Options:"
    echo "  --skip-backup       Skip creating backup before deployment"
    echo "  --skip-build        Skip building Docker images"
    echo ""
    echo "Examples:"
    echo "  $0 deploy                                    # Full deployment"
    echo "  $0 deploy --skip-backup                      # Deploy without backup"
    echo "  $0 rollback backups/backup_20240115_143022.tar.gz"
    echo "  $0 logs backend                              # Show backend logs"
    echo "  $0 status                                    # Show status"
}

# Main script logic
main() {
    local command=${1:-help}
    
    case $command in
        "deploy")
            shift
            check_prerequisites
            validate_environment
            deploy "$@"
            show_status
            ;;
        "rollback")
            shift
            check_prerequisites
            rollback "$@"
            ;;
        "status")
            show_status
            ;;
        "logs")
            shift
            show_logs "$@"
            ;;
        "backup")
            check_prerequisites
            validate_environment
            create_backup
            ;;
        "help"|"--help"|"-h")
            show_help
            ;;
        *)
            log "ERROR" "Unknown command: $command"
            show_help
            exit 1
            ;;
    esac
}

# Run main function with all arguments
main "$@"