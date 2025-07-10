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
import os
import textwrap
from typing import Type, Optional, List, Dict

import dspy  # type: ignore
from dspy.teleprompt import MIPROv2  # type: ignore
from dspy.adapters.chat_adapter import ChatAdapter # type: ignore

from amzn_nova_prompt_optimizer.core.input_adapters.dataset_adapter import DatasetAdapter
from amzn_nova_prompt_optimizer.core.input_adapters.prompt_adapter import (PromptAdapter,
                                                                           USER_PROMPT_COMPONENT,
                                                                           PROMPT_VARIABLES_FIELD,
                                                                           CONVERSE_FEW_SHOT_FORMAT,
                                                                           PROMPT_VARIABLE_PATTERN)
from amzn_nova_prompt_optimizer.core.optimizers import OptimizationAdapter
from amzn_nova_prompt_optimizer.core.optimizers.miprov2.custom_lm.rate_limited_lm import RateLimitedLM
from amzn_nova_prompt_optimizer.core.optimizers.nova_prompt_optimizer.nova_grounded_proposer import NovaGroundedProposer
from amzn_nova_prompt_optimizer.core.optimizers.miprov2.custom_adapters.custom_chat_adapter import CustomChatAdapter

DEFAULT_TASK_MODEL = "us.amazon.nova-pro-v1:0"
DEFAULT_PROMPT_MODEL = "us.amazon.nova-premier-v1:0"

logger = logging.getLogger(__name__)


class PredictorFactory:
    """Factory class to create DSPy predictors based on DatasetAdapter configuration"""

    @staticmethod
    def create_signature(dataset_adapter: DatasetAdapter) -> Type[dspy.Signature]:
        """
        Creates a DSPy Signature class dynamically based on dataset adapter's input and output columns

        :param dataset_adapter: The dataset adapter containing input/output specifications
        :return: A DSPy Signature class
        """
        # Create class attributes dictionary
        attrs = {
            # Add input fields
            **{col: dspy.InputField() for col in dataset_adapter.input_columns},
            # Add output fields
            **{col: dspy.OutputField() for col in dataset_adapter.output_columns}
        }

        # Create the signature class dynamically
        return type('DynamicSignature', (dspy.Signature,), attrs)

    @staticmethod
    def create_predictor(
            dataset_adapter: DatasetAdapter,
            prompt: str,
            temperature: float = 1.0,
            signature_class: Optional[Type[dspy.Signature]] = None
    ) -> dspy.Predict:
        """
        Creates a DSPy Predict module based on dataset adapter and prompt

        :param dataset_adapter: The dataset adapter containing input/output specifications
        :param prompt: The prompt template to use
        :param temperature: Temperature for the predictor
        :param signature_class: Optional custom signature class
        :return: A configured DSPy Predict module
        """
        # Create or use signature class
        SignatureClass = signature_class or PredictorFactory.create_signature(dataset_adapter)

        # Create predictor
        predictor = dspy.Predict(SignatureClass)
        predictor.temperature = temperature
        predictor.signature.instructions = prompt

        return predictor


class MIPROv2OptimizationAdapter(OptimizationAdapter):
    def _process_dataset_adapter(self, train_split):
        if self.dataset_adapter is None:
            raise ValueError("dataset_adapter is required for MIPROv2 optimization")
        # Create DSPy examples
        dspy_examples = []
        for item in self.dataset_adapter.fetch():
            example = dspy.Example(
                **item['inputs'],
                **item['outputs']
            ).with_inputs(*item['inputs'].keys())
            dspy_examples.append(example)

        # Split into train and test
        train_size = int(len(dspy_examples) * train_split)
        train_data = dspy_examples[:train_size]
        test_data = dspy_examples[train_size:]

        return train_data, test_data

    def _construct_optimized_system_prompt(self, optimized_mipro_sys_prompt):
        input_columns = self.dataset_adapter.input_columns
        output_columns = self.dataset_adapter.output_columns
        optimized_system_prompt = []

        prompt_lines = ["Your input fields are:"]
        prompt_lines += [f"{i + 1}. {col}" for i, col in enumerate(input_columns)]

        prompt_lines.append("Your output fields are:")
        prompt_lines += [f"{i + 1}. {col}" for i, col in enumerate(output_columns)]

        prompt_lines.append("")
        prompt_lines.append("All interactions will be structured in the following way, with the appropriate values filled in.")
        for col in input_columns:
            prompt_lines.append(f"[[ ## {col} ## ]]")
            prompt_lines.append(col)
        for col in output_columns:
            prompt_lines.append(f"[[ ## {col} ## ]]")
            prompt_lines.append(col)
        prompt_lines.append("")
        prompt_lines.append("[[ ## completed ## ]]")
        prompt_lines.append("")
        optimized_system_prompt.extend(prompt_lines)

        instructions = textwrap.dedent(optimized_mipro_sys_prompt)
        objective = ("\n" + " " * 8).join([""] + instructions.splitlines())

        optimized_system_prompt.append(f"In adhering to this structure, your objective is: {objective}")
        final_system_prompt = "\n".join(optimized_system_prompt)
        return final_system_prompt

    def _construct_optimized_user_prompt(self):
        user_component = self.prompt_adapter.fetch().get(USER_PROMPT_COMPONENT, {})
        output_columns = self.dataset_adapter.output_columns
        user_prompt = []
        if user_component:
            user_variables = user_component.get(PROMPT_VARIABLES_FIELD, [])
            # Create User Prompt as MIPROv2 Format
            for var in user_variables:
                user_prompt.append(f"[[ ## {var} ## ]]")
                user_prompt.append(f"{{{{ {var} }}}}")
            user_prompt.append("")
            suffix = "Respond with the corresponding output fields, starting with the field "
            suffix += ", then ".join(f"[[ ## {col} ## ]]" for col in output_columns)
            suffix += ", and then ending with the marker for [[ ## completed ## ]]."
            user_prompt.append(suffix)
            final_user_prompt = "\n".join(user_prompt)
            return final_user_prompt, user_variables

        return None, None

    def _create_few_shot_samples(self, optimized_predictor: dspy.Predict) -> tuple[List[Dict[str, str]], str]:
        if self.dataset_adapter is None:
            raise ValueError("dataset_adapter is required for MIPROv2 optimization")
        input_fields = list(self.dataset_adapter.input_columns)
        output_fields = list(self.dataset_adapter.output_columns)
        few_shot_samples = []
        # Create examples as User/Assistant Turns
        for idx, example in enumerate(optimized_predictor.demos, 1):
            input_message = ""
            output_message = ""
            for field in input_fields:
                input_message += f"[[ ## {field} ## ]]\n{example[field]}\n"
            for field in output_fields:
                output_message += f"[[ ## {field} ## ]]\n{example[field]}\n"
            few_shot_samples.append({"input": input_message, "output": output_message})
        return few_shot_samples, CONVERSE_FEW_SHOT_FORMAT

    def _create_optimized_prompt_adapter(self, optimized_predictor: dspy.Predict) -> PromptAdapter:
        optimized_prompt_adapter = self.prompt_adapter.__class__()
        system_prompt = self._construct_optimized_system_prompt(optimized_predictor.signature.instructions)
        optimized_prompt_adapter.set_system_prompt(content=system_prompt)
        user_prompt, user_prompt_variables = self._construct_optimized_user_prompt()
        if user_prompt and user_prompt_variables:
            optimized_prompt_adapter.set_user_prompt(content=user_prompt, variables=user_prompt_variables)
        few_shot_samples, format_type = self._create_few_shot_samples(optimized_predictor)
        optimized_prompt_adapter.add_few_shot(examples=few_shot_samples, format_type=format_type)
        optimized_prompt_adapter.adapt()
        return optimized_prompt_adapter

    def _create_predictor(self, prompt: str) -> dspy.Predict:
        """
        Creates a DSPy predictor based on the dataset adapter and prompt adapter
        """
        if self.dataset_adapter is None:
            raise ValueError("dataset_adapter is required for MIPROv2 optimization")
        return PredictorFactory.create_predictor(
            dataset_adapter=self.dataset_adapter,
            # Append both System and User Prompt for MIPROv2 Optimization
            prompt=prompt
        )

    def _dspy_metric(self, gold: dspy.Example, pred: dspy.Prediction, trace=None) -> float:
        """Wrapper for the metric adapter to work with DSPy's output"""
        if self.dataset_adapter is None:
            raise ValueError("dataset_adapter is required for MIPROv2 optimization")

        if self.metric_adapter is None:
            raise ValueError("metric_adapter is required for MIPROv2 optimization")

        # Assuming the output field is the first (and only) output field
        output_field = list(self.dataset_adapter.output_columns)[0]

        y_pred = getattr(pred, output_field)
        y_true = getattr(gold, output_field)

        return self.metric_adapter.apply(y_pred, y_true)

    def optimize(self,
                 task_model_id: str = DEFAULT_TASK_MODEL,
                 prompter_model_id: str = DEFAULT_PROMPT_MODEL,
                 num_candidates: Optional[int] = None,
                 num_threads: int = 2,
                 num_trials: Optional[int] = None,
                 max_bootstrapped_demos: int = 4,
                 max_labeled_demos: int = 4,
                 minibatch_size: int = 35,
                 train_split: float = 0.5, # Default to 50% Split
                 enable_json_fallback: bool = True) -> PromptAdapter:

        if self.dataset_adapter is None:
            raise ValueError("dataset_adapter is required for MIPROv2 optimization")

        if self.metric_adapter is None:
            raise ValueError("metric_adapter is required for MIPROv2 optimization")

        if self.inference_adapter is None:
            raise ValueError("inference_adapter is required for MIPROv2 optimization")

        auto_setting = None
        if num_candidates is None and num_trials is None:
            auto_setting = "medium"
            logger.info("Both num_candidates and num_trials are None. Defaulting to MIPROv2 Medium optimization")
        elif num_candidates is None:
            raise ValueError("num_candidates must be specified when num_trials is provided")
        elif num_trials is None:
            raise ValueError("num_trials must be specified when num_candidates is provided")

        # Set AWS region
        if self.inference_adapter.region:
            os.environ["AWS_REGION_NAME"] = self.inference_adapter.region
        else:
            os.environ["AWS_REGION_NAME"] = 'us-west-2'

        # Setup dspy.LM
        task_lm = RateLimitedLM(dspy.LM(f'bedrock/{task_model_id}'), rate_limit=self.inference_adapter.rate_limit)
        logger.info(f"Using {task_model_id} for Evaluation")
        prompt_lm = RateLimitedLM(dspy.LM(f'bedrock/{prompter_model_id}'), rate_limit=self.inference_adapter.rate_limit)
        logger.info(f"Using {prompter_model_id} for Prompting")

        # Configure DSPy
        dspy.configure(lm=task_lm)

        # Create a predictor
        prompt = self.prompt_adapter.fetch_system_template() + "\n\n" + self.prompt_adapter.fetch_user_template()
        initial_predictor = self._create_predictor(prompt)

        # Prepare the dataset
        train_data, test_data = self._process_dataset_adapter(train_split)

        minibatch_size = min(len(test_data), minibatch_size)

        # Define the optimizer
        optimizer = MIPROv2(
            metric=self._dspy_metric,
            auto=auto_setting,
            prompt_model=prompt_lm,
            task_model=task_lm,
            num_candidates=num_candidates,
            num_threads=num_threads
        )

        # Run the optimization
        optimized_predictor = optimizer.compile(
            initial_predictor,
            trainset=train_data,
            num_trials=num_trials,
            valset=test_data,
            minibatch_size=minibatch_size,
            max_bootstrapped_demos=max_bootstrapped_demos,
            max_labeled_demos=max_labeled_demos,
            provide_traceback=True,
            requires_permission_to_run=False
        )

        # Create a new PromptAdapter with the optimized prompt
        return self._create_optimized_prompt_adapter(optimized_predictor)

class NovaMIPROv2OptimizationAdapter(MIPROv2OptimizationAdapter):
    def _create_few_shot_samples_with_prompt(self, optimized_predictor: dspy.Predict,
                                 user_prompt: str, user_variables: set) -> tuple[List[Dict[str, str]], str]:
        if self.dataset_adapter is None:
            raise ValueError("dataset_adapter is required for MIPROv2 optimization")
        input_fields = user_variables
        output_fields = list(self.dataset_adapter.output_columns)
        few_shot_samples = []
        # Create examples as User/Assistant Turns
        for idx, example in enumerate(optimized_predictor.demos, 1):
            output_message = ""
            template_vars = {var: str(example.get(var, "")) for var in input_fields}

            def replace_variable(match):
                var = match.group(1)
                return template_vars.get(var, match.group(0))  # Keep as-is if not found

            # Replace variables in the user prompt template
            input_message = PROMPT_VARIABLE_PATTERN.sub(replace_variable, user_prompt)
            for field in output_fields:
                output_message += f"{example[field]}"
            few_shot_samples.append({"input": input_message, "output": output_message})
        return few_shot_samples, CONVERSE_FEW_SHOT_FORMAT

    def _create_optimized_prompt_adapter(self, optimized_predictor: dspy.Predict) -> PromptAdapter:
        optimized_prompt_adapter = self.prompt_adapter.__class__()
        system_prompt = optimized_predictor.signature.instructions
        optimized_prompt_adapter.set_system_prompt(content=system_prompt)

        user_component = self.prompt_adapter.fetch().get(USER_PROMPT_COMPONENT, {})
        user_prompt = self.prompt_adapter.fetch_user_template()
        if user_component:
            user_variables = user_component.get(PROMPT_VARIABLES_FIELD, [])
            if user_prompt and user_variables:
                optimized_prompt_adapter.set_user_prompt(content=user_prompt, variables=user_variables)
            few_shot_samples, format_type = self._create_few_shot_samples_with_prompt(optimized_predictor,
                                                                                      user_prompt, user_variables)
            optimized_prompt_adapter.add_few_shot(examples=few_shot_samples, format_type=format_type)
        optimized_prompt_adapter.adapt()
        return optimized_prompt_adapter

    def optimize(self,
                 task_model_id: str = DEFAULT_TASK_MODEL,
                 prompter_model_id: str = DEFAULT_PROMPT_MODEL,
                 num_candidates: Optional[int] = None,
                 num_threads: int = 2,
                 num_trials: Optional[int] = None,
                 max_bootstrapped_demos: int = 4,
                 max_labeled_demos: int = 4,
                 minibatch_size: int = 35,
                 train_split: float = 0.5, # Default to 50% Split
                 enable_json_fallback: bool = False) -> PromptAdapter:

        if self.dataset_adapter is None:
            raise ValueError("dataset_adapter is required for NovaPromptOptimizer optimization")

        if self.metric_adapter is None:
            raise ValueError("metric_adapter is required for NovaPromptOptimizer optimization")

        if self.inference_adapter is None:
            raise ValueError("inference_adapter is required for Nova Optima optimization")

        auto_setting = None
        if num_candidates is None and num_trials is None:
            auto_setting = "medium"
            logger.info("Both num_candidates and num_trials are None. Defaulting to NovaPromptOptimizer Medium optimization")
        elif num_candidates is None:
            raise ValueError("num_candidates must be specified when num_trials is provided")
        elif num_trials is None:
            raise ValueError("num_trials must be specified when num_candidates is provided")

        # Set AWS region
        if self.inference_adapter.region:
            os.environ["AWS_REGION_NAME"] = self.inference_adapter.region
        else:
            os.environ["AWS_REGION_NAME"] = 'us-west-2'

        # Setup dspy.LM
        task_lm = RateLimitedLM(dspy.LM(f'bedrock/{task_model_id}'), rate_limit=self.inference_adapter.rate_limit)
        logger.info(f"Using {task_model_id} for Evaluation")
        prompt_lm = RateLimitedLM(dspy.LM(f'bedrock/{prompter_model_id}'), rate_limit=self.inference_adapter.rate_limit)
        logger.info(f"Using {prompter_model_id} for Prompting")

        # Configure DSPy
        dspy.configure(lm=task_lm)
        dspy.settings.configure(adapter=CustomChatAdapter(user_prompt_template=
                                                                   self.prompt_adapter.fetch_user_template(),
                                                                   enable_json_fallback=enable_json_fallback))
        # Create a predictor; Only provide System Prompt Template since Nova Meta Prompter was run before this.
        prompt = self.prompt_adapter.fetch_system_template()
        initial_predictor = self._create_predictor(prompt)

        # Prepare the dataset
        train_data, test_data = self._process_dataset_adapter(train_split)

        minibatch_size = min(len(test_data), minibatch_size)

        # Define the optimizer
        optimizer = MIPROv2(
            metric=self._dspy_metric,
            auto=auto_setting,
            prompt_model=prompt_lm,
            task_model=task_lm,
            num_candidates=num_candidates,
            num_threads=num_threads
        )

        logger.info("Using Nova tips for MIPROv2 optimization")
        # Monkey patch the _propose_instructions method to use NovaGroundedProposer
        original_propose_instructions = optimizer._propose_instructions

        def patched_propose_instructions(
                program,
                trainset,
                demo_candidates,
                view_data_batch_size,
                program_aware_proposer,
                data_aware_proposer,
                tip_aware_proposer,
                fewshot_aware_proposer,
        ):
            logger.info("Entering patched_propose_instructions, patching GroundedProposer with NovaGroundedProposer")
            dspy.settings.configure(adapter=ChatAdapter())
            # Save the original GroundedProposer in dspy.teleprompt.mipro_optimizer_v2 module for restoring later
            from dspy.teleprompt.mipro_optimizer_v2 import GroundedProposer as OriginalGroundedProposer  # type: ignore

            # Replace the GroundedProposer with NovaGroundedProposer in the module's namespace
            dspy.teleprompt.mipro_optimizer_v2.GroundedProposer = NovaGroundedProposer

            logger.info(f"Patched GroundedProposer, "
                        f"current GroundedProposer class={dspy.teleprompt.mipro_optimizer_v2.GroundedProposer}")

            try:
                # Call the original method with NovaGroundedProposer being used instead
                result = original_propose_instructions(
                    program,
                    trainset,
                    demo_candidates,
                    view_data_batch_size,
                    program_aware_proposer,
                    data_aware_proposer,
                    tip_aware_proposer,
                    fewshot_aware_proposer,
                )
                return result
            finally:
                # Restore the original GroundedProposer
                dspy.teleprompt.mipro_optimizer_v2.GroundedProposer = OriginalGroundedProposer
                logger.info(f"Restored GroundedProposer, "
                            f"current GroundedProposer class={dspy.teleprompt.mipro_optimizer_v2.GroundedProposer}")
                dspy.settings.configure(adapter=CustomChatAdapter(user_prompt_template=
                                                                  self.prompt_adapter.fetch_user_template(),
                                                                  enable_json_fallback=enable_json_fallback))

        # Apply the monkey patch
        optimizer._propose_instructions = patched_propose_instructions

        # Run the optimization
        optimized_predictor = optimizer.compile(
            initial_predictor,
            trainset=train_data,
            num_trials=num_trials,
            valset=test_data,
            minibatch_size=minibatch_size,
            max_bootstrapped_demos=max_bootstrapped_demos,
            max_labeled_demos=max_labeled_demos,
            provide_traceback=True,
            requires_permission_to_run=False
        )

        # Create a new PromptAdapter with the optimized prompt
        return self._create_optimized_prompt_adapter(optimized_predictor)
