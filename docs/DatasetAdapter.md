## Dataset Adapter

**Core Functions**

Adapt to the Standardized format
```python
# Adapt to the Standardized Format (JSON)
.adapt()
```

Show Dataset Samples
```python
# Prints the datasets first 10 rows to view
.show()
```

Fetches the dataset
```python
# Fetches the dataset as a List of JSON in standardized format
.fetch()
```

Splits the dataset into Train and Test Set
```python
# Splits the dataset based on provided percentage (0 to 1). Stratifies if Set.
.split(split_percentage: float, stratify: bool = False)
```

**Standardized Data Format**

```json
{
    "inputs": {
        "prompt_var_key_1": "foo",
        "prompt_var_key_2": "bar",
        "model_input": "model input"
  },
    "outputs": {
        "ground_truth": "ground_truth"
  }
}
```

### Example

JSONL Input

```python
row = {"product_type": "foo", "conversation_history": "bar", "question": "what's the...", "answer": "the..", "ground_truth": "{\"score\": \"4\", \"sentiment\": \"POSITIVE\"}"}
```

Adapt 
```python
.adapt()
```

Standardized Data
```python
row = {
    "inputs": {
        "product_type": "foo",
        "conversation_history": "bar",
        "question": "what's the ...",
        "answer": "The...."
    },
    "outputs": {
        "ground_truth": "{\"score\": \"4\", \"sentiment\": \"POSITIVE\"}"
    }
}
```
