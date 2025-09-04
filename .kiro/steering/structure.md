# Project Structure

## Root Directory
- `pyproject.toml` - Project configuration and build settings
- `requirements.txt` - Runtime dependencies
- `README.md` - Main documentation and usage examples
- `CONTRIBUTING.md` - Contribution guidelines and development workflow
- `LICENSE` - Apache 2.0 license
- `CODEOWNERS` - Code ownership and review assignments

## Source Code (`src/amzn_nova_prompt_optimizer/`)
```
src/amzn_nova_prompt_optimizer/
├── __init__.py              # Package initialization with logging setup
├── __version__.py           # Version information
├── py.typed                 # Type hints marker file
├── core/                    # Core functionality modules
│   ├── evaluation/          # Evaluation framework
│   ├── inference/           # Model inference adapters
│   │   ├── adapter.py       # BedrockInferenceAdapter
│   │   ├── bedrock_converse.py
│   │   └── inference_constants.py
│   ├── input_adapters/      # Data and prompt adapters
│   │   ├── dataset_adapter.py    # JSON/CSV dataset handling
│   │   ├── metric_adapter.py     # Custom evaluation metrics
│   │   └── prompt_adapter.py     # Prompt loading and formatting
│   └── optimizers/          # Optimization algorithms
│       ├── adapter.py       # Base optimizer interface
│       ├── miprov2/         # MIPROv2 implementation
│       ├── nova_meta_prompter/   # Meta prompting optimizer
│       └── nova_prompt_optimizer/ # Combined optimizer
└── util/                    # Utility modules
    ├── logging_utils.py     # Logging configuration
    └── rate_limiter.py      # API rate limiting
```

## Tests (`tests/`)
- Mirror the source structure with `test_` prefixed files
- Use `unittest` framework with comprehensive mocking
- Each adapter/component has dedicated test modules

## Documentation (`docs/`)
- `DatasetAdapter.md` - Dataset adapter documentation
- `Optimizers.md` - Optimizer documentation
- `PromptAdapter.md` - Prompt adapter documentation
- `adapters.png` - Architecture diagram

## Samples (`samples/`)
- `facility-support-analyzer/` - Complete example with:
  - Sample datasets (CSV/JSONL)
  - Jupyter notebooks demonstrating optimization workflows
  - Original vs optimized prompt comparisons
  - Both user-only and system+user prompt optimization examples

## Naming Conventions
- **Modules**: snake_case (e.g., `dataset_adapter.py`)
- **Classes**: PascalCase with descriptive suffixes (e.g., `JSONDatasetAdapter`)
- **Methods**: snake_case with clear action verbs (e.g., `adapt()`, `batch_apply()`)
- **Constants**: UPPER_SNAKE_CASE (e.g., `OUTPUTS_FIELD`)

## Import Patterns
- Use absolute imports from package root
- Import specific classes/functions rather than modules when possible
- Group imports: standard library, third-party, local modules

## File Organization Principles
- **Separation of Concerns**: Each adapter type in its own module
- **Abstract Base Classes**: Define interfaces before implementations
- **Modular Design**: Components can be used independently
- **Clear Hierarchies**: Core functionality separated from utilities