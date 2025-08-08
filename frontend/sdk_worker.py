#!/Users/tsanti/Development/Publish/nova-prompt-optimizer/.venv/bin/python3
"""
Nova Prompt Optimizer - SDK Proxy Worker
Uses the installed Nova SDK from .venv
"""

import json
import os
import sys
from pathlib import Path
from pathlib import Path

# Ensure we're in the frontend directory and use the same database
frontend_dir = Path(__file__).parent
os.chdir(frontend_dir)
sys.path.insert(0, str(frontend_dir))

from database import Database

# Import the installed SDK (not from /src)
from amzn_nova_prompt_optimizer.core.input_adapters.prompt_adapter import TextPromptAdapter
from amzn_nova_prompt_optimizer.core.input_adapters.dataset_adapter import JSONDatasetAdapter
from amzn_nova_prompt_optimizer.core.input_adapters.metric_adapter import MetricAdapter
from amzn_nova_prompt_optimizer.core.optimizers import NovaPromptOptimizer
from amzn_nova_prompt_optimizer.core.inference.adapter import BedrockInferenceAdapter
from amzn_nova_prompt_optimizer.core.evaluation import Evaluator

def run_optimization_worker(optimization_id: str):
    """Run optimization using the real Nova SDK"""
    db = Database()
    
    try:
        # 1. Load optimization data
        optimization = db.get_optimization_by_id(optimization_id)
        if not optimization:
            print(f"❌ Optimization {optimization_id} not found")
            return
        
        # Use config from command line arguments
        config = json.loads(sys.argv[2])
        db.add_optimization_log(optimization_id, "info", "🚀 Starting SDK-based optimization")
        
        # 2. Load prompt data from database
        db.add_optimization_log(optimization_id, "debug", f"Looking for prompt ID: {optimization['prompt']}")
        
        prompt_data = db.get_prompt(optimization['prompt'])
        db.add_optimization_log(optimization_id, "debug", f"Prompt data found: {prompt_data is not None}")
        
        if not prompt_data:
            # List available prompts for debugging
            all_prompts = db.get_prompts()
            prompt_ids = [p['id'] for p in all_prompts]
            db.add_optimization_log(optimization_id, "debug", f"Available prompt IDs: {prompt_ids}")
            raise Exception(f"Prompt data not found for ID: {optimization['prompt']}")
        
        # Parse the variables JSON to get system and user prompts
        prompt_variables = json.loads(prompt_data['variables'])
        system_prompt = prompt_variables.get('system_prompt', '')
        user_prompt = prompt_variables.get('user_prompt', 'Analyze: {input}')
        
        # 3. Create prompt adapter using real SDK
        prompt_adapter = TextPromptAdapter()
        if system_prompt:
            prompt_adapter.set_system_prompt(content=system_prompt)
        prompt_adapter.set_user_prompt(content=user_prompt, variables={"input"})
        prompt_adapter.adapt()
        
        db.add_optimization_log(optimization_id, "success", "✅ Prompt adapter created")
        
        # 4. Load dataset from database
        dataset_data = db.get_dataset(optimization['dataset'])
        if not dataset_data:
            raise Exception("Dataset not found")
        
        dataset_content = dataset_data['content']
        db.add_optimization_log(optimization_id, "debug", f"Dataset content length: {len(dataset_content)}")
        db.add_optimization_log(optimization_id, "debug", f"Dataset content preview: {dataset_content[:200]}...")
        
        # Write dataset to temp file for SDK
        temp_dataset_path = f"temp_dataset_{optimization_id}.jsonl"
        with open(temp_dataset_path, 'w') as f:
            f.write(dataset_content)
        
        db.add_optimization_log(optimization_id, "debug", f"Created temp file: {temp_dataset_path}")
        
        # Verify file exists and has content
        import os
        if not os.path.exists(temp_dataset_path):
            raise Exception(f"Temp dataset file not created: {temp_dataset_path}")
        
        file_size = os.path.getsize(temp_dataset_path)
        db.add_optimization_log(optimization_id, "debug", f"Temp file size: {file_size} bytes")
        
        # Smart field detection - find the output field automatically
        output_field = None
        if dataset_content.strip():
            try:
                # Parse first line to detect fields
                first_line = dataset_content.strip().split('\n')[0]
                sample_record = json.loads(first_line)
                
                # Common output field names in order of preference
                possible_output_fields = ['answer', 'output', 'response', 'result', 'label', 'target', 'ground_truth']
                
                for field in possible_output_fields:
                    if field in sample_record:
                        output_field = field
                        break
                
                # If none found, use the second field (assuming first is input)
                if not output_field:
                    fields = list(sample_record.keys())
                    if len(fields) >= 2:
                        output_field = fields[1]  # Second field as output
                
                db.add_optimization_log(optimization_id, "info", f"🔍 Detected output field: '{output_field}'")
                
            except Exception as e:
                db.add_optimization_log(optimization_id, "warning", f"⚠️ Could not detect output field: {e}")
                output_field = "answer"  # Default fallback
        
        if not output_field:
            output_field = "answer"  # Final fallback
        
        # Create dataset adapter with detected fields
        dataset_adapter = JSONDatasetAdapter({"input"}, {output_field})
        
        try:
            dataset_adapter.adapt(data_source=temp_dataset_path)
            db.add_optimization_log(optimization_id, "debug", f"Dataset adapted successfully: {len(dataset_adapter.standardized_dataset)} samples")
        except Exception as e:
            db.add_optimization_log(optimization_id, "error", f"Dataset adapt failed: {e}")
            raise Exception(f"Dataset adaptation failed: {e}")
            
        train_dataset, test_dataset = dataset_adapter.split(0.8)  # Use 80% for training with small datasets
        
        db.add_optimization_log(optimization_id, "debug", f"Train dataset size: {len(train_dataset.standardized_dataset) if hasattr(train_dataset, 'standardized_dataset') else 'unknown'}")
        db.add_optimization_log(optimization_id, "debug", f"Test dataset size: {len(test_dataset.standardized_dataset) if hasattr(test_dataset, 'standardized_dataset') else 'unknown'}")
        
        if not hasattr(train_dataset, 'standardized_dataset') or len(train_dataset.standardized_dataset) == 0:
            db.add_optimization_log(optimization_id, "error", f"❌ Training dataset is empty. Original dataset size: {len(dataset_adapter.standardized_dataset) if hasattr(dataset_adapter, 'standardized_dataset') else 'unknown'}")
            db.add_optimization_log(optimization_id, "error", f"❌ Dataset content was: {dataset_content[:500]}...")
            raise Exception("Training dataset is empty after split")
        
        # Ensure minimum dataset size for MIPROv2
        if len(train_dataset.standardized_dataset) < 2:
            db.add_optimization_log(optimization_id, "error", f"❌ Training dataset too small: {len(train_dataset.standardized_dataset)} samples. Need at least 2.")
            raise Exception(f"Training dataset too small: {len(train_dataset.standardized_dataset)} samples. MIPROv2 needs at least 2 training samples.")
        
        db.add_optimization_log(optimization_id, "success", f"✅ Dataset loaded: {len(dataset_adapter.standardized_dataset)} samples")
        
        # 5. Create metric adapter that returns float (like notebook)
        class AnalyzerMetric(MetricAdapter):
            def apply(self, y_pred, y_true):
                try:
                    import json
                    import re
                    
                    # Parse JSON from prediction
                    json_match = re.search(r'\{.*\}', str(y_pred), re.DOTALL)
                    if not json_match:
                        return 0.0
                    
                    pred_json = json.loads(json_match.group())
                    true_json = json.loads(y_true) if isinstance(y_true, str) else y_true
                    
                    score = 0.0
                    total = 0
                    
                    for field in ['urgency', 'sentiment', 'categories']:
                        if field in true_json:
                            total += 1
                            if field in pred_json and pred_json[field] == true_json[field]:
                                score += 1.0
                    
                    return score / total if total > 0 else 0.0
                except:
                    return 0.0
            
            def batch_apply(self, y_preds, y_trues):
                pass  # Not needed for Nova SDK
        
        metric_adapter = AnalyzerMetric()
        
        # 6. Create inference adapter with prompt capturing
        inference_adapter = BedrockInferenceAdapter(region_name="us-east-1", rate_limit=config.get('rate_limit', 2))
        
        # Wrap to capture prompts during optimization
        class PromptCapturingAdapter:
            def __init__(self, base_adapter, optimization_id, db):
                self.base_adapter = base_adapter
                self.optimization_id = optimization_id
                self.db = db
                self.trial_count = 0
                
            def call_model(self, model_id, system_prompt, messages, inf_config):
                self.trial_count += 1
                
                # Store the actual prompts being tested
                system_preview = system_prompt[:300] + "..." if len(system_prompt) > 300 else system_prompt
                user_msg = str(messages[-1]) if messages else "No message"
                user_preview = user_msg[:200] + "..." if len(user_msg) > 200 else user_msg
                
                self.db.add_prompt_candidate(self.optimization_id, f"Trial_{self.trial_count}_SYSTEM", system_preview, None)
                self.db.add_prompt_candidate(self.optimization_id, f"Trial_{self.trial_count}_USER", user_preview, None)
                
                return self.base_adapter.call_model(model_id, system_prompt, messages, inf_config)
            
            def __getattr__(self, name):
                return getattr(self.base_adapter, name)
        
        capturing_adapter = PromptCapturingAdapter(inference_adapter, optimization_id, db)
        
        db.add_optimization_log(optimization_id, "success", "✅ All adapters created")
        
        # 7. Run optimization using real SDK
        db.update_optimization_status(optimization_id, "Running", 50)
        
        nova_optimizer = NovaPromptOptimizer(
            prompt_adapter=prompt_adapter,
            inference_adapter=capturing_adapter,
            dataset_adapter=train_dataset,
            metric_adapter=metric_adapter
        )
        
        model_mode = config.get('model_mode', 'lite')
        db.add_optimization_log(optimization_id, "info", f"🔄 Running optimization with mode: {model_mode}")
        
        optimized_prompt_adapter = nova_optimizer.optimize(mode=model_mode)
        
        db.add_optimization_log(optimization_id, "success", "✅ Optimization completed!")
        
        # 8. Evaluate results using real SDK
        db.update_optimization_status(optimization_id, "Running", 80)
        
        # Baseline evaluation
        baseline_evaluator = Evaluator(prompt_adapter, test_dataset, metric_adapter, inference_adapter)
        baseline_score = baseline_evaluator.aggregate_score(model_id=f"us.amazon.nova-{model_mode}-v1:0")
        
        # Optimized evaluation  
        optimized_evaluator = Evaluator(optimized_prompt_adapter, test_dataset, metric_adapter, inference_adapter)
        optimized_score = optimized_evaluator.aggregate_score(model_id=f"us.amazon.nova-{model_mode}-v1:0")
        
        # Calculate improvement
        # Handle None scores with defaults
        baseline_score = baseline_score if baseline_score is not None else 0.0
        optimized_score = optimized_score if optimized_score is not None else 0.0
        
        # Log the scores for debugging
        db.add_optimization_log(optimization_id, "debug", f"Scores - Baseline: {baseline_score}, Optimized: {optimized_score}")
        
        improvement = ((optimized_score - baseline_score) / baseline_score * 100) if baseline_score > 0 else 0
        
        db.add_optimization_log(optimization_id, "success", f"📈 Results: Baseline: {baseline_score:.3f}, Optimized: {optimized_score:.3f}, Improvement: {improvement:.1f}%")
        
        # 9. Extract optimized prompts using correct attributes (like notebook)
        try:
            # Access prompts directly like in notebook
            optimized_system = optimized_prompt_adapter.system_prompt
            optimized_user = optimized_prompt_adapter.user_prompt
            few_shot_count = len(optimized_prompt_adapter.few_shot_examples)
            
            db.add_optimization_log(optimization_id, "info", f"🔍 Extracted: System={bool(optimized_system)}, User={bool(optimized_user)}, Few-shot={few_shot_count}")
            
            # Only store the FINAL optimized prompts (not SDK internal prompts)
            if optimized_system and optimized_system != system_prompt:
                db.add_prompt_candidate(optimization_id, "FINAL_SYSTEM", optimized_system[:500], optimized_score)
            else:
                db.add_prompt_candidate(optimization_id, "FINAL_SYSTEM", "No system prompt optimization", optimized_score)
                
            if optimized_user and optimized_user != user_prompt:
                db.add_prompt_candidate(optimization_id, "FINAL_USER", optimized_user[:300], optimized_score)
            else:
                db.add_prompt_candidate(optimization_id, "FINAL_USER", "No user prompt optimization", optimized_score)
            
            # Store baseline for comparison
            db.add_prompt_candidate(optimization_id, "BASELINE_SYSTEM", system_prompt[:500], baseline_score)
            db.add_prompt_candidate(optimization_id, "BASELINE_USER", user_prompt[:300], baseline_score)
            
            # Store few-shot examples info
            db.add_prompt_candidate(optimization_id, "FEW_SHOT_COUNT", str(few_shot_count), optimized_score)
            if few_shot_count > 0:
                first_example = str(optimized_prompt_adapter.few_shot_examples[0])[:500]
                db.add_prompt_candidate(optimization_id, "FEW_SHOT_SAMPLE", first_example, optimized_score)
            
        except Exception as e:
            db.add_optimization_log(optimization_id, "error", f"❌ Could not extract prompts: {e}")
            # Store originals as fallback
            db.add_prompt_candidate(optimization_id, "FINAL_SYSTEM", system_prompt[:500], optimized_score)
            db.add_prompt_candidate(optimization_id, "FINAL_USER", user_prompt[:300], optimized_score)
            db.add_prompt_candidate(optimization_id, "BASELINE_SYSTEM", system_prompt[:500], baseline_score)
            db.add_prompt_candidate(optimization_id, "BASELINE_USER", user_prompt[:300], baseline_score)
        
        # 10. Save results
        db.update_optimization_status(optimization_id, "Completed", 100)
        
        # Update the optimization record with results
        cursor = db.conn.cursor()
        cursor.execute("""
            UPDATE optimizations 
            SET improvement = ?, status = 'Completed', completed = datetime('now')
            WHERE id = ?
        """, (f"{improvement:.1f}%", optimization_id))
        db.conn.commit()
        
        # Cleanup
        if os.path.exists(temp_dataset_path):
            os.remove(temp_dataset_path)
        
        print(f"✅ Optimization {optimization_id} completed successfully!")
        
    except Exception as e:
        db.add_optimization_log(optimization_id, "error", f"❌ Optimization failed: {str(e)}")
        db.update_optimization_status(optimization_id, "Failed", 0)
        print(f"❌ Optimization {optimization_id} failed: {e}")
        raise

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python sdk_worker.py <optimization_id> <config_json>")
        sys.exit(1)
    
    optimization_id = sys.argv[1]
    run_optimization_worker(optimization_id)
