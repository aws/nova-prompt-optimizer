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

NOVA_OPTIMA_MODE: Dict[str, Dict[str, Any]] = {
    "micro": {
        "task_model_id": "us.amazon.nova-micro-v1:0",
        "num_candidates": 20,
        "num_trials": 30,
        "max_bootstrapped_demos": 4,
        "max_labeled_demos": 4
    },
    "lite": {
        "task_model_id": "us.amazon.nova-lite-v1:0",
        "num_candidates": 20,
        "num_trials": 30,
        "max_bootstrapped_demos": 4,
        "max_labeled_demos": 4
    },
    "pro": {
        "task_model_id": "us.amazon.nova-pro-v1:0",
        "num_candidates": 20,
        "num_trials": 30,
        "max_bootstrapped_demos": 4,
        "max_labeled_demos": 4
    },
    "premier": {
        "task_model_id": "us.amazon.nova-premier-v1:0",
        "num_candidates": 20,
        "num_trials": 30,
        "max_bootstrapped_demos": 4,
        "max_labeled_demos": 4
    }
}


class NovaPromptOptimizer(OptimizationAdapter):
    """
    NovaOptima is a combination of Meta Prompting and MIPROv2 for Nova Models that yields a stable
    prompt optimization result.
    """

    def __init__(self, prompt_adapter: PromptAdapter,
                 inference_adapter: InferenceAdapter,
                 dataset_adapter: DatasetAdapter,
                 metric_adapter: MetricAdapter):
        # Call parent class's __init__
        super().__init__(prompt_adapter, inference_adapter, dataset_adapter, metric_adapter)
        self.prompt_adapter = prompt_adapter
        self.inference_adapter = inference_adapter
        self.dataset_adapter = dataset_adapter
        self.metric_adapter = metric_adapter
        self.meta_prompt_optimization_adapter = NovaMPOptimizationAdapter(prompt_adapter, inference_adapter)

    def optimize(self, mode: str = "pro", custom_params = None) -> PromptAdapter:
        if not self.inference_adapter:
            raise ValueError("Inference Adapter not passed. "
                             "Initialize and Pass Inference Adapter to use this Optimizer")
        intermediate_prompt_adapter = self.meta_prompt_optimization_adapter.optimize()
        if not self.dataset_adapter or not self.metric_adapter:
            logger.info("[Nova Optima] No Dataset or No metric provided, running only Nova Meta Prompter")
            return intermediate_prompt_adapter

        nova_optima_optimization_adapter = NovaMIPROv2OptimizationAdapter(
            prompt_adapter=intermediate_prompt_adapter,
            dataset_adapter=self.dataset_adapter,
            metric_adapter=self.metric_adapter,
            inference_adapter=self.inference_adapter)

        if mode == "custom":
            if not custom_params:
                raise ValueError("Custom mode requires custom_params dictionary")
            required_keys = {"task_model_id", "num_candidates", "num_trials",
                             "max_bootstrapped_demos", "max_labeled_demos"}
            if not all(key in custom_params for key in required_keys):
                raise ValueError(f"custom_params must contain all required keys: {required_keys}")
            optimization_params = custom_params
        else:
            if mode not in NOVA_OPTIMA_MODE:
                logger.warning(f"Mode '{mode}' not detected, defaulting to 'pro' mode")
                optimization_params = NOVA_OPTIMA_MODE["pro"]
            else:
                optimization_params = NOVA_OPTIMA_MODE[mode]
        optimized_prompt_adapter = nova_optima_optimization_adapter.optimize(**optimization_params,
                                                                             enable_json_fallback=False)
        return optimized_prompt_adapter
