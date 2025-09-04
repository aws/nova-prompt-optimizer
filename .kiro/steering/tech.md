# Technology Stack

## Build System
- **Package Manager**: pip3
- **Build Backend**: setuptools with build system requirements
- **Distribution**: Standard Python wheel distribution via PyPI

## Core Dependencies
- **AWS SDK**: boto3, botocore, boto3-stubs for AWS Bedrock integration
- **ML Framework**: dspy for optimization algorithms (MIPROv2)
- **Template Engine**: jinja2 for prompt templating
- **Data Processing**: numpy for numerical operations
- **HTTP**: urllib3, h11 for network operations
- **Environment**: virtualenv for isolated environments

## Python Requirements
- **Minimum Version**: Python 3.11+
- **Type Hints**: Full type annotation support with py.typed marker

## Common Commands

### Installation
```bash
pip3 install nova-prompt-optimizer
```

### Development Setup
```bash
# Install with dev dependencies
pip install -e ".[dev]"

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On macOS/Linux
```

### Testing
```bash
# Run all tests
python -m unittest discover tests/

# Run specific test module
python -m unittest tests.core.input_adapters.test_dataset_adapter
```

### Building
```bash
# Build package
python -m build

# Install locally for testing
pip install -e .
```

### AWS Prerequisites
```bash
# Set AWS credentials
export AWS_ACCESS_KEY_ID="..."
export AWS_SECRET_ACCESS_KEY="..."

# Configure AWS CLI (alternative)
aws configure
```

## Architecture Patterns
- **Adapter Pattern**: Core design pattern for all components
- **Abstract Base Classes**: Extensive use of ABC for interface definition
- **Dependency Injection**: Components accept other adapters as dependencies
- **Method Chaining**: Fluent interface design for adapter operations