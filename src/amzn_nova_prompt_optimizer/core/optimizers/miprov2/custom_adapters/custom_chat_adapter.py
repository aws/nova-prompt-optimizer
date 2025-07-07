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
from typing import Any, Type, Optional

from dspy import Adapter, ChatAdapter  # type: ignore
from dspy.clients.lm import LM  # type: ignore
from dspy.signatures.signature import Signature  # type: ignore
from dspy.utils import BaseCallback  # type: ignore
from dspy.utils.exceptions import AdapterParseError  # type: ignore
from litellm import ContextWindowExceededError
from amzn_nova_prompt_optimizer.core.input_adapters.prompt_adapter import PROMPT_VARIABLE_PATTERN

logger = logging.getLogger(__name__)


class CustomChatAdapter(ChatAdapter):
    def __init__(self, user_prompt_template:str, callbacks: Optional[list[BaseCallback]] = None,
                 enable_json_fallback: bool = False,  **kwargs):
        super().__init__(callbacks)
        logger.info(f"Initializing CustomChatAdapter with enable_json_fallback={enable_json_fallback}")
        self.enable_json_fallback = enable_json_fallback
        self.user_prompt_template = user_prompt_template

    def __call__(
            self,
            lm: LM,
            lm_kwargs: dict[str, Any],
            signature: Type[Signature],
            demos: list[dict[str, Any]],
            inputs: dict[str, Any],
    ) -> list[dict[str, Any]]:
        try:
            return Adapter.__call__(self, lm, lm_kwargs, signature, demos, inputs)
        except Exception as e:
            logger.warning(f"Encountered error {e} while calling CustomChatAdapter.")
            if not self.enable_json_fallback:
                logger.error("JSON fallback is disabled. Raising error.")
                raise e
            # fallback to JSONAdapter
            logger.info("Falling back to JSONAdapter.")
            from dspy.adapters.json_adapter import JSONAdapter  # type: ignore

            if isinstance(e, ContextWindowExceededError) or isinstance(self, JSONAdapter):
                # On context window exceeded error or already using JSONAdapter, we don't want to retry with a different
                # adapter.
                raise e
            return JSONAdapter()(lm, lm_kwargs, signature, demos, inputs)

    def format_field_description(self, signature: Type[Signature]) -> str:
        return signature.instructions  # Use raw system prompt

    def format_field_structure(self, signature: Type[Signature]) -> str:
        return ""  # No additional structure

    def format_task_description(self, signature: Type[Signature]) -> str:
        return ""  # No appended instructions

    def format_user_message_content(
            self,
            signature: Type[Signature],
            inputs: dict[str, Any],
            prefix: str = "",
            suffix: str = "",
            main_request: bool = False,
    ) -> str:
        """
       Render user prompt template with inputs.
       Example: "Summarize the following text: {{text}}" → "Summarize the following text: Hello world"
       """
        # Prepare template vars
        template_vars = {var: str(inputs.get(var, "")) for var in inputs}

        def replace_variable(match):
            var = match.group(1)
            return template_vars.get(var, match.group(0))  # Keep as-is if not found

        # Replace variables in the user prompt template
        formatted_prompt = PROMPT_VARIABLE_PATTERN.sub(replace_variable, self.user_prompt_template)

        return formatted_prompt.strip()

    def format_assistant_message_content(
            self,
            signature: Type[Signature],
            outputs: dict[str, Any],
            missing_field_message: str | None = None,
    ) -> str:
        assistant_message_content = "\n".join(
            str(outputs.get(k, missing_field_message))
            for k in signature.output_fields
        )
        return assistant_message_content

    def parse(self, signature: Type[Signature], completion: str) -> dict[str, Any]:
        try:
            return {k: completion for k in signature.output_fields}  # simplistic assumption
        except Exception as e:
            raise AdapterParseError(
                adapter_name="CustomChatAdapter",
                signature=signature,
                lm_response=completion,
                message=str(e)
            )
