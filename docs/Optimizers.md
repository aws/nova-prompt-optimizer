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

### Other Optimizers

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

