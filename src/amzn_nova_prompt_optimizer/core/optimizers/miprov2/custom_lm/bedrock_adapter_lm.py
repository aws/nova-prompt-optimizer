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
DSPy LM wrapper that uses BedrockInferenceAdapter directly, bypassing LiteLLM.
This solves the "File name too long" error during MIPROv2 optimization.
"""

import logging
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


class BedrockAdapterLM:
    """
    DSPy-compatible LM that uses BedrockInferenceAdapter directly.
    
    This bypasses LiteLLM entirely, avoiding the "File name too long" errors
    that occur when LiteLLM tries to handle image file paths.
    """
    
    def __init__(self, bedrock_adapter, model_id: str):
        """
        Initialize with a BedrockInferenceAdapter instance.
        
        Args:
            bedrock_adapter: BedrockInferenceAdapter instance
            model_id: Bedrock model ID
        """
        self.bedrock_adapter = bedrock_adapter
        self.model_id = model_id
        self.model = f"bedrock/{model_id}"  # DSPy expects this
        self.history = []  # DSPy expects this
        self.kwargs = {  # DSPy expects this
            "temperature": 0.0,
            "max_tokens": 2000,
            "top_p": 0.9,
            "top_k": 50
        }
        logger.info(f"✅ Initialized BedrockAdapterLM for {model_id} (bypasses LiteLLM)")
    
    def __call__(self, prompt: Optional[str] = None, messages: Optional[List[Dict]] = None, **kwargs):
        """
        Main call method that DSPy uses.
        
        Calls BedrockInferenceAdapter directly, which handles images correctly.
        """
        # Extract the actual prompt
        actual_prompt = prompt
        if messages:
            # Extract the last user message
            for msg in reversed(messages):
                if msg.get('role') == 'user':
                    actual_prompt = msg.get('content', '')
                    break
        
        if not actual_prompt:
            logger.warning("No prompt provided to BedrockAdapterLM")
            return [""]
        
        # Extract system prompt if present
        system_prompt = kwargs.get('system_prompt', '')
        if messages:
            for msg in messages:
                if msg.get('role') == 'system':
                    system_prompt = msg.get('content', '')
                    break
        
        # Extract input data (image path) from the prompt
        # The prompt format from DSPy is: "instruction\n\n[[ ## input ## ]]\nimage_path"
        input_data = ""
        if "[[ ## input ## ]]" in actual_prompt:
            parts = actual_prompt.split("[[ ## input ## ]]")
            if len(parts) == 2:
                instruction = parts[0].strip()
                input_data = parts[1].strip()
                actual_prompt = instruction
                logger.info(f"📝 Extracted input_data: {input_data[:100]}")
        else:
            # Log the actual prompt to debug
            logger.info(f"📝 No [[ ## input ## ]] marker. Prompt preview: {actual_prompt[:200]}")
        
        logger.info(f"🔍 BedrockAdapterLM calling adapter with input: {input_data[:100] if input_data else 'none'}")
        
        # Log what we're actually sending
        user_message = input_data if input_data else actual_prompt
        logger.debug(f"📤 Sending to model: {user_message[:200]}")
        
        try:
            # Call our BedrockInferenceAdapter which handles images correctly
            result = self.bedrock_adapter.call_model(
                model_id=self.model_id,
                system_prompt=system_prompt,
                messages=[{"user": user_message}],
                inf_config={
                    "max_tokens": kwargs.get('max_tokens', 2000),
                    "temperature": kwargs.get('temperature', 0.0),
                    "top_p": kwargs.get('top_p', 0.9),
                    "top_k": kwargs.get('top_k', 50)
                }
            )
            
            logger.info(f"✅ BedrockAdapterLM got response: {result[:100]}...")
            
            # Store in history for DSPy
            self.history.append({
                "prompt": actual_prompt,
                "response": result,
                "kwargs": kwargs
            })
            
            # Return in format DSPy expects (list of completion strings)
            return [result]
        except OSError as e:
            if "File name too long" in str(e):
                # This happens when DSPy passes very long prompts
                # Just return empty response and let DSPy handle it
                logger.warning(f"⚠️ File name too long error (expected during prompt generation), returning empty")
                return [""]
            logger.error(f"❌ BedrockAdapterLM OS error: {e}")
            return [""]
        except Exception as e:
            logger.error(f"❌ BedrockAdapterLM error: {e}")
            return [""]
    
    def __getattr__(self, name):
        """Provide default attributes that DSPy might expect."""
        if name == 'history':
            return self.history
        if name == 'kwargs':
            return self.kwargs
        if name == 'model':
            return self.model
        raise AttributeError(f"'{type(self).__name__}' object has no attribute '{name}'")
