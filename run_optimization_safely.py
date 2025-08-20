#!/usr/bin/env python3
"""
Safe wrapper to run Nova Prompt Optimizer with infinite loop protection
"""

# Apply the fix first
from fix_evaluation_loop import patch_evaluator
patch_evaluator()

# Now run your optimization code
import sys
import os

# Add the src directory to Python path
src_path = os.path.join(os.getcwd(), 'src')
if src_path not in sys.path:
    sys.path.insert(0, src_path)

# Your optimization code here
def run_optimization():
    """Run your optimization with the safety patches applied"""
    
    # Import your optimization modules
    from amzn_nova_prompt_optimizer.core.input_adapters.dataset_adapter import JSONDatasetAdapter
    from amzn_nova_prompt_optimizer.core.input_adapters.prompt_adapter import TextPromptAdapter
    from amzn_nova_prompt_optimizer.core.inference.adapter import BedrockInferenceAdapter
    from amzn_nova_prompt_optimizer.core.optimizers.nova_prompt_optimizer import NovaPromptOptimizer
    
    print("🚀 Starting Nova Prompt Optimizer with safety patches...")
    
    # Add your specific optimization configuration here
    # This is just a template - replace with your actual code
    
    print("✅ Optimization setup complete")
    print("⚠️  The infinite loop issue should now be resolved")
    print("📊 Monitor the logs for 'Processed X/Y samples' messages")

if __name__ == "__main__":
    run_optimization()