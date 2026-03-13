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
from typing import Dict, Any, Optional

from amzn_nova_prompt_optimizer.core.inference import InferenceAdapter
from amzn_nova_prompt_optimizer.core.input_adapters.dataset_adapter import DatasetAdapter
from amzn_nova_prompt_optimizer.core.input_adapters.metric_adapter import MetricAdapter
from amzn_nova_prompt_optimizer.core.input_adapters.prompt_adapter import PromptAdapter
from amzn_nova_prompt_optimizer.core.optimizers import NovaMPOptimizationAdapter
from amzn_nova_prompt_optimizer.core.optimizers.adapter import OptimizationAdapter
from amzn_nova_prompt_optimizer.core.optimizers.miprov2.miprov2_optimizer import NovaMIPROv2OptimizationAdapter

logger = logging.getLogger(__name__)

NOVA_PROMPT_OPTIMIZER_MODE: Dict[str, Dict[str, Any]] = {
    "micro": {
        "meta_prompt_model_id": "us.amazon.nova-2-lite-v1:0",
        "prompter_model_id": "us.amazon.nova-2-lite-v1:0",
        "task_model_id": "us.amazon.nova-micro-v1:0",
        "num_candidates": 20,
        "num_trials": 30,
        "max_bootstrapped_demos": 4,
        "max_labeled_demos": 4
    },
    "lite": {
        "meta_prompt_model_id": "us.amazon.nova-2-lite-v1:0",
        "prompter_model_id": "us.amazon.nova-2-lite-v1:0",
        "task_model_id": "us.amazon.nova-lite-v1:0",
        "num_candidates": 20,
        "num_trials": 30,
        "max_bootstrapped_demos": 4,
        "max_labeled_demos": 4
    },
    "pro": {
        "meta_prompt_model_id": "us.amazon.nova-2-lite-v1:0",
        "prompter_model_id": "us.amazon.nova-2-lite-v1:0",
        "task_model_id": "us.amazon.nova-pro-v1:0",
        "num_candidates": 20,
        "num_trials": 30,
        "max_bootstrapped_demos": 4,
        "max_labeled_demos": 4
    },
    "lite-2": {
        "meta_prompt_model_id": "us.amazon.nova-2-lite-v1:0",
        "prompter_model_id": "us.amazon.nova-2-lite-v1:0",
        "task_model_id": "us.amazon.nova-2-lite-v1:0",
        "num_candidates": 20,
        "num_trials": 30,
        "max_bootstrapped_demos": 4,
        "max_labeled_demos": 4
    }
}


class NovaPromptOptimizer(OptimizationAdapter):
    """
    NovaPromptOptimizer is a combination of Meta Prompting and MIPROv2 for Nova Models that yields a stable
    prompt optimization result.
    
    This optimizer supports using separate inference adapters for:
    - Meta-prompting phase (generating optimized prompts)
    - Task model optimization phase (evaluating prompts on the target model)
    
    This allows you to use Bedrock for meta-prompting while optimizing a SageMaker endpoint.
    """
    def __init__(self, 
                 prompt_adapter: PromptAdapter,
                 inference_adapter: InferenceAdapter,
                 dataset_adapter: DatasetAdapter,
                 metric_adapter: MetricAdapter,
                 meta_prompt_inference_adapter: Optional[InferenceAdapter] = None):
        """
        Initialize NovaPromptOptimizer.
        
        Args:
            prompt_adapter: Adapter for managing prompts
            inference_adapter: Adapter for task model inference (used in MIPROv2 optimization)
            dataset_adapter: Adapter for dataset management
            metric_adapter: Adapter for evaluation metrics
            meta_prompt_inference_adapter: Optional separate adapter for meta-prompting phase.
                If not provided, creates a default BedrockInferenceAdapter with Nova 2.0 Lite
                for meta-prompting, while using inference_adapter for task optimization.
                This allows using Bedrock for meta-prompting while optimizing a SageMaker endpoint.
        """
        # Call parent class's __init__
        super().__init__(prompt_adapter, inference_adapter, dataset_adapter, metric_adapter)
        self.prompt_adapter = prompt_adapter
        self.inference_adapter = inference_adapter
        self.dataset_adapter = dataset_adapter
        self.metric_adapter = metric_adapter
        
        # Use separate adapter for meta-prompting if provided, otherwise create default Bedrock adapter
        if meta_prompt_inference_adapter is not None:
            self.meta_prompt_inference_adapter = meta_prompt_inference_adapter
        else:
            # Import here to avoid circular dependency
            from amzn_nova_prompt_optimizer.core.inference import BedrockInferenceAdapter
            
            # Create default Bedrock adapter for meta-prompting with Nova 2.0 Lite
            logger.info(
                "No meta_prompt_inference_adapter provided. "
                "Creating default BedrockInferenceAdapter with Nova 2.0 Lite for meta-prompting."
            )
            self.meta_prompt_inference_adapter = BedrockInferenceAdapter(
                region_name=getattr(inference_adapter, 'region', 'us-east-1'),
                rate_limit=5
            )
        
        self.meta_prompt_optimization_adapter = NovaMPOptimizationAdapter(
            prompt_adapter, 
            self.meta_prompt_inference_adapter
        )

    def optimize(self, mode: str = "pro", custom_params = None) -> PromptAdapter:
        """
        Optimize the prompt using Nova Meta Prompter followed by MIPROv2.
        
        Args:
            mode: Optimization mode ('micro', 'lite', 'pro', 'lite-2', or 'custom')
            custom_params: Custom parameters for 'custom' mode
            
        Returns:
            Optimized PromptAdapter
        """
        if mode == "custom":
            if not custom_params:
                raise ValueError("Custom mode requires custom_params dictionary")
            required_keys = {"task_model_id", "num_candidates", "num_trials",
                             "max_bootstrapped_demos", "max_labeled_demos"}
            if not all(key in custom_params for key in required_keys):
                raise ValueError(f"custom_params must contain all required keys: {required_keys}")
            meta_prompt_model_id = custom_params.pop("meta_prompt_model_id", None)
            optimization_params = custom_params
        else:
            if mode not in NOVA_PROMPT_OPTIMIZER_MODE:
                logger.warning(f"Mode '{mode}' not detected, defaulting to 'pro' mode")
                mode = "pro"
            config = NOVA_PROMPT_OPTIMIZER_MODE[mode].copy()  # Create a copy to avoid modifying the original
            meta_prompt_model_id = config.pop("meta_prompt_model_id")
            optimization_params = config

        if not self.inference_adapter:
            raise ValueError("Inference Adapter not passed. "
                             "Initialize and Pass Inference Adapter to use this Optimizer")
        
        # Log which adapters are being used
        if self.meta_prompt_inference_adapter is not self.inference_adapter:
            logger.info(
                f"Using separate inference adapters: "
                f"Meta-prompting with {type(self.meta_prompt_inference_adapter).__name__}, "
                f"Task optimization with {type(self.inference_adapter).__name__}"
            )
        
        # Phase 1: Meta-prompting (uses meta_prompt_inference_adapter)
        if meta_prompt_model_id:
            intermediate_prompt_adapter = (
                self.meta_prompt_optimization_adapter.optimize(prompter_model_id=meta_prompt_model_id))
        else:
            intermediate_prompt_adapter = self.meta_prompt_optimization_adapter.optimize()

        if not self.dataset_adapter or not self.metric_adapter:
            logger.info("[Nova Prompt Optimizer] No Dataset or No metric provided, running only Nova Meta Prompter")
            return intermediate_prompt_adapter

        # Phase 2: MIPROv2 optimization (uses main inference_adapter for task model)
        nova_prompt_optimizer = NovaMIPROv2OptimizationAdapter(
            prompt_adapter=intermediate_prompt_adapter,
            dataset_adapter=self.dataset_adapter,
            metric_adapter=self.metric_adapter,
            inference_adapter=self.inference_adapter)

        optimized_prompt_adapter = nova_prompt_optimizer.optimize(**optimization_params, enable_json_fallback=False)
        return optimized_prompt_adapter
