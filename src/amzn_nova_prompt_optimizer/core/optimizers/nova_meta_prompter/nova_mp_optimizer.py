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
import re
import logging

from amzn_nova_prompt_optimizer.core.inference import InferenceAdapter, MAX_TOKENS_FIELD, TEMPERATURE_FIELD, \
    TOP_P_FIELD, TOP_K_FIELD
from amzn_nova_prompt_optimizer.core.input_adapters.dataset_adapter import DatasetAdapter
from amzn_nova_prompt_optimizer.core.input_adapters.metric_adapter import MetricAdapter
from amzn_nova_prompt_optimizer.core.input_adapters.prompt_adapter import (PromptAdapter,
                                                                           PROMPT_VARIABLE_PATTERN,
                                                                           USER_PROMPT_COMPONENT,
                                                                           SYSTEM_PROMPT_COMPONENT,
                                                                           PROMPT_VARIABLES_FIELD)
from amzn_nova_prompt_optimizer.core.optimizers import OptimizationAdapter
from amzn_nova_prompt_optimizer.core.optimizers.nova_meta_prompter.nova_prompt_template import NOVA_PROMPT_TEMPLATE

from typing import Optional, List

logger = logging.getLogger(__name__)
DEFAULT_PROMPTER_MODEL_ID = "us.amazon.nova-premier-v1:0"

class NovaMPOptimizationAdapter(OptimizationAdapter):
    def __init__(self, prompt_adapter: PromptAdapter,
                 inference_adapter: InferenceAdapter,
                 dataset_adapter: Optional[DatasetAdapter] = None,
                 metric_adapter: Optional[MetricAdapter] = None):
        # Call parent class's __init__
        super().__init__(prompt_adapter, inference_adapter, dataset_adapter, metric_adapter)
        self.inference_config = {MAX_TOKENS_FIELD: 5000, TEMPERATURE_FIELD: 1.0, TOP_P_FIELD: 1.0, TOP_K_FIELD: 1}


    def optimize(self, prompter_model_id: str = DEFAULT_PROMPTER_MODEL_ID, max_retries: int = 5):
        logger.info("Optimizing prompt using Nova Meta Prompter")
        if not self.inference_adapter:
            raise ValueError("Inference Adapter not passed. "
                             "Initialize and Pass Inference Adapter to use this Optimizer")

        # Add the User Prompt Variables to the Prompt Template to not drop them
        user_component = self.prompt_adapter.fetch().get(USER_PROMPT_COMPONENT, {})
        user_variables = user_component.get(PROMPT_VARIABLES_FIELD, [])
        user_prompt_variables = ', '.join(f'{{{{{var}}}}}' for var in user_variables)
        nova_prompt_template = NOVA_PROMPT_TEMPLATE.replace("<USER_PROMPT_VARIABLES>", user_prompt_variables)

        # Add the System Prompt Variables to the Prompt Template to not drop them
        system_component = self.prompt_adapter.fetch().get(SYSTEM_PROMPT_COMPONENT, {})
        system_variables = system_component.get(PROMPT_VARIABLES_FIELD, [])
        system_prompt_variables = ', '.join(f'{{{{{var}}}}}' for var in system_variables)
        nova_prompt_template = nova_prompt_template.replace("<SYSTEM_PROMPT_VARIABLES>", system_prompt_variables)

        last_optimized_prompt = None
        all_variables = system_variables + user_variables
        overall_prompt_template = (self.prompt_adapter.fetch_system_template() + "\n\n"
                                + self.prompt_adapter.fetch_user_template())

        messages = [{"user": overall_prompt_template}]
        for attempt in range(max_retries):
            optimized_prompt = self.inference_adapter.call_model(prompter_model_id,
                                                                 nova_prompt_template,
                                                                 messages,
                                                                 self.inference_config)
            last_optimized_prompt = optimized_prompt
            system_prompt, user_prompt = self._split_prompt(optimized_prompt)
            if (self._validate_system_prompt(system_prompt, all_variables)
                    and self._validate_user_prompt(user_prompt, all_variables)):
                return self._create_optimized_prompt_adapter(system_prompt, user_prompt, all_variables)
            logger.warning(f"Attempt {attempt + 1}: Optimized prompt does not contain all variables. Retrying...")
        logger.warning("Failed to generate a valid optimized prompt after maximum retries. "
                       "Using last generated prompt and appending variables to the end")

        if not last_optimized_prompt:
            raise ValueError("[Optimization Error] Failure in optimization, please re-run the optimizer.")

        system_prompt, user_prompt = self._split_prompt(last_optimized_prompt)
        user_prompt = self._format_prompt_with_variables(user_prompt, all_variables)
        return self._create_optimized_prompt_adapter(system_prompt, user_prompt, all_variables)

    def _create_optimized_prompt_adapter(self, system_prompt: str, user_prompt: str, all_variables: List[str]) -> PromptAdapter:
        optimized_prompt_adapter = self.prompt_adapter.__class__()
        optimized_prompt_adapter.set_system_prompt(content=system_prompt)
        optimized_prompt_adapter.set_user_prompt(content=user_prompt, variables=set(all_variables))
        optimized_prompt_adapter.adapt()
        return optimized_prompt_adapter

    @staticmethod
    def _split_prompt(prompt: str):
        """
        Split the overall prompt into system prompt and user prompt based on tags
        :param prompt: Overall prompt
        :return: System Prompt, and User Prompt
        """
        try:
            system_pattern = r"<system_prompt>(.*?)</system_prompt>"
            user_pattern = r"<user_prompt>(.*?)</user_prompt>"

            system_match = re.search(system_pattern, prompt, re.DOTALL)
            user_match = re.search(user_pattern, prompt, re.DOTALL)

            if not system_match or not user_match:
                return None, None

            return system_match.group(1).strip(), user_match.group(1).strip()

        except Exception as e:
            logger.warn("Error extracting prompts, re-trying....")
            return None, None


    @staticmethod
    def _validate_user_prompt(prompt: str, variables: List[str]) -> bool:
        """
        Validate that all variables are present in the optimized prompt.
        :param prompt: Prompt to validate
        :return: True if prompt contains ALL prompt variables, else False
        """
        if prompt is None:  # Only None is invalid
            return False

        if not variables:  # If no variables to check, prompt is valid
            return True
        used_vars = set(PROMPT_VARIABLE_PATTERN.findall(prompt))
        return used_vars.issuperset(set(variables))

    @staticmethod
    def _validate_system_prompt(prompt: str, variables: List[str]) -> bool:
        """
        Validate that all variables are not present in the optimized system prompt.
        :param prompt: Prompt to validate
        :return: True if prompt contains ALL prompt variables, else False
        """
        if prompt is None:  # Only None is invalid
            return False

        if not variables:  # If no variables to check, prompt is valid
            return True
        used_vars = set(PROMPT_VARIABLE_PATTERN.findall(prompt))
        return not used_vars.issuperset(set(variables))

    @staticmethod
    def _format_prompt_with_variables(prompt: str, variables: List[str]) -> str:
        """
        Formats the prompt by appending the variables in the end.
        :param prompt: Prompt to format
        :return: formatted prompt
        """
        used_vars = set(PROMPT_VARIABLE_PATTERN.findall(prompt))
        missing_vars = set(variables) - used_vars
        # Append missing variables
        if missing_vars:
            prompt += "\n\nHere are the additional inputs:\n"
            prompt += "\n".join(f"[[ ## {var} ## ]]\n{{{{{var}}}}}\n" for var in missing_vars)
        return prompt
