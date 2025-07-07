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


class BedrockConverseHandler:
    def __init__(self, bedrock_client):
        """
        Bedrock Converse Handler to manage converse API calls to Bedrock given a model_id
        :param bedrock_client: Bedrock Client
        """
        self.client = bedrock_client

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

    @staticmethod
    def _get_messages(user_input):
        formatted_messages = []

        for message in user_input:
            if "user" in message:
                formatted_message = {
                    "role": "user",
                    "content": [{"text": message["user"]}]
                }
                formatted_messages.append(formatted_message)

            if "assistant" in message:
                formatted_message = {
                    "role": "assistant",
                    "content": [{"text": message["assistant"]}]
                }
                formatted_messages.append(formatted_message)

        return formatted_messages


    @staticmethod
    def _get_system_config(system_prompt):
        if system_prompt != "":
            return [{'text': system_prompt}]
        else:
            return None
