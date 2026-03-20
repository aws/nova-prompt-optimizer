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
Image-aware DSPy LM wrapper for multimodal support during MIPROv2 optimization.
"""

import logging
from pathlib import Path
from typing import Any, Dict, List, Optional
from io import BytesIO

import boto3
from PIL import Image
import requests

logger = logging.getLogger(__name__)


class ImageAwareLM:
    """
    Wrapper around DSPy LM that handles image file paths in prompts.
    
    This enables multimodal support during MIPROv2 optimization by:
    1. Detecting image paths in prompts
    2. Loading images from local files or URLs
    3. Calling Bedrock Converse API directly with image content
    
    Note: This is NOT a dspy.LM subclass to avoid initialization issues.
    It acts as a transparent wrapper that delegates to the base LM.
    """
    
    def __init__(self, base_lm, bedrock_client, model_id: str):
        """
        Initialize image-aware LM wrapper.
        
        Args:
            base_lm: The base DSPy LM to wrap (for text-only fallback)
            bedrock_client: Boto3 Bedrock client
            model_id: Bedrock model ID
        """
        self.base_lm = base_lm
        self.bedrock_client = bedrock_client
        self.model_id = model_id
        self._is_processing_image = False  # Flag to prevent recursion
        logger.info(f"✅ Initialized ImageAwareLM wrapper for {model_id}")
    
    def _load_image(self, image_path: str) -> Optional[Dict]:
        """Load image from file path or URL and return Bedrock-formatted content."""
        try:
            if image_path.startswith('http'):
                # Download from URL
                response = requests.get(image_path, timeout=30)
                response.raise_for_status()
                image_bytes = response.content
            elif Path(image_path).exists():
                # Load from local file
                with open(image_path, 'rb') as f:
                    image_bytes = f.read()
            else:
                logger.warning(f"Image path not found: {image_path}")
                return None
            
            # Get image format
            img = Image.open(BytesIO(image_bytes))
            img_format = (img.format or 'JPEG').lower()
            if img_format == 'jpg':
                img_format = 'jpeg'
            
            logger.info(f"✅ ImageAwareLM loaded image: {img.size} pixels, format: {img_format}")
            
            return {
                "image": {
                    "format": img_format,
                    "source": {"bytes": image_bytes}
                }
            }
        except Exception as e:
            logger.error(f"❌ Failed to load image from {image_path}: {e}")
            return None
    
    def _extract_image_path(self, prompt: str) -> tuple[Optional[str], str]:
        """
        Extract image path from prompt if present.
        
        Returns:
            (image_path, cleaned_prompt) tuple
        """
        # Check for image path patterns
        if "Analyze this image for watermarks:" in prompt:
            parts = prompt.split("Analyze this image for watermarks:")
            if len(parts) == 2:
                cleaned_prompt = parts[0].strip()
                image_path = parts[1].strip()
                return image_path, cleaned_prompt
        
        # Check if the entire prompt is just a file path
        prompt_stripped = prompt.strip()
        if (prompt_stripped.startswith('http') or 
            (Path(prompt_stripped).exists() and 
             Path(prompt_stripped).suffix.lower() in ['.jpg', '.jpeg', '.png', '.gif', '.webp'])):
            return prompt_stripped, ""
        
        return None, prompt
    
    def __call__(self, prompt: Optional[str] = None, messages: Optional[List[Dict]] = None, **kwargs):
        """
        Main call method that DSPy uses.
        
        Intercepts the call to detect images and use Bedrock Converse API directly.
        """
        # Prevent recursion
        if self._is_processing_image:
            return self.base_lm(prompt=prompt, messages=messages, **kwargs)
        
        # Handle messages format (DSPy sometimes uses this)
        actual_prompt = prompt
        if messages:
            # Extract the last user message
            for msg in reversed(messages):
                if msg.get('role') == 'user':
                    actual_prompt = msg.get('content', '')
                    break
        
        if not actual_prompt:
            logger.debug("No prompt provided to ImageAwareLM, delegating to base LM")
            return self.base_lm(prompt=prompt, messages=messages, **kwargs)
        
        # Extract image path if present
        image_path, cleaned_prompt = self._extract_image_path(actual_prompt)
        
        if image_path:
            logger.info(f"🔍 ImageAwareLM detected image path: {image_path}")
            self._is_processing_image = True
            
            try:
                # Load image
                image_content = self._load_image(image_path)
                
                if image_content:
                    # Build Bedrock Converse API request with image
                    content_blocks = [image_content]
                    if cleaned_prompt:
                        content_blocks.append({"text": cleaned_prompt})
                    
                    request_params = {
                        "modelId": self.model_id,
                        "messages": [{
                            "role": "user",
                            "content": content_blocks
                        }],
                        "inferenceConfig": {
                            "maxTokens": kwargs.get('max_tokens', 2000),
                            "temperature": kwargs.get('temperature', 0.0),
                            "topP": kwargs.get('top_p', 0.9)
                        }
                    }
                    
                    # Add system prompt if present in kwargs
                    system_prompt = kwargs.get('system_prompt')
                    if system_prompt:
                        request_params["system"] = [{"text": system_prompt}]
                    
                    try:
                        response = self.bedrock_client.converse(**request_params)
                        result = response['output']['message']['content'][0]['text']
                        
                        # Return in DSPy expected format
                        return {"choices": [{"message": {"content": result}}]}
                    except Exception as e:
                        logger.error(f"❌ Bedrock API error in ImageAwareLM: {e}")
                        # Fall back to base LM
                        return self.base_lm(prompt=prompt, messages=messages, **kwargs)
            finally:
                self._is_processing_image = False
        
        # No image detected, use base LM
        logger.debug("No image detected in prompt, delegating to base LM")
        return self.base_lm(prompt=prompt, messages=messages, **kwargs)
    
    def __getattr__(self, name):
        """Delegate all other attributes to base LM."""
        return getattr(self.base_lm, name)
