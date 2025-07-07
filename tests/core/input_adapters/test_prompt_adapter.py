import unittest
import json

from amzn_nova_prompt_optimizer.core.input_adapters.prompt_adapter import TextPromptAdapter
from unittest.mock import mock_open, patch


class TestPromptAdapter(unittest.TestCase):
    def setUp(self):
        self.adapter = TextPromptAdapter()
        self.user_prompt = "This is a test user prompt with {variable}"
        self.system_prompt = "This is a test system prompt with {variable}"
        self.few_shot_examples = [
            {"input": "test input 1", "output": "test output 1"},
            {"input": "test input 2", "output": "test output 2"}
        ]

    def test_set_user_prompt(self):
        self.adapter.set_user_prompt(content=self.user_prompt, variables={"variable"})
        self.assertEqual(self.adapter.user_prompt, self.user_prompt)
        self.assertEqual(self.adapter.user_variables, {"variable"})

    def test_set_system_prompt(self):
        self.adapter.set_system_prompt(content=self.system_prompt, variables={"variable"})
        self.assertEqual(self.adapter.system_prompt, self.system_prompt)
        self.assertEqual(self.adapter.system_variables, {"variable"})

    def test_load_few_shot(self):
        examples_json = json.dumps([
            {"role": "user", "content": [{"text": "test input"}]},
            {"role": "assistant", "content": [{"text": "test output"}]}
        ])

        # Specify the file path in the patch decorator
        with patch('builtins.open', mock_open(read_data=examples_json)):
            self.adapter.load_few_shot("fake_path.json")

            # Verify the content was processed correctly
            self.assertEqual(len(self.adapter.few_shot_examples), 1)
            self.assertEqual(self.adapter.few_shot_examples[0]["input"], "test input")
            self.assertEqual(self.adapter.few_shot_examples[0]["output"], "test output")

    def test_add_few_shot(self):
        self.adapter.add_few_shot(self.few_shot_examples, "converse")
        self.assertEqual(self.adapter.few_shot_examples, self.few_shot_examples)
        self.assertEqual(self.adapter.few_shot_format, "converse")

    def test_adapt_with_user_prompt_only(self):
        self.adapter.set_user_prompt(content=self.user_prompt)
        adapted = self.adapter.adapt().fetch()

        self.assertIn("user_prompt", adapted)
        self.assertIn("system_prompt", adapted)
        self.assertEqual(adapted["user_prompt"]["template"], self.user_prompt)
        self.assertEqual(adapted["system_prompt"]["template"], "")

    def test_adapt_with_both_prompts(self):
        self.adapter.set_user_prompt(content=self.user_prompt)
        self.adapter.set_system_prompt(content=self.system_prompt)
        adapted = self.adapter.adapt().fetch()

        self.assertIn("user_prompt", adapted)
        self.assertIn("system_prompt", adapted)
        self.assertEqual(adapted["user_prompt"]["template"], self.user_prompt)
        self.assertEqual(adapted["system_prompt"]["template"], self.system_prompt)

    def test_save(self):
        self.adapter.set_user_prompt(content=self.user_prompt)
        self.adapter.set_system_prompt(content=self.system_prompt)
        self.adapter.add_few_shot(self.few_shot_examples, "converse")
        self.adapter.adapt()

        with patch('builtins.open', mock_open()) as mock_file:
            self.adapter.save("./test_dir")
            # Verify that open was called at least 3 times (user, system, and few-shot files)
            self.assertGreaterEqual(mock_file.call_count, 3)

    def test_fetch_templates(self):
        self.adapter.set_user_prompt(content=self.user_prompt)
        self.adapter.set_system_prompt(content=self.system_prompt)
        self.adapter.adapt()

        self.assertEqual(self.adapter.fetch_user_template(), self.user_prompt)
        self.assertEqual(self.adapter.fetch_system_template(), self.system_prompt)

    def test_invalid_few_shot_format(self):
        with self.assertRaises(ValueError):
            self.adapter.add_few_shot(self.few_shot_examples, "invalid_format")

class TestTextPromptAdapter(unittest.TestCase):
    def test_format_specifics(self):
        adapter = TextPromptAdapter()
        self.assertEqual(adapter.get_format(), "text")
        self.assertEqual(adapter.get_file_extension(), ".txt")