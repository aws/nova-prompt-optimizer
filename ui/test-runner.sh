#!/bin/bash

# Nova Prompt Optimizer Frontend Test Runner
# This script runs all tests for both backend and frontend

set -e

echo "🧪 Nova Prompt Optimizer Frontend Test Suite"
echo "============================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if we're in the right directory
if [ ! -f "test-runner.sh" ]; then
    print_error "Please run this script from the ui/ directory"
    exit 1
fi

# Parse command line arguments
BACKEND_ONLY=false
FRONTEND_ONLY=false
E2E_ONLY=false
COVERAGE=false
PARALLEL=false

while [[ $# -gt 0 ]]; do
    case $1 in
        --backend-only)
            BACKEND_ONLY=true
            shift
            ;;
        --frontend-only)
            FRONTEND_ONLY=true
            shift
            ;;
        --e2e-only)
            E2E_ONLY=true
            shift
            ;;
        --coverage)
            COVERAGE=true
            shift
            ;;
        --parallel)
            PARALLEL=true
            shift
            ;;
        --help)
            echo "Usage: $0 [OPTIONS]"
            echo ""
            echo "Options:"
            echo "  --backend-only    Run only backend tests"
            echo "  --frontend-only   Run only frontend tests"
            echo "  --e2e-only        Run only end-to-end tests"
            echo "  --coverage        Generate coverage reports"
            echo "  --parallel        Run tests in parallel where possible"
            echo "  --help            Show this help message"
            exit 0
            ;;
        *)
            print_error "Unknown option: $1"
            exit 1
            ;;
    esac
done

# Backend Tests
if [ "$FRONTEND_ONLY" = false ] && [ "$E2E_ONLY" = false ]; then
    print_status "Running Backend Tests..."
    cd backend
    
    if [ "$COVERAGE" = true ]; then
        if [ "$PARALLEL" = true ]; then
            python -m pytest -n auto --cov=app --cov-report=html --cov-report=term-missing
        else
            python -m pytest --cov=app --cov-report=html --cov-report=term-missing
        fi
    else
        if [ "$PARALLEL" = true ]; then
            python -m pytest -n auto
        else
            python -m pytest
        fi
    fi
    
    BACKEND_EXIT_CODE=$?
    cd ..
    
    if [ $BACKEND_EXIT_CODE -ne 0 ]; then
        print_error "Backend tests failed!"
        if [ "$BACKEND_ONLY" = true ]; then
            exit $BACKEND_EXIT_CODE
        fi
    else
        print_status "Backend tests passed!"
    fi
fi

# Frontend Tests
if [ "$BACKEND_ONLY" = false ] && [ "$E2E_ONLY" = false ]; then
    print_status "Running Frontend Tests..."
    cd frontend
    
    # Check if node_modules exists
    if [ ! -d "node_modules" ]; then
        print_warning "node_modules not found. Installing dependencies..."
        npm install
    fi
    
    if [ "$COVERAGE" = true ]; then
        npm run test:coverage
    else
        npm run test
    fi
    
    FRONTEND_EXIT_CODE=$?
    cd ..
    
    if [ $FRONTEND_EXIT_CODE -ne 0 ]; then
        print_error "Frontend tests failed!"
        if [ "$FRONTEND_ONLY" = true ]; then
            exit $FRONTEND_EXIT_CODE
        fi
    else
        print_status "Frontend tests passed!"
    fi
fi

# End-to-End Tests
if [ "$BACKEND_ONLY" = false ] && [ "$FRONTEND_ONLY" = false ] || [ "$E2E_ONLY" = true ]; then
    print_status "Running End-to-End Tests..."
    cd frontend
    
    # Check if Cypress is installed
    if [ ! -d "node_modules/cypress" ]; then
        print_warning "Cypress not found. Installing dependencies..."
        npm install
    fi
    
    # Start the development server in the background
    print_status "Starting development server..."
    npm run dev &
    DEV_SERVER_PID=$!
    
    # Wait for the server to start
    print_status "Waiting for server to start..."
    sleep 10
    
    # Run Cypress tests
    npm run test:e2e
    E2E_EXIT_CODE=$?
    
    # Kill the development server
    kill $DEV_SERVER_PID 2>/dev/null || true
    
    cd ..
    
    if [ $E2E_EXIT_CODE -ne 0 ]; then
        print_error "End-to-end tests failed!"
        exit $E2E_EXIT_CODE
    else
        print_status "End-to-end tests passed!"
    fi
fi

# Summary
echo ""
print_status "Test Summary:"
echo "============="

if [ "$FRONTEND_ONLY" = false ] && [ "$E2E_ONLY" = false ]; then
    if [ $BACKEND_EXIT_CODE -eq 0 ]; then
        echo -e "Backend Tests: ${GREEN}PASSED${NC}"
    else
        echo -e "Backend Tests: ${RED}FAILED${NC}"
    fi
fi

if [ "$BACKEND_ONLY" = false ] && [ "$E2E_ONLY" = false ]; then
    if [ $FRONTEND_EXIT_CODE -eq 0 ]; then
        echo -e "Frontend Tests: ${GREEN}PASSED${NC}"
    else
        echo -e "Frontend Tests: ${RED}FAILED${NC}"
    fi
fi

if [ "$BACKEND_ONLY" = false ] && [ "$FRONTEND_ONLY" = false ] || [ "$E2E_ONLY" = true ]; then
    if [ $E2E_EXIT_CODE -eq 0 ]; then
        echo -e "E2E Tests: ${GREEN}PASSED${NC}"
    else
        echo -e "E2E Tests: ${RED}FAILED${NC}"
    fi
fi

# Coverage reports
if [ "$COVERAGE" = true ]; then
    echo ""
    print_status "Coverage Reports Generated:"
    echo "Backend: backend/htmlcov/index.html"
    echo "Frontend: frontend/coverage/index.html"
fi

echo ""
print_status "All tests completed!"