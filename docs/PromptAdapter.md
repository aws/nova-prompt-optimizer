## Prompt Adapter
**Core Functions**

Set System Prompt as file_path or content
```python
# Set the System Prompt for the Adapter
.set_system_prompt(file_path=, variables=)
```

Set User Prompt as file_path or content
```python
# Set the User Prompt for the Adapter
.set_user_prompt(content=, variables=)
```

Add Few Shot examples to the Prompt, choose format_type based on your prompting strategy.
```python
# (Optional) Add few shot examples
.add_few_shot(examples=, format_type="converse"|"append_to_user_prompt"|"append_to_system_prompt")
```

Adapt the Prompt
```python
# Adapt prompt to Standardized Format
.adapt()
```

Save the prompt to a directory. Saves a user_prompt.txt, system_prompt.txt and optionally a few_shot.json file
```python
# Save the prompt to the required format, requires directory path
.save("path/to/directory")
```

**Standardized Prompt Format**
```json
{
    "user_prompt_component": {
        "variables": ["var_1", "var_2", "var_3"],
        "template": "Task: You are a...... {{var_1}}, {{var_2}}",
        "metadata": {
            "format": "text",
        }
    },
    "system_prompt_component": {
        "variables": ["var_1", "var_2", "var_3"],
        "template": "Task: You are a...... {{var_1}}, {{var_2}}",
        "metadata": {
            "format": "text",
        }
    },
    "few_shot": {
        "examples": [{
            "input": "",
            "output": ""
        }, {
            "input": "",
            "output": ""
        }],
        "format": "converse" | "append_to_user_prompt" | "append_to_system_prompt"
    }
}
```


**Example**

Inputs to the Prompt Adapter
```
# system_prompt.txt
'''
You are a review classifier for ABC. Provide a review....
'''
```
```
# user_prompt.txt
'''
Classify the sentiment of the following review:

{{ review }}

Respond only with: positive, neutral, or negative.
'''
```

Functionality of Prompt Adapter
```python
.set_system_prompt(file_path="system_prompt.txt", variables={})

.set_user_prompt(file_path="user_prompt.txt", variables={"review"})

.adapt()
```

Standardized Prompt 
```json
## Standardized Prompt
{
    "user_prompt_component": {
        "variables": ["review"],
        "template": "Classify the sentiment of the following review....",
        "metadata": {
            "format": "text",
        }
    },
    "system_prompt_component": {
        "variables": [],
        "template": "You are a review classifier for ABC. Provide a review....",
        "metadata": {
            "format": "text",
        }
    }
}
```

#### Supported Few-Shot Formats
**1. Converse**

When Few-Shot format type is `converse`, we pass the examples as User/Assistant turns when running inference.

When you save the prompt adapter, we save the `system_prompt.txt`, `user_prompt.txt`, and `few_shot.json` in
Converse format.

Example:
```json
{
    "user_prompt_component": {
        "variables": ["review"],
        "template": "Classify the sentiment of the following review....",
        "metadata": {
            "format": "text"
        }
    },
    "system_prompt_component": {
        "variables": [],
        "template": "You are a review classifier for ABC. Provide a review....",
        "metadata": {
            "format": "text"
        }
    },
    "few_shot": {
        "examples": [{
            "input": "foo_1",
            "output": "bar_1"
        }, {
            "input": "foo_2",
            "output": "bar_2"
        }],
        "format": "converse"
    }
}
```
On Saving
```python
prompt_adapter.save("optimized_prompt/")
```

Saved User Prompt (user_prompt.txt)
```user_prompt.txt
Classify the sentiment of the following review....
```
Saved System Prompt (system_prompt.txt)
```system_prompt.txt
You are a review classifier for ABC. Provide a review....
```

Saved Few Shot Samples (few_shot.json)
```json
[{
    "role": "user",
    "content": [{
        "text": "foo_1"
    }]
}, {
    "role": "assistant",
    "content": [{
        "text": "bar_1"
    }]
},{
    "role": "user",
    "content": [{
        "text": "foo_2"
    }]
}, {
    "role": "assistant",
    "content": [{
        "text": "bar_2"
    }]
}]
```

**2. Append to User Prompt / Append to System Prompt**

When Few-Shot format type is `append_to_user_prompt` or `append_to_system_prompt`, we append the examples to either the user_prompt or the system prompt based on the specification

When you save the prompt adapter, we save the `system_prompt.txt` and `user_prompt.txt` and they will contain the examples

Example:
```json
{
    "user_prompt_component": {
        "variables": ["review"],
        "template": "Classify the sentiment of the following review....",
        "metadata": {
            "format": "text"
        }
    },
    "system_prompt_component": {
        "variables": [],
        "template": "You are a review classifier for ABC. Provide a review....",
        "metadata": {
            "format": "text"
        }
    },
    "few_shot": {
        "examples": [{
            "input": "foo_1",
            "output": "bar_1"
        }, {
            "input": "foo_2",
            "output": "bar_2"
        }],
        "format": "append_to_user_prompt"
    }
}
```
On Saving
```python
prompt_adapter.save("optimized_prompt/")
```
Saved User Prompt (user_prompt.txt)
```user_prompt.txt
Classify the sentiment of the following review....

**Examples**
Example 1:
Input: foo_1
Output: bar_1

Example 2:
Input: foo_2
Output: bar_2
```
Saved System Prompt (system_prompt.txt)
```system_prompt.txt
You are a review classifier for ABC. Provide a review....
```
