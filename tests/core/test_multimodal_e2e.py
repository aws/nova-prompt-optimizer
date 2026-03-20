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

"""
End-to-end tests for the multimodal image pipeline.

Covers the full data flow without hitting real AWS:
  DatasetAdapter (image_columns)
    → PromptAdapter (image_variables)
      → InferenceRunner (_create_messages / _format_template)
        → BedrockConverseHandler (_build_content_blocks / _bytes_to_image_block)
          → Bedrock Converse API (mocked)
"""

import io
import os
import struct
import tempfile
import unittest
import zlib
from unittest.mock import MagicMock, patch

from amzn_nova_prompt_optimizer.core.inference import InferenceRunner, INFERENCE_OUTPUT_FIELD
from amzn_nova_prompt_optimizer.core.inference.bedrock_converse import (
    BedrockConverseHandler,
    IMAGE_SUPPORT_AVAILABLE,
)
from amzn_nova_prompt_optimizer.core.input_adapters.dataset_adapter import JSONDatasetAdapter
from amzn_nova_prompt_optimizer.core.input_adapters.prompt_adapter import TextPromptAdapter


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_minimal_png() -> bytes:
    """Return a valid 1×1 white PNG as bytes (no external deps needed)."""
    def _chunk(name: bytes, data: bytes) -> bytes:
        c = struct.pack(">I", len(data)) + name + data
        return c + struct.pack(">I", zlib.crc32(name + data) & 0xFFFFFFFF)

    signature = b"\x89PNG\r\n\x1a\n"
    ihdr_data = struct.pack(">IIBBBBB", 1, 1, 8, 2, 0, 0, 0)  # 1x1 RGB
    ihdr = _chunk(b"IHDR", ihdr_data)
    raw_row = b"\x00\xff\xff\xff"  # filter byte + RGB white
    idat = _chunk(b"IDAT", zlib.compress(raw_row))
    iend = _chunk(b"IEND", b"")
    return signature + ihdr + idat + iend


def _make_bedrock_mock_client(response_text: str = "model response") -> MagicMock:
    """Return a mock boto3 bedrock-runtime client."""
    mock_client = MagicMock()
    mock_client.converse.return_value = {
        "output": {"message": {"content": [{"text": response_text}]}}
    }
    return mock_client


# ---------------------------------------------------------------------------
# Layer 1: DatasetAdapter — image_columns loads bytes
# ---------------------------------------------------------------------------

class TestDatasetAdapterImageColumns(unittest.TestCase):

    def test_image_column_loads_png_bytes(self):
        """PNG file path in an image_column is replaced with bytes at adapt time."""
        png_bytes = _make_minimal_png()
        with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as f:
            f.write(png_bytes)
            tmp = f.name
        try:
            adapter = JSONDatasetAdapter(
                input_columns={"image", "label"},
                output_columns={"result"},
                image_columns={"image"},
            )
            adapter.adapt([{"image": tmp, "label": "cat", "result": "animal"}])
            row = adapter.fetch()[0]
            self.assertIsInstance(row["inputs"]["image"], bytes)
            self.assertEqual(row["inputs"]["image"], png_bytes)
            self.assertEqual(row["inputs"]["label"], "cat")  # non-image unchanged
        finally:
            os.unlink(tmp)

    def test_non_image_column_stays_string(self):
        adapter = JSONDatasetAdapter(
            input_columns={"text", "image"},
            output_columns={"result"},
            image_columns={"image"},
        )
        adapter.adapt([{"text": "hello", "image": "/no/such/file.jpg", "result": "x"}])
        row = adapter.fetch()[0]
        self.assertEqual(row["inputs"]["text"], "hello")
        self.assertEqual(row["inputs"]["image"], "/no/such/file.jpg")  # fallback to string

    def test_split_preserves_image_columns_and_bytes(self):
        png_bytes = _make_minimal_png()
        with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as f:
            f.write(png_bytes)
            tmp = f.name
        try:
            adapter = JSONDatasetAdapter(
                input_columns={"image"},
                output_columns={"result"},
                image_columns={"image"},
            )
            data = [{"image": tmp, "result": str(i)} for i in range(10)]
            adapter.adapt(data)
            train, test = adapter.split(0.7)
            self.assertEqual(train.image_columns, {"image"})
            self.assertEqual(test.image_columns, {"image"})
            # All rows in train should have bytes
            for row in train.fetch():
                self.assertIsInstance(row["inputs"]["image"], bytes)
        finally:
            os.unlink(tmp)


# ---------------------------------------------------------------------------
# Layer 2: PromptAdapter — image_variables stored in standardized prompt
# ---------------------------------------------------------------------------

class TestPromptAdapterImageVariables(unittest.TestCase):

    def test_image_variables_in_standardized_prompt(self):
        adapter = TextPromptAdapter()
        adapter.set_user_prompt(
            content="Classify this image: {{image}}",
            variables={"image"},
            image_variables={"image"},
        )
        adapter.adapt()
        component = adapter.fetch()["user_prompt"]
        self.assertEqual(set(component["image_variables"]), {"image"})
        self.assertEqual(set(component["variables"]), {"image"})

    def test_no_image_variables_by_default(self):
        adapter = TextPromptAdapter()
        adapter.set_user_prompt(content="Hello {{name}}", variables={"name"})
        adapter.adapt()
        component = adapter.fetch()["user_prompt"]
        self.assertEqual(component.get("image_variables", []), [])

    def test_image_variables_not_subset_raises(self):
        adapter = TextPromptAdapter()
        with self.assertRaises(ValueError):
            adapter.set_user_prompt(
                content="Hello {{name}}",
                variables={"name"},
                image_variables={"image"},  # not in variables
            )


# ---------------------------------------------------------------------------
# Layer 3: InferenceRunner — _format_template uses placeholder for image vars
# ---------------------------------------------------------------------------

class TestInferenceRunnerImageVariables(unittest.TestCase):

    def _make_runner(self):
        return InferenceRunner(
            prompt_adapter=MagicMock(),
            dataset_adapter=MagicMock(),
            inference_adapter=MagicMock(),
        )

    def test_format_template_image_var_uses_placeholder(self):
        runner = self._make_runner()
        template = "Classify this image: {{image}}"
        variables = ["image"]
        inputs = {"image": b"\x89PNG\r\n"}  # bytes
        result = runner._format_template(template, variables, inputs, image_variables={"image"})
        # Should NOT contain raw bytes repr; should contain placeholder
        self.assertNotIn("b'\\x89PNG", result)
        self.assertIn("[image]", result)

    def test_format_template_non_image_var_substituted_normally(self):
        runner = self._make_runner()
        template = "Label: {{label}}, Image: {{image}}"
        variables = ["label", "image"]
        inputs = {"label": "cat", "image": b"\x89PNG\r\n"}
        result = runner._format_template(template, variables, inputs, image_variables={"image"})
        self.assertIn("cat", result)
        self.assertIn("[image]", result)
        self.assertNotIn("b'\\x89", result)

    def test_create_messages_builds_structured_dict_for_image(self):
        runner = self._make_runner()
        png_bytes = _make_minimal_png()
        standardized_prompt = {
            "user_prompt": {
                "template": "Classify: {{image}}",
                "variables": ["image"],
                "image_variables": ["image"],
            },
            "system_prompt": {"template": "You are a classifier.", "variables": []},
        }
        inputs = {"image": png_bytes}
        _, messages = runner._create_messages(standardized_prompt, inputs)
        self.assertEqual(len(messages), 1)
        user_msg = messages[0]["user"]
        # Must be a dict with both text and image_bytes
        self.assertIsInstance(user_msg, dict)
        self.assertIn("text", user_msg)
        self.assertIn("image_bytes", user_msg)
        self.assertEqual(user_msg["image_bytes"], png_bytes)

    def test_create_messages_plain_string_when_no_image_vars(self):
        runner = self._make_runner()
        standardized_prompt = {
            "user_prompt": {
                "template": "Classify: {{label}}",
                "variables": ["label"],
                "image_variables": [],
            },
            "system_prompt": {"template": "", "variables": []},
        }
        inputs = {"label": "cat"}
        _, messages = runner._create_messages(standardized_prompt, inputs)
        self.assertEqual(len(messages), 1)
        self.assertIsInstance(messages[0]["user"], str)
        self.assertIn("cat", messages[0]["user"])

    def test_create_messages_falls_back_to_string_when_bytes_missing(self):
        """If image_variables declared but input has string (file not found), use string."""
        runner = self._make_runner()
        standardized_prompt = {
            "user_prompt": {
                "template": "Classify: {{image}}",
                "variables": ["image"],
                "image_variables": ["image"],
            },
            "system_prompt": {"template": "", "variables": []},
        }
        inputs = {"image": "/nonexistent/path.jpg"}  # string, not bytes
        _, messages = runner._create_messages(standardized_prompt, inputs)
        self.assertEqual(len(messages), 1)
        # Falls back to plain string message
        self.assertIsInstance(messages[0]["user"], str)


# ---------------------------------------------------------------------------
# Layer 4: BedrockConverseHandler — _build_content_blocks
# ---------------------------------------------------------------------------

class TestBedrockConverseHandlerMultimodal(unittest.TestCase):

    def setUp(self):
        self.mock_client = _make_bedrock_mock_client()

    def test_bytes_with_image_support_disabled_returns_placeholder(self):
        handler = BedrockConverseHandler(self.mock_client, enable_image_support=False)
        result = handler._build_content_blocks(b"\x89PNG\r\n")
        self.assertEqual(result, [{"text": "[image]"}])

    def test_dict_text_only_returns_text_block(self):
        handler = BedrockConverseHandler(self.mock_client, enable_image_support=False)
        result = handler._build_content_blocks({"text": "hello"})
        self.assertEqual(result, [{"text": "hello"}])

    def test_dict_image_bytes_disabled_returns_text_only(self):
        handler = BedrockConverseHandler(self.mock_client, enable_image_support=False)
        result = handler._build_content_blocks({"text": "classify", "image_bytes": b"data"})
        self.assertEqual(result, [{"text": "classify"}])

    def test_plain_string_returns_text_block(self):
        handler = BedrockConverseHandler(self.mock_client, enable_image_support=False)
        result = handler._build_content_blocks("hello world")
        self.assertEqual(result, [{"text": "hello world"}])

    @unittest.skipUnless(IMAGE_SUPPORT_AVAILABLE, "PIL/requests not installed")
    def test_bytes_with_image_support_enabled_returns_image_block(self):
        handler = BedrockConverseHandler(self.mock_client, enable_image_support=True)
        png_bytes = _make_minimal_png()
        result = handler._build_content_blocks(png_bytes)
        self.assertEqual(len(result), 1)
        self.assertIn("image", result[0])
        self.assertEqual(result[0]["image"]["format"], "png")
        self.assertEqual(result[0]["image"]["source"]["bytes"], png_bytes)

    @unittest.skipUnless(IMAGE_SUPPORT_AVAILABLE, "PIL/requests not installed")
    def test_dict_with_image_bytes_and_text_enabled(self):
        handler = BedrockConverseHandler(self.mock_client, enable_image_support=True)
        png_bytes = _make_minimal_png()
        result = handler._build_content_blocks({"text": "classify this", "image_bytes": png_bytes})
        # Should have image block + text block
        types = [list(b.keys())[0] for b in result]
        self.assertIn("image", types)
        self.assertIn("text", types)
        text_block = next(b for b in result if "text" in b)
        self.assertEqual(text_block["text"], "classify this")

    @unittest.skipUnless(IMAGE_SUPPORT_AVAILABLE, "PIL/requests not installed")
    def test_get_messages_with_structured_dict(self):
        handler = BedrockConverseHandler(self.mock_client, enable_image_support=True)
        png_bytes = _make_minimal_png()
        messages = handler._get_messages([{"user": {"text": "classify", "image_bytes": png_bytes}}])
        self.assertEqual(len(messages), 1)
        content = messages[0]["content"]
        types = [list(b.keys())[0] for b in content]
        self.assertIn("image", types)
        self.assertIn("text", types)


# ---------------------------------------------------------------------------
# Layer 5: Full end-to-end pipeline (all layers together, Bedrock mocked)
# ---------------------------------------------------------------------------

class TestMultimodalEndToEnd(unittest.TestCase):

    def _build_prompt_adapter(self):
        adapter = TextPromptAdapter()
        adapter.set_system_prompt(content="You are an image classifier.")
        adapter.set_user_prompt(
            content="Classify this image: {{image}}",
            variables={"image"},
            image_variables={"image"},
        )
        adapter.adapt()
        return adapter

    def test_full_pipeline_text_only_unchanged(self):
        """Text-only flow must be completely unaffected by multimodal changes."""
        prompt_adapter = TextPromptAdapter()
        prompt_adapter.set_system_prompt(content="You are helpful.")
        prompt_adapter.set_user_prompt(content="What is {{topic}}?", variables={"topic"})
        prompt_adapter.adapt()

        dataset_adapter = JSONDatasetAdapter({"topic"}, {"answer"})
        dataset_adapter.adapt([{"topic": "Python", "answer": "a language"}])

        mock_bedrock = _make_bedrock_mock_client("Python is a language.")
        with patch("amzn_nova_prompt_optimizer.core.inference.bedrock_adapter.boto3.Session") as mock_session_cls:
            mock_session = MagicMock()
            mock_session.client.return_value = mock_bedrock
            mock_session_cls.return_value = mock_session

            from amzn_nova_prompt_optimizer.core.inference.bedrock_adapter import BedrockInferenceAdapter
            inference_adapter = BedrockInferenceAdapter(region_name="us-east-1")

        runner = InferenceRunner(prompt_adapter, dataset_adapter, inference_adapter)
        runner.model_id = "us.amazon.nova-lite-v1:0"
        runner.inf_config = {"max_tokens": 100, "temperature": 0, "top_p": 1, "top_k": 1}

        result = runner._infer_row(dataset_adapter.fetch()[0])
        self.assertEqual(result[INFERENCE_OUTPUT_FIELD], "Python is a language.")

        # Verify Bedrock was called with plain text content
        call_args = mock_bedrock.converse.call_args
        messages = call_args.kwargs["messages"]
        self.assertEqual(len(messages), 1)
        self.assertEqual(messages[0]["role"], "user")
        self.assertEqual(messages[0]["content"], [{"text": "What is Python?"}])

    @unittest.skipUnless(IMAGE_SUPPORT_AVAILABLE, "PIL/requests not installed")
    def test_full_pipeline_multimodal_sends_image_block(self):
        """Multimodal flow sends correct image content block to Bedrock."""
        png_bytes = _make_minimal_png()

        with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as f:
            f.write(png_bytes)
            tmp = f.name

        try:
            # 1. Dataset: image column loads bytes
            dataset_adapter = JSONDatasetAdapter(
                input_columns={"image"},
                output_columns={"label"},
                image_columns={"image"},
            )
            dataset_adapter.adapt([{"image": tmp, "label": "cat"}])
            row = dataset_adapter.fetch()[0]
            self.assertIsInstance(row["inputs"]["image"], bytes)

            # 2. Prompt: image_variables declared
            prompt_adapter = self._build_prompt_adapter()

            # 3. Inference adapter with image support enabled
            mock_bedrock = _make_bedrock_mock_client("cat")
            with patch("amzn_nova_prompt_optimizer.core.inference.bedrock_adapter.boto3.Session") as mock_session_cls:
                mock_session = MagicMock()
                mock_session.client.return_value = mock_bedrock
                mock_session_cls.return_value = mock_session

                from amzn_nova_prompt_optimizer.core.inference.bedrock_adapter import BedrockInferenceAdapter
                inference_adapter = BedrockInferenceAdapter(
                    region_name="us-east-1",
                    enable_image_support=True,
                )

            # 4. Run inference
            runner = InferenceRunner(prompt_adapter, dataset_adapter, inference_adapter)
            runner.model_id = "us.amazon.nova-lite-v1:0"
            runner.inf_config = {"max_tokens": 100, "temperature": 0, "top_p": 1, "top_k": 1}

            result = runner._infer_row(row)
            self.assertEqual(result[INFERENCE_OUTPUT_FIELD], "cat")

            # 5. Verify Bedrock received an image content block
            call_args = mock_bedrock.converse.call_args
            messages = call_args.kwargs["messages"]
            self.assertEqual(len(messages), 1)
            self.assertEqual(messages[0]["role"], "user")
            content = messages[0]["content"]

            block_types = [list(b.keys())[0] for b in content]
            self.assertIn("image", block_types, "Expected an image block in Bedrock call")
            self.assertIn("text", block_types, "Expected a text block in Bedrock call")

            image_block = next(b for b in content if "image" in b)
            self.assertEqual(image_block["image"]["format"], "png")
            self.assertEqual(image_block["image"]["source"]["bytes"], png_bytes)

            text_block = next(b for b in content if "text" in b)
            self.assertIn("[image]", text_block["text"])  # placeholder in formatted text

        finally:
            os.unlink(tmp)

    def test_full_pipeline_image_file_missing_falls_back_to_string(self):
        """If image file not found, DatasetAdapter keeps string; pipeline sends plain text."""
        dataset_adapter = JSONDatasetAdapter(
            input_columns={"image"},
            output_columns={"label"},
            image_columns={"image"},
        )
        dataset_adapter.adapt([{"image": "/nonexistent/img.jpg", "label": "cat"}])
        row = dataset_adapter.fetch()[0]
        # Should be string, not bytes
        self.assertIsInstance(row["inputs"]["image"], str)

        prompt_adapter = self._build_prompt_adapter()

        mock_bedrock = _make_bedrock_mock_client("cat")
        with patch("amzn_nova_prompt_optimizer.core.inference.bedrock_adapter.boto3.Session") as mock_session_cls:
            mock_session = MagicMock()
            mock_session.client.return_value = mock_bedrock
            mock_session_cls.return_value = mock_session

            from amzn_nova_prompt_optimizer.core.inference.bedrock_adapter import BedrockInferenceAdapter
            inference_adapter = BedrockInferenceAdapter(
                region_name="us-east-1",
                enable_image_support=True,
            )

        runner = InferenceRunner(prompt_adapter, dataset_adapter, inference_adapter)
        runner.model_id = "us.amazon.nova-lite-v1:0"
        runner.inf_config = {"max_tokens": 100, "temperature": 0, "top_p": 1, "top_k": 1}

        result = runner._infer_row(row)
        self.assertEqual(result[INFERENCE_OUTPUT_FIELD], "cat")

        # Bedrock should receive plain text (no image block)
        call_args = mock_bedrock.converse.call_args
        messages = call_args.kwargs["messages"]
        content = messages[0]["content"]
        block_types = [list(b.keys())[0] for b in content]
        self.assertNotIn("image", block_types)
        self.assertIn("text", block_types)


if __name__ == "__main__":
    unittest.main()
