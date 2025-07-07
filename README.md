# Nova Prompt Optimizer

A Python SDK for optimizing prompts for Nova.

## Table of contents
* [Installation](#installation)
* [Quick Start: Facility Support Analyzer Dataset](#quick-start)
* [Optimization Recommendations](#set-up)
* [Core Concepts](#core-concepts)
  * [Input Adapters](#input-adapters)
    * [1. Dataset Adapter](#1-dataset-adapter)
    * [2. Prompt Adapter](#2-prompt-adapter)
    * [3. Metric Adapter](#3-metric-adapter)
    * [4. Inference Adapter](#4-inference-adapter)
    * [5. Optimization Adapter](#5-optimization-adapter)
  * [Optimizers](#optimizers)
    * [NovaPromptOptimizer](#novapromptoptimizer)
    * [Other Optimizers](#other-optimizers)
      * [1.Nova Meta Prompter](#nova-meta-prompter)
      * [2. DSPy's MIPROv2 Optimizer](#miprov2)
  * [Evaluator](#evaluator)
* [Acknowledgements](#acknowledgements)

## Installation

Install the library using
```sh
pip install amzn-nova-prompt-optimizer
```

## Quick Start
### Facility Support Analyzer Dataset
The Facility Support Analyzer dataset consists of emails that are to be classified based on category, urgency and sentiment.

Please see the [samples](samples/facility-support-analyzer/) folder for example notebooks of how to optimize a prompt in the scenario where a [user prompt template is to be optimized](samples/facility-support-analyzer/user_prompt_only) and the scenario where a [user and system prompt is to be optimized together](samples/facility-support-analyzer/system_and_user_prompt)


## Optimization Recommendations
1. Provide representative real-world evaluation sets and split them into training and testing sets. Ensure dataset is balanced on output label when splitting train and test sets.
2. For evaluation sets, the ground truth column should be as close to the inference output as possible. e.g. If the inference output is {"answer": "POSITIVE"} ground truth should also be in the same format {"answer": "POSITIVE"}
3. For NovaPromptOptimizer, choose the mode (mode= "premier" | ""pro" | "lite" | "micro") based on your model class. By default, we use "pro".
4. The `apply` function of the evaluation metric should return a numerical value between 0 and 1 for NovaPromptOptimizer or MIPROv2.


## Core Concepts
### Input Adapters
### 1. Dataset Adapter

**Responsibility:** Ability to read/write datasets from different formats. Uses an intermediary standardized format when communicating with other adapters. 
It can also read list of JSON object. It can also create Train/Test splits (with stratify capability if set).

**Requirements:** Currently, you can only provide a singleton set as output column. 

**Core Functions**
```commandline
# Adapt to the Standardized Format (JSON)
.adapt()

# Prints the datasets first 10 rows to view
.show()

# Fetches the dataset as a List of JSON in standardized format
.fetch()

# Splits the dataset based on provided percentage (0 to 1). Stratifies if Set.
.split(split_percentage: float, stratify: bool = False)
```

**Standardized Data Format**

```python
{
    "inputs": {
        "prompt_var_key_1": "foo",
        "prompt_var_key_2": "bar",
        ....
            "model_input": "model input"
},
"outputs": {
    "ground_truth": "ground_truth"
}
}

# Example

## JSONL Input
row = {"product_type": "foo", "conversation_history": "bar", "question": "what's the...", "answer": "the..", "ground_truth": "{\"score\": \"4\", \"sentiment\": \"POSITIVE\"}"}

.adapt(row)

## Standardized Data
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

**Sample Dataset Adapter Initialization**
```python
# Example Usage
from amzn_nova_prompt_optimizer.core.input_adapters.dataset_adapter import JSONDatasetAdapter

input_columns = {"input"}
output_columns = {"answer"}

dataset_adapter = JSONDatasetAdapter(input_columns, output_columns)

# Adapt
dataset_adapter.adapt(data_source="sample_data.jsonl")

# Split
train, test = dataset_adapter.split(0.5)
```

**Supported Dataset Adapters:** `JSONDatasetAdapter`, `CSVDatasetAdapter`

### 2. Prompt Adapter

**Responsibility:** Ability to load prompts from different formats and store them in the standardized format (JSON)

**Core Functions**
```commandline
# Set the System Prompt for the Adapter
.set_system_prompt(data_source=, variables=)

# Set the User Prompt for the Adapter
.set_user_prompt(data_source=, variables=)

# (Optional) Add few shot examples
.add_few_shot(examples=, format_type="converse"|"append_to_user_prompt"|"append_to_system_prompt")

# Adapt prompt to Standardized Format
.adapt()

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

```python
.set_system_prompt(file_path="system_prompt.txt", variables={})

.set_user_prompt(file_path="user_prompt.txt", variables={"review"})

.adapt()
```

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


**Sample Prompt Adapter Initialization**

```python
from amzn_nova_prompt_optimizer.core.input_adapters.prompt_adapter import TextPromptAdapter

prompt_adapter = TextPromptAdapter()

prompt_adapter.set_system_prompt(file_path="prompt/sys_prompt.txt", variables={"foo"})

prompt_adapter.set_user_prompt(content="You are a .....", variables={"bar"})

prompt_adapter.adapt()
```

**Supported Prompt Adapters:** `TextPromptAdapter`

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

```user_prompt.txt
Classify the sentiment of the following review....
```
```system_prompt.txt
You are a review classifier for ABC. Provide a review....
```

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
```system_prompt.txt
You are a review classifier for ABC. Provide a review....
```

### 3. Metric Adapter
**Responsibility:** Ability to load custom metrics and apply them on inference output and ground truth

**Core Functions**
```commandline
# Apply the metric on a prediction and ground_truth
.apply(y_pred: Any, y_true: Any)

# Apply the metric on a list of prediction and ground_truth
.batch_apply(y_preds: List[Any], y_trues: List[Any])
```

**Sample Custom Metric Adapter Initialization**

```python
from amzn_nova_prompt_optimizer.core.input_adapters.metric_adapter import MetricAdapter
from typing import List, Any, Dict
import re
import json

class CustomMetric(MetricAdapter):
    def _parse_answer(self, model_output):
        match = re.search(r"<answer>(.*?)</answer>", model_output)
        if not match:
            return "Choice not found"
        return match.group(1).lower().strip()

    def _calculate_metrics(self, y_pred: Any, y_true: Any) -> Dict:
        pred = self._parse_answer(y_pred)
        ground_truth = self._parse_answer(y_true)
        return int(pred == ground_truth)

    def apply(self, y_pred: Any, y_true: Any):
        return self._calculate_metrics(y_pred, y_true)

    def batch_apply(self, y_preds: List[Any], y_trues: List[Any]):
        evals = []
        for y_pred, y_true in zip(y_preds, y_trues):
            evals.append(self.apply(y_pred, y_true))
        return sum(evals)/len(evals)

metric_adapter = CustomMetric()
```

### 4. Inference Adapter
**Responsibility:** Ability to call an inference backend for the models e.g. Bedrock, etc.

**Core Functions**
```commandline
# Call the model with the passed parametrs
.call_model(model_id: str, system_prompt: str, messages: List[Dict[str, str]], inf_config: Dict[str, Any])

```

The Inference Adapter accepts the `system_prompt` as a string and the input to the model as a list of User/Assistant 
turns. e.g. `[{"user": "foo"}, {"assistant": "bar"}, {"user": "What comes next?"}]`

**Sample use of Inference Adapter**

```python
from amzn_nova_prompt_optimizer.core.inference.adapter import BedrockInferenceAdapter

inference_adapter = BedrockInferenceAdapter(region_name="us-east-1")
```

**Supported Inference Adapters:** `BedrockInferenceAdapter`

### 5. Optimization Adapter
**Responsibility:** Load Optimizer, Prompt Adapter, and Optionally Dataset Adapter, Metric Adapter, and Inference Adapter. Perform Optimization and ability to create a Prompt Adapter with the Optimized Prompt.

**Core Functions**
```commandline
# Optimize and return a PromptAdapter
.optimize() -> PromptAdapter
```

## Optimizers

### NovaPromptOptimizer

NovaPromptOptimizer is a combination of Meta Prompting using the Nova Guide on prompting and DSPy's MIPROv2 Optimizer using Nova Prompting Tips. 
NovaPromptOptimizer first runs a meta prompter to identify system instructions and user template from the prompt adapter. 
Then MIPROv2 is run on top of this to optimize system instructions and identify few-shot samples that need to be added. 
The few shot samples are added as `converse` format so they are added as User/Assistant turns.

**Requirements:** NovaPromptOptimizer requires Prompt Adapter, Dataset Adapter, Metric Adapter and Inference Adapter.

**Optimization Example**
```python
from amzn_nova_prompt_optimizer.core.optimizers import NovaPromptOptimizer

nova_prompt_optimizer = NovaPromptOptimizer(prompt_adapter=prompt_adapter, inference_adapter=inference_adapter, dataset_adapter=train_dataset_adapter, metric_adapter=metric_adapter)

optimized_prompt_adapter = nova_prompt_optimizer.optimize(mode="lite")
```
NovaPromptOptimizer uses Premier for Meta Prompting and then uses MIPROv2 with 20 candidates and 50 trials with Premier as Prompting model and task model dependent on the mode it's set at.
You can specify enable_json_fallback=False to disable the behavior that MIPROv2 will [fallback to use JSONAdapter to parse LM model output](https://github.com/stanfordnlp/dspy/blob/main/dspy/adapters/chat_adapter.py#L44-L51). This will force MIPROv2 use structured output (pydantic model) to parse LM output.

You could also define a custom mode and pass your own parameter values to NovaPromptOptimizer

```python
from amzn_nova_prompt_optimizer.core.optimizers import NovaPromptOptimizer

nova_prompt_optimizer = NovaPromptOptimizer(prompt_adapter=prompt_adapter, inference_adapter=inference_adapter, dataset_adapter=train_dataset_adapter, metric_adapter=metric_adapter)

optimized_prompt_adapter = nova_prompt_optimizer.optimize(mode="custom", custom_params={"task_model_id": "us.amazon.nova-pro-v1:0",
    "num_candidates": 10,
    "num_trials": 15,
    "max_bootstrapped_demos": 5,
    "max_labeled_demos": 0
})
```

#### Other Optimizers
#### Nova Meta Prompter

Nova Meta Prompter performs Meta Prompting using the [Nova Guide on prompting](https://docs.aws.amazon.com/nova/latest/userguide/prompting-precision.html). 
Nova Meta Prompter identifies system instructions and user template from the prompt adapter.

**Requirements:** Nova Meta Prompter requires Prompt Adapter and Inference Adapter.

**Optimization Example**
```python
from amzn_nova_prompt_optimizer.core.optimizers import NovaMPOptimizationAdapter

nova_mp_optimization_adapter = NovaMPOptimizationAdapter(prompt_adapter=prompt_adapter, inference_adapter=inference_adapter)

nova_mp_optimized_prompt_adapter = nova_mp_optimization_adapter.optimize(max_retries=5)
```
Nova Meta Prompter uses Premier for Meta Prompting. Max Retries to retry optimization if optimized prompts do not contain prompt variables.

#### MIPROv2

MIPROv2 (Multiprompt Instruction PRoposal Optimizer Version 2) [Provided by DSPy Library](https://github.com/stanfordnlp/dspy): 

MIPROv2 is a prompt optimizer capable of optimizing both instructions and few-shot examples jointly. It does this by bootstrapping few-shot example candidates, proposing instructions grounded in different dynamics of the task, and finding an optimized combination of these options using Bayesian Optimization. It can be used for optimizing few-shot examples & instructions jointly, or just instructions for 0-shot optimization. 

1. Step 1: Generate a good set of demos to show what the ideal input output pairs look like. 
2. Step 2: Generate a good set of instructions(or prompts) that will likely generate the ideal input output pairs. 
3. Step 3: Run a Bayesian Optimization algorithm to figure out the best instruction - demo pair that can be used to generate the most ideal prompt.

**Requirements:** MIPROv2 requires Prompt Adapter, Dataset Adapter, Inference Adapter, and Metric Adapter.

**Optimization Example**
```python
from amzn_nova_prompt_optimizer.core.optimizers.miprov2.miprov2_optimizer import MIPROv2OptimizationAdapter

mipro_optimization_adapter = MIPROv2OptimizationAdapter(prompt_adapter=prompt_adapter, dataset_adapter=train_dataset_adapter, metric_adapter=metric_adapter)

mipro_prompt_adapter = mipro_optimization_adapter.optimize(task_model_id="us.amazon.nova-lite-v1:0",
                                                           prompter_model_id ="us.amazon.nova-premier-v1:0", 
                                                           num_candidates=None, 
                                                           num_threads= 2,
                                                           num_trials=None,
                                                           max_bootstrapped_demos = 4,
                                                           max_labeled_demos = 4,
                                                           minibatch_size = 35,
                                                           train_split = 0.5,
                                                           enable_json_fallback = False)
```

MIPROv2 uses Premier for Prompting and the task model provided as `task_model_id`. 
By default, it uses "medium" optimization i.e. Generating 6 instruction candidates and num_trials proportional to it 

You can specify enable_json_fallback=False to disable the behavior that MIPROv2 will [fallback to use JSONAdapter to parse LM model output](https://github.com/stanfordnlp/dspy/blob/main/dspy/adapters/chat_adapter.py#L44-L51). This will force MIPROv2 use structured output (pydantic model) to parse LM output.

MIPROv2's inference output is in a structured format and requires parsing prior to running evaluation.

The output can be found between tokens `[[ ## output_var_name ## ]]` and `[[ ## completed ## ]]`. 
Hence, if your output variable is `answer` then the inference output can be found between tokens `[[ ## answer ## ]]` and `[[ ## completed ## ]]`


## Evaluator
The SDK also provides a way to baseline prompts and provide evaluation scores.
The evaluator has the `aggregate_score` and `scores` function.

**Core Functions**
```commandline
# Runs Batch evaluation on the dataset using the batch_apply function of the metric
.aggregate_score(model_id)

# Runs evaluation on the dataset a row at a time and returns the eval results as a whole.
.score(model_id)

# Save the eval results
.save()
```

**Initialization Example**
```python
from amzn_nova_prompt_optimizer.core.evaluation import Evaluator

evaluator = Evaluator(nova_mp_optimized_prompt_adapter, test_dataset_adapter, metric_adapter, inference_adapter)

nova_mp_score = evaluator.aggregate_score(model_id="us.amazon.nova-lite-v1:0")
```

**Note: You may come across the below warning. This is when prompt variables are missing from the prompt, the inference runner under the evaluator appends them to the end of the prompt for continuity**
```python
WARNING amzn_nova_prompt_optimizer.core.inference: Warn: Prompt Variables not found in User Prompt, injecting them at the end of the prompt
```

## Acknowledgements
* Special acknowledgment to [DSPy](https://github.com/stanfordnlp/dspy) – your innovations continue to inspire us.