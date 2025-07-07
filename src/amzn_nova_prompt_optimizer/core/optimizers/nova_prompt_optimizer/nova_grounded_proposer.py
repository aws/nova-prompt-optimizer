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
import traceback
from dspy.propose.grounded_proposer import GroundedProposer # type: ignore

logger = logging.getLogger(__name__)

NOVA_TIPS = {
    "none": "",

    # Original + Enhanced
    "creative": "Encourage the model to think outside the box and explore novel or unconventional ideas.",
    "simple": "Keep the instruction short, clear, and unambiguous. Avoid unnecessary complexity or jargon.",
    "description": "Include detailed and informative context to guide the model toward a more accurate response.",
    "high_stakes": "Frame the task with high-consequence scenarios where accuracy and precision are critical.",
    "persona": 'Assign a relevant persona (e.g., "You are a legal advisor...") to anchor the model’s tone and expertise.',

    # New/Extended TIPS
    "format_control": "Explicitly define the required output format (e.g., JSON, bullet points, Markdown) and enforce strict formatting rules.",
    "structured_prompt": "Use structured prompt sections like ## Task, ## Context, and ## Instructions to improve comprehension.",
    "examples": "Provide both positive and negative examples to illustrate what a good or bad response looks like.",
    "rules_based": "State rules or compliance constraints (e.g., GDPR, company policy) that the model MUST follow.",
    "multi_turn": "Guide the model to ask clarifying questions if the task is ambiguous or requires multiple steps."
}

class NovaGroundedProposer(GroundedProposer):
    """Enhanced version of DSPy's GroundedProposer with support for Nova Tips"""
    def __init__(self, *args, **kwargs):
        logger.info("Initializing NovaGroundedProposer")
        super().__init__(*args, **kwargs)
        self.TIPS = NOVA_TIPS

    def propose_instructions_for_program(
            self, trainset, program, demo_candidates, trial_logs, N, T
    ):
        proposed_instructions = {}

        if self.set_history_randomly:
            use_history = self.rng.random() < 0.5
            self.use_instruct_history = use_history
            if self.verbose:
                print(f"Use history T/F: {self.use_instruct_history}")

        if not demo_candidates:
            self.use_task_demos = False
            num_demos = N
        else:
            num_demos = max(len(demo_candidates[0]), 1)

        for pred_i, predictor in enumerate(program.predictors()):
            for demo_set_i in range(min(N, num_demos)):
                if pred_i not in proposed_instructions:
                    proposed_instructions[pred_i] = []

                selected_tip = None
                if self.set_tip_randomly:
                    selected_tip_key = self.rng.choice(list(self.TIPS.keys()))  #  use Nova Tips
                    selected_tip = self.TIPS[selected_tip_key]
                    self.use_tip = bool(selected_tip)
                    print(f"[Nova] Selected tip: {selected_tip_key}")

                proposed_instructions[pred_i].append(
                    self.propose_instruction_for_predictor(
                        program=program,
                        predictor=predictor,
                        pred_i=pred_i,
                        T=T,
                        demo_candidates=demo_candidates,
                        demo_set_i=demo_set_i,
                        trial_logs=trial_logs,
                        tip=selected_tip,
                    )
                )

        return proposed_instructions
