# Nova Prompt Optimizer

A Python SDK for optimizing prompts for Amazon Nova models using AWS Bedrock.

## Purpose
The Nova Prompt Optimizer provides a modular approach to prompt optimization through adapters that handle different aspects of the optimization pipeline:
- Prompt loading and formatting
- Dataset management and evaluation
- Model inference via AWS Bedrock
- Custom metrics and evaluation
- Optimization algorithms (NovaPromptOptimizer, MIPROv2)

## Key Features
- **Adapter Pattern**: Modular components for prompts, datasets, metrics, and inference
- **Multiple Optimizers**: NovaPromptOptimizer (meta prompting + MIPROv2) and standalone optimizers
- **AWS Integration**: Built for AWS Bedrock with Nova model support
- **Evaluation Framework**: Custom metrics and comprehensive evaluation tools
- **Dataset Support**: JSON and CSV dataset adapters with train/test splitting

## Target Use Cases
- Prompt optimization for classification tasks
- Few-shot learning optimization
- System and user prompt refinement
- Performance evaluation and benchmarking

## Status
Currently in public preview - functionality may change as more use cases are supported.