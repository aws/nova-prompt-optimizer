# Copyright 2025 Amazon Inc

# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
import logging

from amzn_nova_prompt_optimizer.core.inference.adapter import InferenceAdapter
from amzn_nova_prompt_optimizer.core.inference.inference_constants import (
    MAX_TOKENS_FIELD, TEMPERATURE_FIELD, TOP_P_FIELD, TOP_K_FIELD
)
from amzn_nova_prompt_optimizer.core.input_adapters.dataset_adapter import DatasetAdapter
from amzn_nova_prompt_optimizer.core.input_adapters.prompt_adapter import (
    PromptAdapter,
    PROMPT_VARIABLE_PATTERN,
    SYSTEM_PROMPT_COMPONENT,
    USER_PROMPT_COMPONENT,
    PROMPT_TEMPLATE_FIELD,
    FEW_SHOT_COMPONENT,
    FEW_SHOT_EXAMPLES_FIELD,
    FEW_SHOT_FORMAT_FIELD,
    CONVERSE_FEW_SHOT_FORMAT,
    PROMPT_VARIABLES_FIELD,
    APPEND_TO_USER_PROMPT_FEW_SHOT_FORMAT,
    APPEND_TO_SYSTEM_PROMPT_FEW_SHOT_FORMAT
)

from typing import List, Dict, Any
from concurrent.futures import ThreadPoolExecutor, as_completed
from tqdm import tqdm

logger = logging.getLogger(__name__)

INFERENCE_OUTPUT_FIELD = "inference_output"

class InferenceRunner:
    def __init__(self, prompt_adapter: PromptAdapter,
                 dataset_adapter: DatasetAdapter,
                 inference_adapter: InferenceAdapter):
        self.max_workers: int = 4
        self.model_id: str = ""
        self.inf_config: Dict[str, Any] = {}
        self.prompt_adapter: PromptAdapter = prompt_adapter
        self.dataset_adapter: DatasetAdapter = dataset_adapter
        self.inference_adapter: InferenceAdapter = inference_adapter
        self.inference_results: List[Dict] = []
        self.warned_user_on_missing_prompt_variables = False

    def _format_template(self, template: str, variables: List[str], inputs: Dict[str, Any]) -> str:
        """Format a single template with its variables"""
        template_vars = {var: str(inputs.get(var, '')) for var in variables}

        def replace_variable(match):
            var = match.group(1)
            return template_vars.get(var, match.group(0))

        formatted_prompt = PROMPT_VARIABLE_PATTERN.sub(replace_variable, template)

        # Check for unused variables
        used_vars = set(PROMPT_VARIABLE_PATTERN.findall(template))
        unused_vars = set(template_vars.keys()) - used_vars

        if unused_vars:
            formatted_prompt += "\n\nHere are the additional inputs:\n"
            formatted_prompt += "\n".join(f"[[ ## {var} ## ]]\n{template_vars[var]}\n" for var in unused_vars)
            if not self.warned_user_on_missing_prompt_variables:
                logger.warning("Warn: Some prompt variables were not found in the template "
                               "and have been appended at the end.")
                self.warned_user_on_missing_prompt_variables = True

        return formatted_prompt

    def _create_messages(self, standardized_prompt: Dict[str, Any],
                         inputs: Dict[str, Any]) -> tuple[str, List[Dict[str, str]]]:
        """Create system prompt string and conversation messages"""
        messages = []

        # Get few-shot component
        few_shot = standardized_prompt.get(FEW_SHOT_COMPONENT, {})
        few_shot_examples = few_shot.get(FEW_SHOT_EXAMPLES_FIELD, [])
        few_shot_format = few_shot.get(FEW_SHOT_FORMAT_FIELD)

        # Format few-shot examples text if needed for appending
        few_shot_text = ""
        if few_shot_examples and few_shot_format in [APPEND_TO_USER_PROMPT_FEW_SHOT_FORMAT,
                                                     APPEND_TO_SYSTEM_PROMPT_FEW_SHOT_FORMAT]:
            few_shot_text = "\n\n**Examples**\n"
            for i, example in enumerate(few_shot_examples, 1):
                few_shot_text += f"\nExample {i}:\nInput: {example['input']}\nOutput: {example['output']}\n"

        # Handle system prompt
        system_component = standardized_prompt.get(SYSTEM_PROMPT_COMPONENT, {})
        system_template = system_component.get(PROMPT_TEMPLATE_FIELD, "")
        system_prompt = system_template

        if system_template.strip():
            system_variables = system_component.get(PROMPT_VARIABLES_FIELD, [])
            system_prompt = self._format_template(system_template, system_variables, inputs)

        # Append few-shot examples to system prompt if specified
        if few_shot_format == APPEND_TO_SYSTEM_PROMPT_FEW_SHOT_FORMAT:
            system_prompt = f"{system_prompt}{few_shot_text}"

        # Handle few-shot examples in conversation format
        if few_shot_format == CONVERSE_FEW_SHOT_FORMAT:
            for example in few_shot_examples:
                messages.append({"user": example["input"]})
                messages.append({"assistant": example["output"]})

        # Handle user prompt
        user_component = standardized_prompt.get(USER_PROMPT_COMPONENT, {})
        user_template = user_component.get(PROMPT_TEMPLATE_FIELD)
        if user_template and user_template.strip():
            user_variables = user_component.get(PROMPT_VARIABLES_FIELD, [])
            formatted_user = self._format_template(user_template, user_variables, inputs)

            # Append few-shot examples to user prompt if specified
            if few_shot_format == APPEND_TO_USER_PROMPT_FEW_SHOT_FORMAT:
                formatted_user = f"{formatted_user}{few_shot_text}"

            if formatted_user:
                messages.append({"user": formatted_user})

        return system_prompt, messages

    def _infer_row(self, row):
        """Process a single row for inference"""
        try:
            standardized_prompt = self.prompt_adapter.fetch()
            system_prompt, messages = self._create_messages(standardized_prompt, row['inputs'])

            if not messages:
                raise ValueError("No messages generated for inference")

            model_output = self.inference_adapter.call_model(
                model_id=self.model_id,
                system_prompt=system_prompt,
                messages=messages,
                inf_config=self.inf_config
            )

            row[INFERENCE_OUTPUT_FIELD] = model_output
            return row
        except Exception as e:
            logger.error(f"Error processing row: {e}")
            raise

    def run(self, model_id: str, max_tokens: int = 5000, temperature: float = 0,
            top_p: float = 1, top_k: int = 1, max_workers: int = 4):
        """Run inference on the dataset"""
        self.inference_results = [] # Make sure inference results are cleaned before each run
        self.model_id = model_id
        self.max_workers = max_workers
        self.inf_config = {
            MAX_TOKENS_FIELD: max_tokens,
            TEMPERATURE_FIELD: temperature,
            TOP_P_FIELD: top_p,
            TOP_K_FIELD: top_k
        }
        dataset = self.dataset_adapter.fetch()
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            future_to_row = {
                executor.submit(self._infer_row, row): row
                for row in dataset
            }

            # Collect results as they complete
            for future in tqdm(as_completed(future_to_row), total=len(future_to_row), desc="Running inference"):
                try:
                    result = future.result()
                    self.inference_results.append(result)
                except Exception as e:
                    logger.error(f"Error during inference: {e}")
        return self.inference_results
