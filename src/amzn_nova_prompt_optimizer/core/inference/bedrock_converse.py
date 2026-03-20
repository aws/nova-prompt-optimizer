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

from amzn_nova_prompt_optimizer.core.inference.inference_constants import MAX_TOKENS_FIELD, TEMPERATURE_FIELD, TOP_P_FIELD, TOP_K_FIELD

logger = logging.getLogger(__name__)

# Check if image support dependencies are available
try:
    from pathlib import Path
    from PIL import Image
    from io import BytesIO
    import requests
    IMAGE_SUPPORT_AVAILABLE = True
except ImportError:
    IMAGE_SUPPORT_AVAILABLE = False
    logger.info("Image support dependencies (PIL/requests) not available. Multimodal features disabled.")


class BedrockConverseHandler:
    def __init__(self, bedrock_client, enable_image_support=False):
        """
        Bedrock Converse Handler to manage converse API calls to Bedrock given a model_id
        :param bedrock_client: Bedrock Client
        :param enable_image_support: Enable automatic image loading from paths (default: False).
                                     Set to True to enable multimodal support.
        """
        self.client = bedrock_client
        self.enable_image_support = enable_image_support and IMAGE_SUPPORT_AVAILABLE

    def call_model(self, model_id, system_prompt, user_input, inference_config):
        """
        Makes a bedrock call for the model_id given a system_prompt, user_input, and the inference_config.
        :param model_id: Model ID that needs to be used.
        :param system_prompt: System Prompt
        :param user_input: [{"user": "abcd", {"assistant": "def"}...]
        :param inference_config: Inference parameters
        :return: Model Response as String
        """
        messages = self._get_messages(user_input)
        system_config = self._get_system_config(system_prompt)
        inf_config = self._get_inference_config(inference_config)
        additional_model_request_fields = self._get_additional_model_request_fields(inference_config, model_id)
        model_response = self._call_converse_model(system_config, messages, model_id, inf_config,
                                                   additional_model_request_fields)
        return model_response

    def _call_converse_model(self, system_config, messages, model_id, inf_config, additional_model_request_fields):
        if system_config:
            response = self.client.converse(
                modelId=model_id,
                messages=messages,
                system=system_config,
                inferenceConfig=inf_config,
                additionalModelRequestFields=additional_model_request_fields
            )
        else:
            response = self.client.converse(
                modelId=model_id,
                messages=messages,
                inferenceConfig=inf_config,
                additionalModelRequestFields=additional_model_request_fields
            )
        model_response = response["output"]["message"]["content"][0]["text"]
        return model_response

    @staticmethod
    def _get_inference_config(inference_config):
        inf_config = {"maxTokens": inference_config.get(MAX_TOKENS_FIELD),
                      "temperature": inference_config.get(TEMPERATURE_FIELD),
                      "topP": inference_config.get(TOP_P_FIELD)}
        return inf_config

    @staticmethod
    def _get_additional_model_request_fields(inference_config, model_id):
        if "nova" in model_id:
            return {
                "inferenceConfig": {
                    "topK": inference_config.get(TOP_K_FIELD)
                }
            }
        elif "anthropic" in model_id:
            return {
                "top_k": inference_config.get(TOP_K_FIELD)
            }
        else:
            logger.warning(f"Unsupported model_id: {model_id}, skip adding additional model request fields")
            return {}

    def _get_messages(self, user_input):
        """
        Format messages for Bedrock Converse API.
        Supports three content types per user message:
        - str: plain text (default)
        - bytes: raw image bytes (loaded by DatasetAdapter for image_columns)
        - dict with 'text' and/or 'image_bytes' keys: structured multimodal content
        When enable_image_support=False, bytes values are skipped with a warning.
        """
        formatted_messages = []

        for message in user_input:
            if "user" in message:
                user_content = message["user"]
                content_blocks = self._build_content_blocks(user_content)
                formatted_messages.append({"role": "user", "content": content_blocks})

            if "assistant" in message:
                formatted_messages.append({
                    "role": "assistant",
                    "content": [{"text": message["assistant"]}]
                })

        return formatted_messages

    def _build_content_blocks(self, user_content) -> list:
        """
        Convert a user message value into a list of Bedrock content blocks.

        Handles:
        - bytes: treat as raw image bytes (requires enable_image_support=True)
        - dict with keys 'text' and/or 'image_bytes': structured multimodal
        - str: plain text, or legacy path-based image detection when enable_image_support=True
        """
        # --- Case 1: raw image bytes from DatasetAdapter ---
        if isinstance(user_content, bytes):
            if not self.enable_image_support:
                logger.warning("Received image bytes but enable_image_support=False; sending as text placeholder")
                return [{"text": "[image]"}]
            return self._bytes_to_image_block(user_content)

        # --- Case 2: structured dict with explicit text + image_bytes ---
        if isinstance(user_content, dict):
            blocks = []
            if "image_bytes" in user_content and self.enable_image_support:
                blocks.extend(self._bytes_to_image_block(user_content["image_bytes"]))
            if "text" in user_content:
                blocks.append({"text": str(user_content["text"])})
            return blocks if blocks else [{"text": str(user_content)}]

        # --- Case 3: plain string ---
        if not isinstance(user_content, str):
            return [{"text": str(user_content)}]

        # Fast path: image support off or no image indicators → plain text
        if not self.enable_image_support:
            return [{"text": user_content}]

        might_have_image = (
            'image' in user_content.lower() or
            user_content.startswith('http') or
            any(ext in user_content.lower() for ext in ['.jpg', '.jpeg', '.png', '.gif', '.webp'])
        )
        if might_have_image:
            logger.debug(f"Processing potential multimodal content: {user_content}")
            return self._process_multimodal_content(user_content)

        return [{"text": user_content}]

    @staticmethod
    def _bytes_to_image_block(image_bytes: bytes) -> list:
        """Convert raw image bytes to a Bedrock image content block."""
        if not IMAGE_SUPPORT_AVAILABLE:
            logger.warning("PIL not available; cannot determine image format. Skipping image block.")
            return [{"text": "[image]"}]
        try:
            from io import BytesIO
            img = Image.open(BytesIO(image_bytes))
            img_format = (img.format or 'JPEG').lower()
            if img_format == 'jpg':
                img_format = 'jpeg'
            logger.info(f"Building image block: {img.size} pixels, format={img_format}")
            return [{"image": {"format": img_format, "source": {"bytes": image_bytes}}}]
        except Exception as e:
            logger.warning(f"Failed to parse image bytes: {e}; sending as text placeholder")
            return [{"text": "[image]"}]
    
    @staticmethod
    def _process_multimodal_content(user_content):
        """
        Process content that might contain images.
        Returns list of content blocks for Bedrock Converse API.
        """
        if not IMAGE_SUPPORT_AVAILABLE:
            logger.warning("Image support not available, treating as text")
            return [{"text": str(user_content)}]
        
        content_blocks = []
        image_path = None
        prompt_text = None
        
        # Parse user_content to extract image path and prompt text
        stripped = user_content.strip()
        
        # Check if it's a template variable (skip image processing)
        template_patterns = ['[input]', '{input}', '{{input}}', '[[input]]']
        is_template = (
            stripped.startswith('[[ ##') or
            any(pattern in stripped for pattern in template_patterns) or
            (stripped.startswith('{') and '}' in stripped and not Path(stripped).exists())
        )
        
        if is_template:
            return [{"text": user_content}]
        
        # Check if it contains the image marker pattern
        if "Analyze this image for watermarks:" in user_content:
            parts = user_content.split("Analyze this image for watermarks:")
            if len(parts) == 2:
                prompt_text = parts[0].strip()
                potential_image_path = parts[1].strip()
                logger.debug(f"Found image pattern, extracted path: {potential_image_path}")
                
                # Handle MIPROv2 format: [][actual_path]
                if potential_image_path.startswith('[]'):
                    potential_image_path = potential_image_path[2:]
                    if potential_image_path.startswith('[') and potential_image_path.endswith(']'):
                        potential_image_path = potential_image_path[1:-1]
                    logger.debug(f"Cleaned MIPROv2 format to: {potential_image_path}")
                
                # Skip if it's a template variable
                if potential_image_path not in ['[input]', '{{input}}', '{input}', '[[input]]', 'input', '']:
                    image_path = potential_image_path
                else:
                    return [{"text": user_content}]
        
        # Check if it's a direct file path or URL
        elif user_content.startswith('http'):
            image_path = user_content
        elif Path(user_content).exists() and Path(user_content).suffix.lower() in ['.jpg', '.jpeg', '.png', '.gif', '.webp']:
            image_path = user_content
        else:
            # Regular text content
            return [{"text": user_content}]
        
        # Process image if found
        if image_path:
            try:
                if image_path.startswith('http'):
                    response = requests.get(image_path, timeout=30)
                    response.raise_for_status()
                    image_bytes = response.content
                else:
                    with open(image_path, 'rb') as f:
                        image_bytes = f.read()
                
                # Get image format
                img = Image.open(BytesIO(image_bytes))
                img_format = (img.format or 'JPEG').lower()
                if img_format == 'jpg':
                    img_format = 'jpeg'
                
                # Add image to content blocks
                content_blocks.append({
                    "image": {
                        "format": img_format,
                        "source": {"bytes": image_bytes}
                    }
                })
                
                logger.info(f"Added image: {img.size} pixels, {img_format}, {image_path}")
            except Exception as e:
                logger.warning(f"Failed to load image from {image_path}: {e}")
                # Fall back to text
                return [{"text": str(user_content)}]
        
        # Add prompt text if present
        if prompt_text:
            content_blocks.append({"text": prompt_text})
        
        # If no content blocks, return original as text
        if not content_blocks:
            content_blocks.append({"text": str(user_content)})
        
        return content_blocks


    @staticmethod
    def _get_system_config(system_prompt):
        if system_prompt != "":
            return [{'text': system_prompt}]
        else:
            return None
