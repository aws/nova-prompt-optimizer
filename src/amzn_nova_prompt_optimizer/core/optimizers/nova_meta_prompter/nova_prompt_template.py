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
NOVA_PROMPT_TEMPLATE = """
You are tasked with translating the Original Prompt into a well-structured, contextual, and specific system prompt and user prompt that Amazon Nova can use to generate accurate and pertinent responses.

### Instructions for output:

- The output MUST include two sections:
    - <system_prompt> … </system_prompt> — This contains instructions or context intended for the model itself and description of input variables but NO VARIABLES TO BE ADDED.
    - <user_prompt> … </user_prompt> — This contains the prompt or input the user will provide to the model.

- Each prompt MUST fully maintain all sections of the Original Prompt (Task, Context Information, Model Instructions, Any Other Sections, Response Format).

- DO NOT omit or leave out any important section or detail from the Original Prompt.

- Emphasize clarity, structure, and specificity using strong wordings such as MUST and DO NOT to convey rules clearly.

- REMOVE ANY examples or example wording from the Original Prompt.

- DO NOT drop or remove any prompt variables such as [<SYSTEM_PROMPT_VARIABLES>][<USER_PROMPT_VARIABLES>] as they are critical for passing input and MUST BE added to the <user_prompt></user_prompt>

- DO NOT add these variables [<SYSTEM_PROMPT_VARIABLES>][<USER_PROMPT_VARIABLES>] to <system_prompt></system_prompt>

- The output MUST preserve the output format from the Original Prompt exactly.

- The response SHOULD be clear, concise, and structured following the provided prompt template below.

- DO NOT OUTPUT anything other than the output format described here.

### Prompt Template to be used:

Task: {{Task summary}}

Context:

{{Context and content information 1}}

{{Context and content information 2}} ...

Instructions:

{{Other Model Instructions}} ...

Any other section from Original Prompt:

{{Clearly define the details under that section here}}

Response Format:

{{Style and format requirement 1}}

{{Style and format requirement 2}} ...

Your final output MUST be in this exact structure:

<system_prompt>
Task: ...

Context:

...

Instructions:

...

Any other section from Original Prompt:

...

Response Format:

...
</system_prompt>

<user_prompt>
{{User-facing prompt crafted to be clear, concise, specific, and to adhere to the system instructions above, including all required variables [<SYSTEM_PROMPT_VARIABLES>][<USER_PROMPT_VARIABLES>]}}
</user_prompt>


Example Translation:

BAD PROMPT:

Write me a meeting invite to the project team

GOOD PROMPT:

<system_prompt>
**Task:**
Write a meeting invite

**Context Information:**
- The meeting is about project planning.

**Model Instructions:**
- Use formal and professional language.
- Ensure the invite is concise and to the point.

**Response Style**
- The response MUST be in the format of a formal email.
- DO NOT exceed 200 words.

**Output Format**
- Add the output format here
</system_prompt>

<user_prompt>
Plan a meeting for October 16th, from 10 AM to 11 AM in Conference Room B. 
Include an agenda that covers our progress on the project thus far, as well as any upcoming milestones and deadlines.
</user_prompt>

Now provide the best prompt for Nova, given the user provided prompt. Remember the modeling instructions.

Original Prompt:
"""
