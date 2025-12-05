# Multimodal Image Support

## Overview

Nova Prompt Optimizer now supports multimodal (image + text) inputs for prompt optimization and evaluation. This enables use cases like:

- Image classification and tagging
- OCR and text extraction from images
- Visual question answering
- Watermark detection
- Object detection and description

## Features

- **Automatic Image Detection**: Detects image paths in prompts and loads them automatically
- **Multiple Formats**: Supports JPEG, PNG, GIF, WebP
- **Local & Remote**: Load images from local filesystem or URLs
- **Template-Aware**: Preserves template variables like `{input}` without treating them as file paths
- **MIPROv2 Compatible**: Images preserved during optimization
- **Backward Compatible**: Text-only workflows unchanged
- **Configurable**: Can disable image support via feature flag
- **Performant**: No overhead for text-only prompts

## Quick Start

### Basic Usage

```python
from amzn_nova_prompt_optimizer.core.input_adapters.prompt_adapter import TextPromptAdapter
from amzn_nova_prompt_optimizer.core.inference.adapter import BedrockInferenceAdapter

# Setup prompt with image reference
prompt_adapter = TextPromptAdapter()
prompt_adapter.set_system_prompt("You are an assistant that analyzes images.")
prompt_adapter.set_user_prompt(
    content="Analyze this image for watermarks: {input}",
    variables={"input"}
)
prompt_adapter.adapt()

# Dataset with image paths
dataset = [
    {"input": "images/photo1.jpg", "output": "Watermark: Company Logo"},
    {"input": "images/photo2.jpg", "output": "No watermark"}
]

# Images are automatically loaded and sent to Bedrock
inference_adapter = BedrockInferenceAdapter(region_name="us-west-2")
result = inference_adapter.call_model(
    model_id="us.amazon.nova-pro-v1:0",
    system_prompt="You are an assistant that analyzes images.",
    messages=[{"user": "Analyze this image for watermarks: images/photo1.jpg"}],
    inf_config={"max_tokens": 200, "temperature": 0.7, "top_p": 0.9, "top_k": 50}
)
```

### With Optimization

```python
from amzn_nova_prompt_optimizer.core.optimizers import NovaPromptOptimizer
from amzn_nova_prompt_optimizer.core.input_adapters.dataset_adapter import JSONDatasetAdapter
from amzn_nova_prompt_optimizer.core.input_adapters.metric_adapter import MetricAdapter

# Setup dataset
dataset_adapter = JSONDatasetAdapter(
    input_columns={"input"},
    output_columns={"output"}
).adapt("dataset.jsonl")

# Define metric
class ImageMetric(MetricAdapter):
    def apply(self, y_pred, y_true):
        # Your metric logic
        return 1.0 if y_pred == y_true else 0.0

# Optimize with images
optimizer = NovaPromptOptimizer(
    prompt_adapter=prompt_adapter,
    inference_adapter=inference_adapter,
    dataset_adapter=dataset_adapter,
    metric_adapter=ImageMetric()
)

optimized_prompt = optimizer.optimize(
    mode="custom",
    custom_params={
        "task_model_id": "us.amazon.nova-pro-v1:0",
        "num_candidates": 10,
        "num_trials": 3
    }
)
```

## Supported Patterns

### Pattern 1: Explicit Image Marker
```python
"Analyze this image for watermarks: images/photo.jpg"
```

### Pattern 2: Direct File Path
```python
"images/photo.jpg"  # If file exists and has image extension
```

### Pattern 3: URL
```python
"https://example.com/image.jpg"
```

### Pattern 4: MIPROv2 Format
```python
"Analyze this image for watermarks: [][images/photo.jpg]"
```

### Pattern 5: Template Variables (NOT treated as images)
```python
"Analyze this image for watermarks: {input}"  # Preserved as template
```

## Configuration

### Disable Image Support

```python
from amzn_nova_prompt_optimizer.core.inference.bedrock_converse import BedrockConverseHandler
import boto3

session = boto3.Session()
bedrock_client = session.client('bedrock-runtime', region_name='us-west-2')

# Disable image support
handler = BedrockConverseHandler(bedrock_client, enable_image_support=False)
```

### Check if Image Support Available

```python
from amzn_nova_prompt_optimizer.core.inference.bedrock_converse import IMAGE_SUPPORT_AVAILABLE

if IMAGE_SUPPORT_AVAILABLE:
    print("Image support is available")
else:
    print("Install PIL and requests: pip install Pillow requests")
```

## Requirements

Image support requires additional dependencies:

```bash
pip install Pillow requests
```

If these are not installed, the optimizer will:
- Log a warning
- Fall back to text-only mode
- Continue working normally for text prompts

## Supported Models

All Bedrock models that support the Converse API with multimodal inputs:

- Amazon Nova Lite (`us.amazon.nova-lite-v1:0`)
- Amazon Nova Pro (`us.amazon.nova-pro-v1:0`)
- Amazon Nova Premier (`us.amazon.nova-premier-v1:0`)
- Anthropic Claude 3 models
- Other multimodal models via Bedrock

## Performance

- **Text-only**: No performance impact (< 0.001ms overhead per message)
- **Image loading**: Lazy loading only when image patterns detected
- **Caching**: Images loaded once per inference call

## Troubleshooting

### Images Not Loading

1. **Check file path**: Ensure the path is correct and file exists
2. **Check format**: Supported formats: JPEG, PNG, GIF, WebP
3. **Check permissions**: Ensure read access to image files
4. **Enable logging**: Set log level to DEBUG to see image loading details

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

### Template Variables Treated as Images

If your template variable is being treated as an image path:
- Ensure it's in the format `{variable}` or `{{variable}}`
- Avoid using actual file paths as template variable names

### Performance Issues

If image loading is slow:
- Use local files instead of URLs when possible
- Resize large images before processing
- Consider using a CDN for remote images

## Examples

See the `tests/` directory for comprehensive examples:
- `test_bedrock_converse_compatibility.py` - Basic compatibility tests
- `test_comprehensive_validation.py` - Full validation suite
- `test_miprov2_integration.py` - MIPROv2 optimization tests

## API Reference

### BedrockConverseHandler

```python
class BedrockConverseHandler:
    def __init__(self, bedrock_client, enable_image_support=True):
        """
        Initialize Bedrock Converse Handler.
        
        Args:
            bedrock_client: Boto3 Bedrock client
            enable_image_support: Enable automatic image loading (default: True)
        """
```

### ImageAwareLM

```python
class ImageAwareLM:
    def __init__(self, base_lm, bedrock_client, model_id: str):
        """
        Initialize image-aware LM wrapper for MIPROv2.
        
        Args:
            base_lm: Base DSPy LM to wrap
            bedrock_client: Boto3 Bedrock client
            model_id: Bedrock model ID
        """
```

## Contributing

See [CONTRIBUTING.md](../CONTRIBUTING.md) for guidelines on contributing to this feature.

## License

Copyright 2025 Amazon Inc. Licensed under the Apache License, Version 2.0.
