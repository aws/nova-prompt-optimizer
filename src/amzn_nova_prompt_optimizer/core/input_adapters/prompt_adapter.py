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
import json
import re
import logging
import os

from abc import ABC, abstractmethod
from typing import Set, Optional, Dict, Any, List
from jinja2 import Environment, Template

logger = logging.getLogger(__name__)

DEFAULT_SYSTEM_PROMPT = ""
USER_PROMPT_COMPONENT = "user_prompt"
SYSTEM_PROMPT_COMPONENT = "system_prompt"
FEW_SHOT_COMPONENT = "few_shot"
CONVERSE_FEW_SHOT_FORMAT = "converse"
APPEND_TO_USER_PROMPT_FEW_SHOT_FORMAT = "append_to_user_prompt"
APPEND_TO_SYSTEM_PROMPT_FEW_SHOT_FORMAT = "append_to_system_prompt"
PROMPT_TYPE_FIELD = "type"
PROMPT_VARIABLES_FIELD = "variables"
PROMPT_TEMPLATE_FIELD = "template"
PROMPT_METADATA_FIELD = "metadata"
PROMPT_FORMAT_FIELD = "format"
FEW_SHOT_EXAMPLES_FIELD = "examples"
FEW_SHOT_FORMAT_FIELD = "format"
PROMPT_MODEL_INPUT_FIELD = "model_input"

PROMPT_VARIABLE_PATTERN = re.compile(r'\{+\s*(\w+)\s*\}+')

class FewShotFormat:
    """Handler for different few-shot example formats"""

    @staticmethod
    def convert(examples: List[Dict[str, Any]]) -> List[Dict[str, str]]:
        """Convert any supported format to input-output format"""
        if not examples:
            return []

        # Already in input-output format
        if all(isinstance(ex, dict) and 'input' in ex and 'output' in ex for ex in examples):
            return examples

        # Convert from role-based format
        if all(isinstance(ex, dict) and 'role' in ex for ex in examples):
            return [
                {
                    'input': examples[i]['content'][0]['text'],
                    'output': examples[i + 1]['content'][0]['text']
                }
                for i in range(0, len(examples), 2)
                if i + 1 < len(examples)
                   and examples[i]['role'] == 'user'
                   and examples[i + 1]['role'] == 'assistant'
            ]
        raise ValueError("Unsupported example format")

    @staticmethod
    def validate(examples: List[Dict[str, Any]]) -> bool:
        """Validate that examples are in input-output format"""
        return all(
            isinstance(ex, dict)
            and 'input' in ex
            and 'output' in ex
            and isinstance(ex['input'], str)
            and isinstance(ex['output'], str)
            for ex in examples
        )

class PromptAdapter(ABC):
    def __init__(self):
        self.standardized_prompt: Dict[Any, Any] = {}
        self.few_shot_examples = []
        self.few_shot_format = None
        self.user_prompt: Optional[str] = None
        self.system_prompt: Optional[str] = None
        self.user_variables: Set[str] = set()
        self.system_variables: Set[str] = set()

    def load_few_shot(self, file_path: str, format_type: str = "converse") -> 'PromptAdapter':
        """
        Load few-shot examples from a file and convert to input-output format.

        :param file_path: Path to the JSON file containing examples
        :param format_type: Format type for few-shot examples ("converse", "user_prompt", "system_prompt")
        :return: Self for method chaining
        :raises FileNotFoundError: If the specified file does not exist
        :raises ValueError: If the file contains invalid JSON or unsupported example format
        """
        # Validate format type
        if format_type not in ["converse", "user_prompt", "system_prompt"]:
            raise ValueError("Invalid few-shot format type")

        try:
            with open(file_path, 'r') as f:
                examples = json.load(f)
        except json.JSONDecodeError:
            raise ValueError(f"Invalid JSON format in file: {file_path}")

        if not examples:
            raise ValueError("Examples list is empty")

        # Convert to input-output format
        try:
            self.few_shot_examples = FewShotFormat.convert(examples)
        except ValueError as e:
            raise ValueError(f"Failed to process examples: {str(e)}")

        # Validate final format
        if not FewShotFormat.validate(self.few_shot_examples):
            raise ValueError("Examples conversion resulted in invalid format")

        self.few_shot_format = format_type
        return self


    def add_few_shot(self, examples: List[Dict[str, str]], format_type: str = "converse"):
        if format_type not in [CONVERSE_FEW_SHOT_FORMAT,
                               APPEND_TO_USER_PROMPT_FEW_SHOT_FORMAT,
                               APPEND_TO_SYSTEM_PROMPT_FEW_SHOT_FORMAT]:
            raise ValueError("Invalid few-shot format type")
        self.few_shot_examples = examples
        self.few_shot_format = format_type

    def set_user_prompt(self,
                        content: Optional[str] = None,
                        file_path: Optional[str] = None,
                        variables: Optional[Set[str]] = None) -> 'PromptAdapter':
        """
        Set the user prompt content and its variables

        :param content: Prompt content as string
        :param file_path: Path to prompt file
        :param variables: Set of variables used in the user prompt
        """
        self.user_prompt = self._get_content(content, file_path)
        if variables is not None:
            self.user_variables = variables
        return self

    def set_system_prompt(self,
                          content: Optional[str] = None,
                          file_path: Optional[str] = None,
                          variables: Optional[Set[str]] = None) -> 'PromptAdapter':
        """
        Set the system prompt content and its variables

        :param content: Prompt content as string
        :param file_path: Path to prompt file
        :param variables: Set of variables used in the system prompt
        """
        self.system_prompt = self._get_content(content, file_path)
        if variables is not None:
            self.system_variables = variables
        return self

    def _get_content(self, content: Optional[str], file_path: Optional[str]) -> str:
        if content is None and file_path is None:
            raise ValueError("Either content or file_path must be provided")

        if file_path is not None:
            return self._load_prompt(file_path)
        if content is not None:
            return content
        else:
            raise ValueError("Content cannot be None if no file_path is provided")

    def adapt(self) -> 'PromptAdapter':
        self.standardized_prompt = self._standardize_prompt()
        return self

    @staticmethod
    def _load_prompt(file_path: str) -> str:
        with open(file_path, 'r') as file:
            return file.read()

    def _standardize_prompt(self) -> dict:
        standardized_prompt = {}

        # Add user prompt component if it exists
        if self.user_prompt:
            standardized_prompt[USER_PROMPT_COMPONENT] = {
                PROMPT_VARIABLES_FIELD: list(self.user_variables),
                PROMPT_TEMPLATE_FIELD: self.user_prompt,
                PROMPT_METADATA_FIELD: {
                    PROMPT_FORMAT_FIELD: self.get_format()
                }
            }
        else:
            # If it does not exist but System prompt does, then we are missing user input, raise an error
            if self.system_prompt:
                raise ValueError("User Input cannot be empty when system prompt is set")

        # Add system prompt component if it exists
        if self.system_prompt:
            standardized_prompt[SYSTEM_PROMPT_COMPONENT] = {
                PROMPT_VARIABLES_FIELD: list(self.system_variables),
                PROMPT_TEMPLATE_FIELD: self.system_prompt,
                PROMPT_METADATA_FIELD: {
                    PROMPT_FORMAT_FIELD: self.get_format()
                }
            }
        # If it does not exist, provide default system prompt i.e. empty string
        else:
            logger.info("System Prompt not set, initializing as empty string...")
            standardized_prompt[SYSTEM_PROMPT_COMPONENT] = {
                PROMPT_VARIABLES_FIELD: [],
                PROMPT_TEMPLATE_FIELD: DEFAULT_SYSTEM_PROMPT,
                PROMPT_METADATA_FIELD: {
                    PROMPT_FORMAT_FIELD: self.get_format()
                }
            }

        # Add few-shot examples if they exist
        if self.few_shot_examples:
            standardized_prompt[FEW_SHOT_COMPONENT] = {
                FEW_SHOT_EXAMPLES_FIELD: self.few_shot_examples,
                FEW_SHOT_FORMAT_FIELD: self.few_shot_format
            }

        if not standardized_prompt:
            raise ValueError("No prompts have been set. Use set_user_prompt() or set_system_prompt()")

        return standardized_prompt

    def show(self) -> None:
        if not self.standardized_prompt:
            logger.warn("Prompt is empty. Call adapt() first.")
            return

        logger.info("\nStandardized Prompt:")
        print(json.dumps(self.standardized_prompt, indent=2))

    def save(self, directory_path: str = "./prompts") -> None:
        """
        Save prompts and examples to appropriate files based on format and configuration

        :param directory_path: Directory where files should be saved
        """
        if not self.standardized_prompt:
            raise ValueError("No prompt to save. Call adapt() first.")

        os.makedirs(directory_path, exist_ok=True)

        # Handle user prompt
        if USER_PROMPT_COMPONENT in self.standardized_prompt:
            user_format = self.standardized_prompt[USER_PROMPT_COMPONENT][PROMPT_METADATA_FIELD][PROMPT_FORMAT_FIELD]
            user_template = self.standardized_prompt[USER_PROMPT_COMPONENT][PROMPT_TEMPLATE_FIELD]

            # If few-shot examples should be appended to user prompt
            if (self.few_shot_examples and
                    self.few_shot_format == APPEND_TO_USER_PROMPT_FEW_SHOT_FORMAT):
                user_template = self._append_examples(user_template)

            user_file = os.path.join(directory_path, f"user_prompt{self._get_extension(user_format)}")
            with open(user_file, 'w') as f:
                f.write(user_template)

        # Handle system prompt
        if SYSTEM_PROMPT_COMPONENT in self.standardized_prompt:
            system_format = (
                self.standardized_prompt)[SYSTEM_PROMPT_COMPONENT][PROMPT_METADATA_FIELD][PROMPT_FORMAT_FIELD]
            system_template = self.standardized_prompt[SYSTEM_PROMPT_COMPONENT][PROMPT_TEMPLATE_FIELD]
            if system_template != DEFAULT_SYSTEM_PROMPT:
                # If few-shot examples should be appended to system prompt
                if (self.few_shot_examples and
                        self.few_shot_format == APPEND_TO_SYSTEM_PROMPT_FEW_SHOT_FORMAT):
                    system_template = self._append_examples(system_template)

                system_file = os.path.join(directory_path, f"system_prompt{self._get_extension(system_format)}")
                with open(system_file, 'w') as f:
                    f.write(system_template)

        # Handle few-shot examples in converse format
        if self.few_shot_examples and self.few_shot_format == CONVERSE_FEW_SHOT_FORMAT:
            few_shot_file = os.path.join(directory_path, "few_shot.json")
            formatted_examples = []
            for example in self.few_shot_examples:
                formatted_examples.extend([
                    {"role": "user", "content": [{"text": example['input']}]},
                    {"role": "assistant", "content": [{"text": example['output']}]}
                ])
            with open(few_shot_file, 'w') as f:
                json.dump(formatted_examples, f, indent=2)

    def _append_examples(self, template: str) -> str:
        """
        Append examples to the template in the specified format

        :param template: Original template
        :return: Template with appended examples
        """
        examples_text = "\n\n**Examples**\n"
        for i, example in enumerate(self.few_shot_examples, 1):
            examples_text += f"\nExample {i}:\nInput: {example['input']}\nOutput: {example['output']}\n"
        return template + examples_text

    def _get_extension(self, format_type: str) -> str:
        """
        Get file extension based on format type

        :param format_type: Format type (e.g., 'jinja', 'text')
        :return: Appropriate file extension
        """
        format_extensions = {
            "text": ".txt"
        }
        return format_extensions.get(format_type, ".txt")


    def fetch(self) -> Dict[Any, Any]:
        if not self.standardized_prompt:
            raise ValueError("No prompt to fetch. Call adapt() first.")
        return self.standardized_prompt

    def fetch_user_template(self) -> str:
        if not self.standardized_prompt:
            raise ValueError("No prompt to fetch. Call adapt() first.")

        component = self.standardized_prompt.get(USER_PROMPT_COMPONENT)
        if not component:
            raise ValueError("Fault in Prompt Adapter setup, User prompt component not set")
        return component[PROMPT_TEMPLATE_FIELD]

    def fetch_system_template(self) -> str:
        if not self.standardized_prompt:
            raise ValueError("No prompt to fetch. Call adapt() first.")

        component = self.standardized_prompt.get(SYSTEM_PROMPT_COMPONENT)
        if not component:
            raise ValueError("Fault in Prompt Adapter setup, System prompt component not set")
        return component[PROMPT_TEMPLATE_FIELD]

    @abstractmethod
    def get_format(self) -> str:
        pass

    @abstractmethod
    def get_file_extension(self) -> str:
        pass



class TextPromptAdapter(PromptAdapter):
    def get_format(self) -> str:
        return "text"

    def get_file_extension(self) -> str:
        return ".txt"
